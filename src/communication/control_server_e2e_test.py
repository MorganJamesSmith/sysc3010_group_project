#! /usr/bin/env python3

#
# file name: control_server_e2e_tests
# Description: Entry scenario Control server message sequence code for End to End demo
# Author(s): Sunjeevani Pujari and Samuel Dewan 
#

import thingspeak
import transpcrt
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

            #determining message response
            
            #for AccessRequest received, requesting door node for temperature measurement
            if isinstance(message,AccessRequestMessage): 
		print(f"Received \"{data}\" ({message}) from \"{c.peer_address}\"")
                resp = InformationRequestMessage(message.transaction_id,InformationType.USER_TEMPERATURE)
            
            #authorizing access if received temperature from InformationResponse is ideal
            elif isinstance(message,InformationResponseMessage):
		print(f"Received \"{data}\" ({message}) from \"{c.peer_address}\"")
                if message.type == InformationType.USER_TEMPERATURE:
                    if message.payload.user_temp <= 38.5 and message.payload.user_temp >= 36.5:
			resp = AccessResponseMessage(message.transaction_id, True) 

            # sending response to Thingspeak channel
            c.send(resp.to_bytes())
