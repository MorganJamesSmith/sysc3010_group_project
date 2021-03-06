#! /usr/bin/env python3

#
# file name: control_server_e2e_tests
# Description: Entry scenario Control server message sequence code for End to End demo
# Author(s): Sunjeevani Pujari and Samuel Dewan 
#

import sys
sys.path.append("../../communication")

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
channel = thingspeak.Channel(1222699, write_key=write_key, read_key=read_key)
# Create server on channel
server = transport.Server(channel, "control_server")

clients = {}

while (True):
    r, _, _ = select.select(list(clients.keys()) + [server], [], [])
    
    for c in r:
        if c is server:
            connection, address = server.accept(block = False)
            print(f"New connection from \"{address}\".\n")
            clients[connection] = [0, None]

            # Send door state update
            new_state = DoorState.ALLOWING_ENTRY
            resp = DoorStateUpdateMessage(new_state)
            print(f"Sending door state update ({resp}) to {address}")
            connection.send(resp.to_bytes())

        elif c in clients.keys():
            data = c.recv(block = False)
            try:
                message = Message.from_bytes(data)
            except:
                print(f"Received invalid message from \"{c.peer_address}\"")
            print(f"Received ({message}) from \"{c.peer_address}\"")

            if isinstance(message, AccessRequestMessage):
                if clients[c][0] != 0:
                    print("Received unexpected second access request")
                    exit(1)
                #exit scenario
                if c.peer_address =="exit":
                    resp = AccessResponseMessage(message.transaction_id,True)
                    print(f"Sending access response ({resp}) to {c.peer_address}")
                    c.send(resp.to_bytes())

                    new_state = DoorState.ALLOWING_ENTRY
                    resp = DoorStateUpdateMessage(new_state)
                    print(f"Sending door state update ({resp}) to {c.peer_address}")
                    connection.send(resp.to_bytes())
                    continue
                elif message.transaction_id == 2:
                    print(f"Recieved access request with unauthorized transaction id{message.transaction_id}")
                    resp = AccessResponseMessage(message.transaction_id, False)
                    print(f"Sending access response ({resp}) to {c.peer_address}")
                    c.send(resp.to_bytes())
                    continue
                clients[c][0] = 1
                clients[c][1] = message.transaction_id

                resp = InformationRequestMessage(message.transaction_id,
                                                 InformationType.USER_TEMPERATURE)
                print(f"Sending information request ({resp}) to {c.peer_address}")
                c.send(resp.to_bytes()) 
            elif isinstance(message,InformationResponseMessage):
                if clients[c][0] != 1:
                    print("Received out of sequence information response")
                    exit(1)
                elif clients[c][1] != message.transaction_id:
                    print("Received info response with unexpected transaction id")
                    exit(1)
                clients[c][0] = 0
                
                if message.information_type != InformationType.USER_TEMPERATURE:
                    print("Received info response with unexpected type: {str(message.information_type)}")
                    exit(1)

                # Send an access response
                allow = message.payload.user_temp <= 38.5
                resp = AccessResponseMessage(message.transaction_id, allow)
                print(f"Sending access response ({resp}) to {c.peer_address}")
                c.send(resp.to_bytes())
