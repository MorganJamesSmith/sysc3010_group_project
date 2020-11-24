#!/usr/bin/env python3
#
# Copyright (C) 2020 by Morgan Smith
#
# ControlServer.py
#
# TODO:
# - occupancy limits
# - database interaction

import sys
sys.path.append("./communication")

import select

import thingspeak
import transport
from database_code import DataBase
from message import *

# If your address is in this list, I will treat you as an entrance
entrance_addresses = ["ENTRANCE"]

# If your address is in this list, I will treat you as an exit
exit_addresses = ["EXIT"]

class Client:
    def __init__(self, connection, address, entrance):
        self.connection = connection
        self.address = address
        self.entrance = entrance

class ControlServer:
    safe_temperature_range = (30, 37.5)
    maximum_occupancy = 50
    current_occupancy = 0
    clients = [] # List of Client objects
    def __init__(self):
        self.database = DataBase()
        # Get API keys from file
        try:
            with open("api_write_key.txt", "r") as keyfile:
                write_key = keyfile.read().strip()
            with open("api_read_key.txt", "r") as keyfile:
                read_key = keyfile.read().strip()
        except FileNotFoundError as e:
            print("Could not open keyfiles.")
            exit(1)
        self.channel = thingspeak.Channel(1222699, write_key=write_key, read_key=read_key)
        self.server = transport.Server(self.channel, "control_server")

    def main_loop(self):
        while(True):
            r, _, _ = select.select([i.connection for i in self.clients] + [self.server], [], [])

            for connection in r:
                if connection is self.server:
                    connection, address = self.server.accept(block = False)
                    self._new_client(connection, address)
                else:
                    data = connection.recv(block = False)
                    try:
                        message = Message.from_bytes(data)
                    except:
                        print(f"Received invalid message from \"{connection.peer_address}\"")
                    print(f"Received ({message}) from \"{connection.peer_address}\"")
                    client = next((x for x in self.clients if x.connection == connection), None)
                    self._new_message(client, message)

    def _new_client(self, connection, address):
        print(f"New connection from \"{address}\".\n")
        if address in entrance_addresses:
            entrance = True
        elif address in exit_addresses:
            entrance = False
        else:
            raise Exception("A stranger tried to connect!")

        self.clients.append(Client(connection, address, entrance))

        # Send door state update
        new_state = DoorState.ALLOWING_ENTRY
        resp = DoorStateUpdateMessage(new_state)
        print(f"Sending door state update ({resp}) to {address}")
        connection.send(resp.to_bytes())

    def _new_message(self, client, message):
        if client.entrance:
            # When we receive an access request, ask for their temperature
            if message is AccessRequestMessage:
                resp = InformationRequestMessage(message.transaction_id, InformationType.USER_TEMPERATURE)

            # When we receive their temperature let them in if it is within
            # range. Else ask for it again
            elif message is InformationResponseMessage:
                if message.information_type != InformationType.USER_TEMPERATURE:
                    raise Exception("This is not the information I requested!")
                if safe_temperature_range[0] < message.payload.user_temp < safe_temperature_range[0]:
                    resp = AccessResponseMessage(message.transaction_id, allow)
                else:
                    resp = InformationRequestMessage(message.transaction_id, InformationType.USER_TEMPERATURE)
            else:
                raise Exception("I don't like these types of messages")
        else:
            resp = AccessResponseMessage(message.transaction_id, allow)

        client.connection.send(resp.to_bytes())

if __name__ == "__main__":
    server = ControlServer()
    server.main_loop()
