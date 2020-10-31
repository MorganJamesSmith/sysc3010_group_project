#! /usr/bin/env python3

import thingspeak
import transport


# Get ThingSpeak channel object
channel = thingspeak.Channel(1154788, write_key="HYQQBPCP3Q0GLKCB",
                             read_key="K5V3D8C2OMPAOKSO")

c = transport.Connection(channel, "client", "server")
c.established.wait()
print("Connection established.")

c.send("Hello World!".encode('utf-8'))
print("Message sent.")
data = c.recv().decode('utf-8')

print(f"Received \"{data}\"")

