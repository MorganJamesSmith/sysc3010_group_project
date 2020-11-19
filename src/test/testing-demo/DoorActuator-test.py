#!/usr/bin/env python3
#
# Copyright (C) 2020 by Morgan Smith
#
# DoorActuator-test.py

import sys
sys.path.append("../../hardware")

from time import sleep
from DoorActuator import DoorActuator

try:
    print("Door Actuator Tests\n")

    door = DoorActuator(12, 50)

    print("Locking the door\n")

    door.lock()
    sleep(3)

    print("Opening the door\n")

    door.open()
    sleep(3)

    print("Locking the door\n")

    door.lock()
    sleep(3)

    print("Doing a timed open for 1 second on repeat")

    while(True):
        door.open_timed(1)
        sleep(1)

except KeyboardInterrupt:
    door.clean_up()
    print("Test Complete!")
