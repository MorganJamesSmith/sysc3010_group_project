#! /usr/bin/env python3

import sys
sys.path.append("../../communication")

import thingspeak
import transport
from time import sleep

from message import *
from access_request_test import *

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

c = transport.Connection(channel, "entrance", "control_server")
c.established.wait()

print("Entrance Node Tests\n")

print("Case: 1")

# Hand door state update
data = c.recv()
try:
    rsp = Message.from_bytes(data)
except:
    print(f"Received invalid message \"{data}\"")
    exit(1)
validate_received(data, rsp, 0)
if(rsp.state == DoorState.ALLOWING_ENTRY):
    print("Test Successful!")
else:
    print("Fail: Expected rsp.state == DoorState.ALLOWING_ENTRY")
print("")

print("Case: Happy Path")
rsp = access_request(0, c)
if(rsp.accepted == True):
    print("Test Successful!")
else:
    print("Fail: Received Unexpected Response (expected access to be allowed)")
print("")

print("Case: Access that is Immediately Denied")
rsp = access_request(2, c)
if(rsp.accepted == False):
    print("Test Successful!")
else:
    print("Fail: Received Unexpected Response (expected access to be denied)")
print("")
