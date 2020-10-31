#! /usr/bin/env python3

import thingspeak
import transport
import select
from time import sleep

from message import *

# Get API keys from file
try:
    with open("api_write_key.txt", "r") as keyfile:
        write_key = keyfile.read().strip()
    with open("api_read_key.txt", "r") as keyfile:
        read_key = keyfile.read().strip()
except FileNotFoundError as e:
    print("Could not open keyfiles.")
    exit(1)

# Get ThingSpeak channel object
channel = thingspeak.Channel(1154788, write_key=write_key, read_key=read_key)
# Create server on channel
server = transport.Server(channel, "server")

clients = []

while (True):
    r, _, _ = select.select(clients + [server], [], [])
    
    for c in r:
        if c is server:
            connection, address = server.accept(block = False)
            print(f"New connection from \"{address}\".")
            clients.append(connection)
        elif c in clients:
            data = c.recv(block = False)
            try:
                message = Message.from_bytes(data)
            except:
                print(f"Received invalid message \"{data}\" from \"{c.peer_address}\"")
            print(f"Received \"{data}\" ({message}) from \"{c.peer_address}\"")

            # respond
            sleep(1)
            resp = AccessResponseMessage(0, True)
            c.send(resp.to_bytes())

