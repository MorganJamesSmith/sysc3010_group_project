#! /usr/bin/env python3

import thingspeak
import transport
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

c = transport.Connection(channel, "client", "server")
c.established.wait()
print("Connection established.")

message = AccessRequestMessage(0, bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))

c.send(message.to_bytes())
print("Message sent.")
data = c.recv()
rsp = Message.from_bytes(data)
print(f"Received \"{data}\" ({rsp})")

message = AccessRequestMessage(0, bytes([16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]))

c.send(message.to_bytes())
print("Message sent.")
data = c.recv()
rsp = Message.from_bytes(data)
print(f"Received \"{data}\" ({rsp})")

