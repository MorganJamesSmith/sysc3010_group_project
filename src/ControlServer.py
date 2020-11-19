#!/usr/bin/env python3
#
# Copyright (C) 2020 by Morgan Smith
#
# ControlServer.py

import sys
sys.path.append("./communication")

import select

import thingspeak
import transport
from database_code import DataBase


class Client:
    def __init__(self, connection):
        self.connection = connection
        self.address = address

class ControlServer:
    safe_temperature_range = (30, 37.5)
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
        r, _, _ = select.select([i.connection for i in self.clients] + [self.server], [], [])

        for connection in r:
            if connection is server:
                self._new_client(self.server.accept(block = False))
            else:
                data = connection.recv(block = False)
                try:
                    message = Message.from_bytes(data)
                except:
                    print(f"Received invalid message from \"{connection.peer_address}\"")
                print(f"Received ({message}) from \"{connection.peer_address}\"")
                self._new_message(connection, message)

    def _new_client(self, connection, address):
        print(f"New connection from \"{address}\".\n")
        clients.append(Client(connection, address))

        # Send door state update
        new_state = DoorState.ALLOWING_ENTRY
        resp = DoorStateUpdateMessage(new_state)
        print(f"Sending door state update ({resp}) to {address}")
        connection.send(resp.to_bytes())

    def _new_message(self, connection, message):
        print("TODO: This is not implemented yet!")

if __name__ == "__main__":
    server = ControlServer()
    server.main_loop()
