#! /usr/bin/env python3

import thingspeak
import transport
import select

# Get ThingSpeak channel object
channel = thingspeak.Channel(1154788, write_key="HYQQBPCP3Q0GLKCB",
                             read_key="K5V3D8C2OMPAOKSO")
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
            data = c.recv(block = False).decode('utf-8')
            print(f"Received \"{data}\" from \"{c.peer_address}\"")
            # echo
            c.send(data.encode('utf-8'))

