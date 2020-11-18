#!/usr/bin/env python3
#
# Copyright (C) 2020 by Morgan Smith
#
# DoorActuator.py
#
# Functions for controlling the door actuator

# TODO: Allow for one node to actuate multiple doors

from time import sleep

# Locks the door
def door_lock():
    print("Door locked!")

# Unlocks the door
def door_open():
    print("Door unlocked!")

# Unlocks the door for delay seconds and then locks the door
def door_open_timed(delay):
    print("Door unlocked for", delay, "seconds!")
    sleep(delay)
    print("Door locked!")


# Quick test of functions
if __name__ == "__main__":
    door_lock()
    door_open()
    door_open_timed(1)
