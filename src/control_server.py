#!/usr/bin/env python3
#
# Copyright (C) 2020 by Morgan Smith
# Copyright (C) 2020 by Sunjeevani Pujari
#
# control_server.py
#
# This file is the control server for our door security system. The server is
# started by running the main loop. The server maintains a list of connected
# clients. The server continuously polls for new messages.
#
# If a client is an exit, then the server will allow the door to open. If the
# client is an entrance, the server will ask for the users body temperature and
# only allow them in if their temperature is within a specified range.

import socket
from queue import Queue
import json
import sqlite3
import time
from datetime import date

import os.path

from dataclasses import dataclass
from select import select

import communication.thingspeak as thingspeak
import communication.transport as transport
import communication.message as message
from db_structure import DataBase

VERBOSE = True

@dataclass
class Settings:
    safe_temperature_range = (30, 37.5)
    maximum_occupancy: int  = 50
    current_occupancy: int = 0

@dataclass
class TCP_Client:
    connection = None
    address = None
    queue = Queue()

@dataclass
class Client:
    connection: transport.Connection
    address: str
    entrance: bool
    node_id: int

@dataclass
class Transaction:
    client: Client
    tid: int
    employee_id: int
    status: str = ''
    temp_reading: int = 99

class ControlServer:
    clients = [] # List of Client objects
    tcp_clients = [] # List of TCP_Client objects
    transactions = [] # List of Transaction objects
    def __init__(self):
        # Get API keys from file
        try:
            with open("api_write_key.txt", "r") as keyfile:
                write_key = keyfile.read().strip()
            with open("api_read_key.txt", "r") as keyfile:
                read_key = keyfile.read().strip()
        except FileNotFoundError:
            raise Exception("Could not open keyfiles.")
        try:
            with open("settings.json", "r") as settingsfile:
                json_string = settingsfile.read().strip()
                self.settings = json_to_settings(json_string)
        except FileNotFoundError:
            print("No settings file")
            self.settings = Settings()

        # Connecting to project database
        if not os.path.isfile('security_system.db'):
            self.database = DataBase()
            self.database_con = sqlite3.connect('security_system.db')
            self.cursor = self.database_con.cursor()
            self.database.creating_db()
        else:
            self.database = DataBase()
            self.database_con = sqlite3.connect('security_system.db')
            self.cursor = self.database_con.cursor()
        self.channel = thingspeak.Channel(1222699, write_key=write_key, read_key=read_key)
        self.server = transport.Server(self.channel, "control_server")

        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.setblocking(0)
        self.tcp_server.bind(('localhost', 8888))
        self.tcp_server.listen(0)



    def main_loop(self):
        while True:
            new_messages, writable, exceptions = \
                select([i.connection for i in self.clients] +
                       [i.connection for i in self.tcp_clients] +
                       [self.server, self.tcp_server],
                       [i.connection for i in self.tcp_clients if not i.queue.empty()],
                       [i.connection for i in self.tcp_clients])

            for connection in new_messages:
                if connection is self.server:
                    connection, address = self.server.accept(block=False)
                    self._new_client(connection, address)
                elif connection is self.tcp_server:
                    connection, address = self.tcp_server.accept()
                    tcp_clients.append(TCP_Client(connection, address))
                elif isinstance(connection, transport.Connection):
                    data = connection.recv(block=False)
                    received_message = message.Message.from_bytes(data)
                    if VERBOSE:
                        print(f"Received ({received_message}) from \"{connection.peer_address}\"")
                    client = next((x for x in self.clients if x.connection == connection), None)
                    self._new_message(client, received_message)
                else: # TCP connections
                    data = connection.recv(1023)
                    client = next((x for x in self.clients if x.connection == connection), None)
                    if data:
                        data = data.decode('UTF-8')
                        if data != "request":
                            self.settings = json_to_settings(data)
                            try:
                                with open("settings.json", "w") as settingsfile:
                                    settingsfile.write(data)
                            except FileNotFoundError:
                                print("Could not write settings")
                        client.queue.enque(setting_to_json(self.settings).encode('UTF-8'))
                    else:
                        self.tcp_clients.remove(client)
                        client.connection.close()

            for write in writable:
                try:
                    client =  next((x for x in self.tcp_clients if x.connection == write), None)
                    msg = client.queue.get_nowait()
                except queue.Empty:
                    pass
                else:
                    write.send(msg)

            for exception in exceptions:
                self.tcp_clients = [i for i in self.tcp_clients if i.connection != exception]
                exception.close()

    def _new_client(self, connection, address):
        if VERBOSE:
            print(f"New connection from \"{address}\".\n")
        self.cursor.execute("SELECT node_id, node_type FROM node_info WHERE address = ?", (address,))
        try:
            node_id, node_type = self.cursor.fetchone()
        except:
            print("A stranger tried to connect!")
            return

        if node_type == 'entry':
            entrance = True
        elif node_type == 'exit':
            entrance = False

        self.clients.append(Client(connection, address, entrance, node_id))

        # Send door state update
        new_state = message.DoorState.ALLOWING_ENTRY
        resp = message.DoorStateUpdateMessage(new_state)
        if VERBOSE:
            print(f"Sending door state update ({resp}) to \"{address}\"")
        connection.send(resp.to_bytes())

    def _new_message(self, client, received_message):

        transaction = next((x for x in self.transactions if x.tid == received_message.transaction_id),
                           None)

        if transaction is None:
            if not isinstance(received_message, message.AccessRequestMessage):
                print(f"Unexpected message received: {received_message}")
                return

            transaction = Transaction(client,
                                      received_message.transaction_id,
                                      self.badge_id_to_employee_id(received_message.badge_id))
            transaction.status = self.employee_id_to_status(transaction.employee_id)
            self.transactions.append(transaction)


        #invalid employee ID
        if transaction.employee_id == 0:
            resp = message.AccessResponseMessage(transaction.tid, False)
            transaction.status = 'unauthorized'

        #if exit request
        elif not client.entrance:
            resp = message.AccessResponseMessage(transaction.tid, True)
            transaction.status = 'authorized'
            self.settings.current_occupancy = self.settings.current_occupancy - 1

        # Entry request
        # When we receive an access request, ask for their temperature
        elif isinstance(received_message, message.AccessRequestMessage):
            #if building can take entries
            if self.settings.current_occupancy < self.settings.maximum_occupancy:
                resp = message.InformationRequestMessage(
                    transaction.tid, message.InformationType.USER_TEMPERATURE)
                transaction.status = 'unauthorized'
            else:
                transaction.status = 'unauthorized'
                resp = message.AccessResponseMessage(transaction.tid, False)

        # When we receive their temperature let them in if it is within
        # range. Else ask for it again.
        elif isinstance(received_message, message.InformationResponseMessage):
            if received_message.information_type != message.InformationType.USER_TEMPERATURE:
                raise Exception("This is not the information I requested!")

            if(self.settings.safe_temperature_range[0] < received_message.payload.user_temp
               < self.settings.safe_temperature_range[1]):
                resp = message.AccessResponseMessage(received_message.transaction_id, True)
                transaction.status = 'authorized'
                self.settings.current_occupancy = self.settings.current_occupancy + 1
            else:
                resp = message.AccessResponseMessage(received_message.transaction_id, False)
        else:
            raise Exception(f"I don't like these types of messages: {received_message}")

        self.save_access(transaction)
        if isinstance(resp, message.AccessResponseMessage):
            self.transactions.remove(transaction)
        if VERBOSE:
            print(f"Sending ({resp}) from \"{transaction.client.connection.peer_address}\"")
        client.connection.send(resp.to_bytes())

    def employee_id_to_status(self, employee_id):
        self.cursor.execute("SELECT status FROM access_summary WHERE employee_id = ? ORDER BY employee_id DESC LIMIT 1", (employee_id,))
        return self.cursor.fetchone()
    
    def badge_id_to_employee_id(self, badge_id):
        self.cursor.execute("SELECT employee_id FROM employee_info WHERE nfc_id =?",(badge_id,) )
        employeeId = self.cursor.fetchone()[0]
        if (employeeId == None):
            employeeId = 0
            return employeeId
        return employeeId

    def setting_to_json(self, settings):
        tmp = {"safe_temperature_range": settings.safe_temperature_range,
               "maximum_occupancy": settings.maximum_occupancy,
               "current_occupancy": settings.current_occupancy}
        return json.dumps(tmp)

    def json_to_settings(self, json_string):
        tmp = json.load(json_string)
        return Settings(tmp["safe_temperature_range"],
                        tmp["maximum_occupancy"],
                        tmp["current_occupancy"])

    def save_access(self, transaction):
        access_type =  'entry' if transaction.client.entrance else 'exit'
        data_tuple = (transaction.tid, transaction.employee_id, access_type, transaction.client.node_id, transaction.temp_reading, transaction.status)
        self.cursor.execute("INSERT INTO access_summary(transaction_id, employee_id, access_type, access_node, temp_reading, status) VALUES (?,?,?,?,?,?)", data_tuple)

if __name__ == "__main__":
    server = ControlServer()
    server.main_loop()
