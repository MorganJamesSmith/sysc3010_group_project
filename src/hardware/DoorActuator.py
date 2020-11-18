#!/usr/bin/env python3
#
# Copyright (C) 2020 by Morgan Smith
#
# DoorActuator.py
#
# Functions for controlling the door actuator

# TODO: Allow for one node to actuate multiple doors

from time import sleep
import RPi.GPIO as GPIO

locked = 12.5
unlocked = 2.5
servo_delay = 0.5

p = ""

def door_clean_up():
    p.stop()
    GPIO.cleanup()

def door_setup(servo_pin, frequency):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(servo_pin, GPIO.OUT)
    global p
    p = GPIO.PWM(servo_pin, frequency)
    p.start(locked)
    sleep(servo_delay)

# Locks the door
def door_lock():
    p.ChangeDutyCycle(locked)
    sleep(servo_delay)
    print("Door locked!")

# Unlocks the door
def door_open():
    p.ChangeDutyCycle(unlocked)
    sleep(servo_delay)
    print("Door unlocked!")

# Unlocks the door for delay seconds and then locks the door
def door_open_timed(delay):
    p.ChangeDutyCycle(unlocked)
    print("Door unlocked for", delay, "seconds!")
    sleep(delay)
    p.ChangeDutyCycle(locked)
    print("Door locked!")
    sleep(servo_delay)


# Quick test of functions
if __name__ == "__main__":
    door_setup(12, 50)
    door_open()
    door_lock()
    door_open_timed(1)
    door_clean_up()
