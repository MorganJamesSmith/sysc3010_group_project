#!/usr/bin/env python3
#
# Copyright (C) 2020 by Mario Shebib
#
# DoorActuator_stub.py
#
# Functions for controlling the door actuator stub

from time import sleep

class DoorActuator_stub:

    def clean_up(self):
        print("Door Actuator has been cleaned")

    def __init__(self):
        self.servo_delay = 0.5
        sleep(self.servo_delay)

    # Locks the door
    def lock(self):
        print("Door is now locked")
        sleep(self.servo_delay)
    # Unlocks the door
    def open(self):
        print("Door is now opened")
        sleep(self.servo_delay)
    # Unlocks the door for delay seconds and then locks the door
    def open_timed(self, delay):
        print("Door is now open for " + delay + " seconds")
        sleep(delay)
        print("Door is now closed")
        sleep(self.servo_delay)
