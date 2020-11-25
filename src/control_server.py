#!/usr/bin/env python3
#
# Copyright (C) 2020 by Morgan Smith
#
# control_server.py
#
# TODO:
# - occupancy limits
# - database interaction

from dataclasses import dataclass
from select import select

import communication.thingspeak as thingspeak
import communication.transport as transport
import communication.message as message
from database_code import DataBase

VERBOSE = True

# If your address is in this list, I will treat you as an entrance
entrance_addresses = ["ENTRANCE"]

# If your address is in this list, I will treat you as an exit
exit_addresses = ["EXIT"]

@dataclass
class Client:
    connection: transport.Connection
    address: str
    entrance: bool

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
        except FileNotFoundError:
            raise Exception("Could not open keyfiles.")
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
                    self._new_message(client, received_message)

    def _new_client(self, connection, address):
        if VERBOSE:
            print(f"New connection from \"{address}\".\n")
        if address in entrance_addresses:
            entrance = True
        elif address in exit_addresses:
            entrance = False
        else:
            raise Exception("A stranger tried to connect!")

        self.clients.append(Client(connection, address, entrance))

        # Send door state update
        new_state = message.DoorState.ALLOWING_ENTRY
        resp = message.DoorStateUpdateMessage(new_state)
        print(f"Sending door state update ({resp}) to {address}")
        connection.send(resp.to_bytes())

    def _new_message(self, client, received_message):
        if client.entrance:
            # When we receive an access request, ask for their temperature
            if received_message is message.AccessRequestMessage:
                resp = message.InformationRequestMessage(
                    received_message.transaction_id, message.InformationType.USER_TEMPERATURE)

            # When we receive their temperature let them in if it is within
            # range. Else ask for it again
            elif received_message  is message.InformationResponseMessage:
                if received_message.information_type != message.InformationType.USER_TEMPERATURE:
                    raise Exception("This is not the information I requested!")
                if(self.safe_temperature_range[0] < received_message.payload.user_temp
                   < self.safe_temperature_range[1]):
                    resp = message.AccessResponseMessage(received_message.transaction_id, True)
                else:
                    resp = message.InformationRequestMessage(
                        received_message.transaction_id, message.InformationType.USER_TEMPERATURE)
            else:
                raise Exception("I don't like these types of messages")
        else:
            resp = message.AccessResponseMessage(received_message.transaction_id, True)

        client.connection.send(resp.to_bytes())

if __name__ == "__main__":
    server = ControlServer()
    server.main_loop()
