#! /usr/bin/env python3

import sys
sys.path.append("../../communication")

from datetime import datetime
import base64

from message import *
from transport import TransportLayerFlags, TransportLayerHeader

class ThingSpeakCSVLine:
    def __init__(self, s):
        split = s.split(',')

        # Entry timestamp
        self.timestamp = datetime.fromisoformat(split[0][:-4])
        # Entry number
        self.num = int(split[1])
        # Field 1: header
        self.header = TransportLayerHeader.from_string(split[2])
        # Field 2: application layer data
        if split[3]:
            self.message = Message.from_bytes(base64.b64decode(split[3]))
        else:
            self.message = None

    def __str__(self):
        s = f"Mesage {self.num} at {self.timestamp}:\t{self.header.source_addr:15} ->   "
        s += f"{self.header.dest_addr:15}\t"

        if TransportLayerFlags.CONN_REQ in self.header.flags:
            s += f"connection request"
        else:
            s += str(self.message)

        return s
            

lines = []

print("Please enter CSV data from ThingSpeak (ending with an empty line):")

while True:
    line = input().strip()
    if not line:
        break
    lines.append(line)

print()
print()

lines = map(lambda i: ThingSpeakCSVLine(i), lines)

for l in lines:
    print(l)

