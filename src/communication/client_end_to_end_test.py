#! /usr/bin/env python3

import thingspeak
import transport
from time import sleep

from message import *

def validate_received(data, rsp, tid):
    print(f"Received \"{data}\" ({rsp})")

    if type(rsp) == InformationRequestMessage:
        print(f"Information request: tid {rsp.transaction_id}, type {rsp.information_type}")
        if rsp.transaction_id != tid:
            print(f"Received message with unexpected transaction id ({rsp.transaction_id})")
            exit(1)
    elif type(rsp) == AccessResponseMessage:
        print(f"Access request: tid {rsp.transaction_id}, accepted {rsp.accepted}")
        if rsp.transaction_id != tid:
            print(f"Received message with unexpected transaction id ({rsp.transaction_id})")
            exit(1)
    elif type(rsp) == DoorStateUpdateMessage:
        print(f"Door state update: state {rsp.state}")
    else:
        print(f"Received invalid message \"{data}\"")
        exit(1)


def access_request(tid, connection):
    # Send the access request
    print(f"Sending access request: tid {tid}")
    message = AccessRequestMessage(tid, bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))
    connection.send(message.to_bytes())

    while(True):
        data = connection.recv()
        try:
            rsp = Message.from_bytes(data)
        except:
            print(f"Received invalid message \"{data}\"")
            exit(1)

        validate_received(data, rsp, tid)

        if type(rsp) == InformationRequestMessage:
            # Send information response
            payload = TemperatureInfoPayload(22.0, 37.0)
            print(f"Sending information response: tid {tid}, type {InformationType.USER_TEMPERATURE}, payload {payload}")
            info_message = InformationResponseMessage(tid, InformationType.USER_TEMPERATURE, payload)
            connection.send(info_message.to_bytes())
        elif type(rsp) == AccessResponseMessage:
            break;
        else:
            print(f"Received invalid message \"{data}\"")
            exit(1)


if __name__ == "__main__":
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

    access_request(0, c)
