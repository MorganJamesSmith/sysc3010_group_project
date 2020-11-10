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

c = transport.Connection(channel, "client", "control_server")
c.established.wait()
print("Connection established.")

# Send the access request
print(f"Sending access request: tid {0}")
message = AccessRequestMessage(0, bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))
c.send(message.to_bytes())

# Receive the information request
data = c.recv()
try:
    rsp = Message.from_bytes(data)
except:
    print(f"Received invalid message \"{data}\"")
    exit(1)

print(f"Received \"{data}\" ({rsp})")
if not isinstance(rsp, InformationRequestMessage):
    print(f"Received unexpected message (expected information request)")
    exit(1)
if rsp.transaction_id != 0:
    print(f"Received message with unexpected transaction id ({rsp.transaction_id})")
    exit(1)

print(f"Information request: tid {rsp.transaction_id}, type {rsp.information_type}")

# Send information response
payload = TemperatureInfoPayload(22.0, 37.0)
print(f"Sending information response: tid {0}, type {InformationType.USER_TEMPERATURE}, payload {payload}")
info_message = InformationResponseMessage(0, InformationType.USER_TEMPERATURE, payload)
c.send(info_message.to_bytes())

# Receive access response

data = c.recv()
try:
    rsp = Message.from_bytes(data)
except:
    print(f"Received invalid message \"{data}\"")
    exit(1)

print(f"Received \"{data}\" ({rsp})")
if not isinstance(rsp, AccessResponseMessage):
    print(f"Received unexpected message (expected access response)")
    exit(1)
if rsp.transaction_id != 0:
    print(f"Received message with unexpected transaction id ({rsp.transaction_id})")
    exit(1)

print(f"Access request: tid {rsp.transaction_id}, accepted {rsp.accepted}")

# Receive door state update
data = c.recv()
try:
    rsp = Message.from_bytes(data)
except:
    print(f"Received invalid message \"{data}\"")
    exit(1)

print(f"Received \"{data}\" ({rsp})")
if not isinstance(rsp, DoorStateUpdateMessage):
    print(f"Received unexpected message (expected door state update)")
    exit(1)

print(f"Door state update: state {rsp.state}")


