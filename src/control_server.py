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

from dataclasses import dataclass
from select import select

import communication.thingspeak as thingspeak
import communication.transport as transport
import communication.message as message
from database_code import DataBase

VERBOSE = True

# If your address is in this list, I will treat you as an entrance
#entrance_addresses = ["Entrance A", "Entrance B", "Entrance C","Entrance D"]

# If your address is in this list, I will treat you as an exit
#exit_addresses = ["Exit A", "Exit B", "Exit C", "Exit D"]

@dataclass
class Client:
    connection: transport.Connection
    address: str
    entrance: bool
    node_id: int 

class ControlServer:
    clients = [] # List of Client objects
    def __init__(self):
        self.database = DataBase()
        # Get API keys from file
        try:
            with open("api_write_key.txt", "r") as keyfile:
                write_key = keyfile.read().strip()
            with open("api_read_key.txt", "r") as keyfile:
                read_key = keyfile.read().strip()
            # Connecting to project database
            self.database = sqlite3.connect('project.db')
            self.cursor = self.database.cursor()
        except FileNotFoundError:
            raise Exception("Could not open keyfiles.")
        except ConnectionNotMadeError:
            print("Error while working with SQLite", error)
        self.channel = thingspeak.Channel(1222699, write_key=write_key, read_key=read_key)
        self.server = transport.Server(self.channel, "control_server")
        self.safe_temperature_range = (30, 37.5)
        self.maximum_occupancy = 50
        self.current_occupancy = 0

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
                    self._new_message(client, received_message,node_id)

    def _new_client(self, connection, address):
        if VERBOSE:
            print(f"New connection from \"{address}\".\n")
        self.cursor.execute("SELECT node_id, node_type FROM node_info WHERE address = ?", (address,))
        node_id,node_type = self.cursor.fetchone()
        if node_type == 'entry':
            entrance = True
        elif node_type == 'exit':
            entrance = False
        else:
            raise Exception("A stranger tried to connect!")

        self.clients.append(Client(connection, address, entrance, node_id))

        # Send door state update
        new_state = message.DoorState.ALLOWING_ENTRY
        resp = message.DoorStateUpdateMessage(new_state)
        if VERBOSE:
            print(f"Sending door state update ({resp}) to {address}")
        connection.send(resp.to_bytes())

    def _new_message(self, client, received_message,node_id):
        #if entry request
        if client.entrance:
            # When we receive an access request, ask for their temperature
            if received_message is message.AccessRequestMessage:
                #if building can take entries
                if self.current_occupancy <= self.maximum_occupancy:
                    #retrieve employee_info here based off of the nfc_badge_id received from the access request message
                    #sending badge id so that information can be retrieved from db
                    employee_id,accessDate,status,validity = self.entry_queries(received_message.badge_id)
                    #invalid employee ID
                    if employee_id == 0 or status == 'unauthorized' or validity > 3:
                        resp = message.AccessResponseMessage(received_message.transaction_id, False)
                    #valid employee ID
                    else:
                        resp = message.InformationRequestMessage(
                            received_message.transaction_id, message.InformationType.USER_TEMPERATURE)
                #if building at maximum occupancy and cannot take entries
                else:
                    resp = message.AccessResponseMessage(received_message.transaction_id, False)

            # When we receive their temperature let them in if it is within
            # range. Else ask for it again. TODO: limit the number of tries
            elif received_message  is message.InformationResponseMessage:
                employee_id,accessDate,status,validity = self.entry_queries(received_message.badge_id)
                #invalid employee ID
                if employee_id == 0:
                    resp = message.AccessResponseMessage(received_message.transaction_id, False)
                else:
                    #if less than 3 entry attempts
                    if validity <= 3:
                        if received_message.information_type != message.InformationType.USER_TEMPERATURE:
                            raise Exception("This is not the information I requested!")
                        if(self.safe_temperature_range[0] < received_message.payload.user_temp
                           < self.safe_temperature_range[1]):
                            #set validity field to 0 because access is authorized which means no more tries to limit
                            validity = 0
                            resp = message.AccessResponseMessage(received_message.transaction_id, True)
                            #save tranasaction information
                            self.save_access(employee_id, 'entry', node_id,'Y',received_message.payload.user_temp,'authorized',validity,received_message.transaction_id)
                            self.current_occupancy = self.current_occupancy + 1
                        else:
                            #incrementing validity to keep track of number of attempts made
                            validity = validity+1
                            #if entry attempt is still less than 3
                            if validity <= 3:
                                #saving info for invalid entry attempt
                                self.save_access(employee_id,'entry',node_id,'Y',received_message.payload.user_temp,'undetermined',validity,received_message.transaction_id)
                                #requesting information again
                                resp = message.InformationRequestMessage(
                                    received_message.transaction_id, message.InformationType.USER_TEMPERATURE)
                            #if 3rd entry attempt
                            else:
                                resp = message.AccessResponseMessage(received_message.transaction_id, False)
                                self.save_access(employee_id,'entry',node_id,'Y',received_message.payload.user_temp,'unauthorized',validity,received_message.transaction_id)
                                print ("Access entry status: unathorized")
                    #if more than 3 entry attempts
                    else:
                        resp = message.AccessResponseMessage(received_message.transaction_id, False)
                        self.save_access(employee_id, 'entry',node_id,'Y',received_message.payload.user_temp,'unauthorized',validity,received_message.transaction_id)
                        print ("Access entry status: unauthorized")
            else:
                raise Exception("I don't like these types of messages")
            
        #if exit request
        else:
            employee_id = self.exit_queries(received_message.badge_id)
            #invalid employee ID
            if employee_id == 0:
                resp = message.AccessResponseMessage(received_message.transaction_id, False)
            #valid employee ID
            else:
                resp = message.AccessResponseMessage(received_message.transaction_id, True)
                self.save_access(employee_id,'exit',node_id,'N/A',0,'authorized',0,received_message.transaction_id)
                self.current_occupancy = self.current_occupancy - 1

        client.connection.send(resp.to_bytes())

    def entry_queries(self,badge_id):
        self.cursor.execute("SELECT employee_id FROM nfc_and_employee_id WHERE nfc_id =?",(self.badge_id,) )
        employeeId = self.cursor.fetchone()[0]
        if (employeeId == None):
            employeeId = 0
            return employeeId,'none','none',0
        #if employee_id exists in the system then retrieve info of most latest access_type
        self.cursor.execute("SELECT access_datetime FROM access_summary WHERE employee_id = ? ORDER BY employee_id DESC LIMIT 1", (employeeId,))
        accessDate = self.cursor.fetchone()
        self.cursor.execute("SELECT status FROM access_summary WHERE employee_id = ? ORDER BY employee_id DESC LIMIT 1", (employeeId,))
        statusType = self.cursor.fetchone()
        self.cursor.execute("SELECT validity FROM access_summary WHERE employee_id = ? ORDER BY employee_id DESC LIMIT 1", (employeeId,))
        validity = self.cursor.fetchone()
        return employeeId,accessDate,statusType,validity
    
    def exit_queries(self, badge_id):
        self.cursor.execute("SELECT employee_id FROM nfc_and_employee_id WHERE nfc_id =?",(self.badge_id,) )
        employeeId = self.cursor.fetchone()[0]
        if (employeeId == None):
            employeeId = 0
            return employeeId
        return employeeId

    def save_access(self,employeeId,access_type,access_node,in_range,temp_reading,status,validity,t_ID):
        #access_summary(transaction_id INTEGER NOT NULL, employee_id INTEGER NOT NULL, access_type TEXT NOT NULL, access_datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
        #access_node TEXT NOT NULL, temp_reading NUMERIC NOT NULL, status TEXT NOT NULL,validity INTEGER NOT NULL)
        data_tuple = (t_ID,employeeId,access_type,access_node,in_range,temp_reading,status,validity)
        self.cursor.execute("INSERT INTO access_summary(transaction_id,employee_id,access_type,access_node,in_range,temp_reading,status,validity) VALUES (?,?,?,?,?,?)",data_tuple)


if __name__ == "__main__":
    server = ControlServer()
    server.main_loop()
