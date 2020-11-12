#! /usr/bin/env python3

import sys
sys.path.append("../../communication")

import thingspeak
import transport
from time import sleep

from message import *

def validate_received(data, rsp, tid):
    if type(rsp) == InformationRequestMessage:
        print("Received Information Request")
        if rsp.transaction_id != tid:
            print(f"Received message with unexpected transaction id ({rsp.transaction_id})")
            exit(1)
    elif type(rsp) == AccessResponseMessage:
        print("Received Access Response")
        if rsp.transaction_id != tid:
            print(f"Received message with unexpected transaction id ({rsp.transaction_id})")
            exit(1)
    elif type(rsp) == DoorStateUpdateMessage:
        print("Received Door State Update Request: ",end="")
        print(rsp.state.name)
    else:
        print(f"Received invalid message \"{data}\"")
        exit(1)


def access_request(tid, connection):
    # Send the access request
    print("Sending Access Request")
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
            print("Sending Information Response")
            info_message = InformationResponseMessage(tid, InformationType.USER_TEMPERATURE, payload)
            connection.send(info_message.to_bytes())
        elif type(rsp) == AccessResponseMessage:
            return rsp;
        else:
            print(f"Received invalid message \"{data}\"")
            exit(1)
