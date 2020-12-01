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
#
# TODO:
# - occupancy limits - done
# - database interaction - done
# - change _new_client to add database queries for node id and node type - done
# - add object to clients - done 
#   - add a node_id object of int type (client.node_id) - done
#add exception if status is unauthorized - done

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
class Client:
    connection: transport.Connection
    address: str
    entrance: bool
    node_id: int

@dataclass
class Transaction:
    client: Client
    tid: int
    temperature_attempts: int

class ControlServer:
    clients = [] # List of Client objects
    transactions = [] # List of Transaction objects
    def __init__(self):
        # Get API keys from file
        try:
            with open("api_write_key.txt", "r") as keyfile:
                write_key = keyfile.read().strip()
            with open("api_read_key.txt", "r") as keyfile:
                read_key = keyfile.read().strip()
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
        except FileNotFoundError:
            raise Exception("Could not open keyfiles.")
        except ConnectionNotMadeError:
            print("Error while working with SQLite", error)
        self.channel = thingspeak.Channel(1222699, write_key=write_key, read_key=read_key)
        self.server = transport.Server(self.channel, "control_server")
        self.safe_temperature_range = (30, 37.5)
        self.maximum_occupancy = 50
        self.current_occupancy = 0
        self.max_temperature_attempts = 3

    def main_loop(self):
        while True:
            new_messages, _, _ = \
                select([i.connection for i in self.clients] + [self.server], [], [])

            for connection in new_messages:
                if connection is self.server:
                    connection, address = self.server.accept(block=False)
                    self._new_client(connection, address)
                else:
                    data = connection.recv(block=False)
                    received_message = message.Message.from_bytes(data)
                    if VERBOSE:
                        print(f"Received ({received_message}) from \"{connection.peer_address}\"")
                    client = next((x for x in self.clients if x.connection == connection), None)
                    self._new_message(client, received_message)

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
            print(f"Sending door state update ({resp}) to {address}")
        connection.send(resp.to_bytes())

    def _new_message(self, client, received_message):

        #if exit request
        if not client.entrance:
            employee_id = self.exit_queries(received_message.badge_id)
            #invalid employee ID
            if employee_id == 0:
                resp = message.AccessResponseMessage(received_message.transaction_id, False)
            #valid employee ID
            else:
                resp = message.AccessResponseMessage(received_message.transaction_id, True)
                self.save_access(employee_id,'exit',client.node_id,'N/A',0,'authorized',0,received_message.transaction_id)
                self.current_occupancy = self.current_occupancy - 1

            client.connection.send(resp.to_bytes())
            return

        # Entry request
        transaction = next((x for x in self.transactions if x.tid == received_message.transaction_id),
                           None)

        if transaction is None:
            transaction = Transaction(client, received_message.transaction_id, 0)
            self.transactions.append(transaction)

        # When we receive an access request, ask for their temperature
        if isinstance(received_message, message.AccessRequestMessage):
            #if building can take entries
            if self.current_occupancy < self.maximum_occupancy:
                #retrieve employee_info here based off of the nfc_badge_id received from the access request message
                #sending badge id so that information can be retrieved from db
                employee_id,accessDate,status = self.entry_queries(received_message.badge_id)
                #invalid employee ID
                if employee_id == 0 or status == 'unauthorized' or transaction.temperature_attempts >= self.max_temperature_attempts:
                    resp = message.AccessResponseMessage(received_message.transaction_id, False)
                #valid employee ID
                else:
                    resp = message.InformationRequestMessage(
                        received_message.transaction_id, message.InformationType.USER_TEMPERATURE)
            #if building at maximum occupancy and cannot take entries
            else:
                resp = message.AccessResponseMessage(received_message.transaction_id, False)

        # When we receive their temperature let them in if it is within
        # range. Else ask for it again.
        elif isinstance(received_message, message.InformationResponseMessage):
            employee_id,accessDate,status = self.entry_queries(received_message.badge_id)
            #invalid employee ID
            if employee_id == 0:
                resp = message.AccessResponseMessage(received_message.transaction_id, False)
            else:
                #if less than 3 entry attempts
                if transaction.temperature_attempts < self.max_temperature_attempts:
                    if received_message.information_type != message.InformationType.USER_TEMPERATURE:
                        raise Exception("This is not the information I requested!")
                    if(self.safe_temperature_range[0] < received_message.payload.user_temp
                       < self.safe_temperature_range[1]):
                        resp = message.AccessResponseMessage(received_message.transaction_id, True)
                        #save transaction information
                        self.save_access(employee_id, 'entry', client.node_id,'Y',received_message.payload.user_temp,'authorized',received_message.transaction_id)
                        self.current_occupancy = self.current_occupancy + 1
                    else:
                        transaction.temperature_attempts = transaction.temperature_attempts + 1
                        if transaction.temperature_attempts < self.max_temperature_attempts:
                            #saving info for invalid entry attempt
                            self.save_access(employee_id,'entry',client.node_id,'Y',received_message.payload.user_temp,'undetermined',received_message.transaction_id)
                            #requesting information again
                            resp = message.InformationRequestMessage(
                                received_message.transaction_id, message.InformationType.USER_TEMPERATURE)
                        #if 3rd entry attempt
                        else:
                            resp = message.AccessResponseMessage(received_message.transaction_id, False)
                            self.save_access(employee_id,'entry',client.node_id,'Y',received_message.payload.user_temp,'unauthorized',received_message.transaction_id)
                            print ("Access entry status: unauthorized")
                #if more than 3 entry attempts
                else:
                    resp = message.AccessResponseMessage(received_message.transaction_id, False)
                    self.save_access(employee_id, 'entry',client.node_id,'Y',received_message.payload.user_temp,'unauthorized',received_message.transaction_id)
                    print ("Access entry status: unauthorized")
        else:
            raise Exception(f"I don't like these types of messages: {received_message}")

        client.connection.send(resp.to_bytes())

    def entry_queries(self,badge_id):
        self.cursor.execute("SELECT employee_id FROM nfc_and_employee_id WHERE nfc_id =?",(badge_id,) )
        employeeId = self.cursor.fetchone()[0]
        if (employeeId == None):
            employeeId = 0
            return employeeId,'none','none',0
        #if employee_id exists in the system then retrieve info of most latest access_type
        self.cursor.execute("SELECT access_datetime FROM access_summary WHERE employee_id = ? ORDER BY employee_id DESC LIMIT 1", (employeeId,))
        accessDate = self.cursor.fetchone()
        self.cursor.execute("SELECT status FROM access_summary WHERE employee_id = ? ORDER BY employee_id DESC LIMIT 1", (employeeId,))
        statusType = self.cursor.fetchone()
        return employeeId,accessDate,statusType
    
    def exit_queries(self, badge_id):
        self.cursor.execute("SELECT employee_id FROM nfc_and_employee_id WHERE nfc_id =?",(badge_id,) )
        employeeId = self.cursor.fetchone()[0]
        if (employeeId == None):
            employeeId = 0
            return employeeId
        return employeeId

    def save_access(self, employeeId, access_type, access_node, in_range, temp_reading, status,t_ID):
        #access_summary(transaction_id INTEGER NOT NULL, employee_id INTEGER NOT NULL, access_type TEXT NOT NULL, access_datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
        #access_node TEXT NOT NULL, temp_reading NUMERIC NOT NULL, status TEXT NOT NULL)
        data_tuple = (t_ID,employeeId,access_type,access_node,in_range,temp_reading,status)
        self.cursor.execute("INSERT INTO access_summary(transaction_id,employee_id,access_type,access_node,in_range,temp_reading,status) VALUES (?,?,?,?,?)",data_tuple)


if __name__ == "__main__":
    server = ControlServer()
    server.main_loop()
