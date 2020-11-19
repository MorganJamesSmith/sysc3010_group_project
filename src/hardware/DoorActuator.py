#!/usr/bin/env python3
#
# Copyright (C) 2020 by Morgan Smith
#
# DoorActuator.py
#
# Functions for controlling the door actuator

from time import sleep
import RPi.GPIO as GPIO

class DoorActuator:


    def clean_up(self):
        self.p.stop()
        GPIO.cleanup()

    def __init__(self, servo_pin, frequency):
        self.locked = 12.5
        self.unlocked = 2.5
        self.servo_delay = 0.5
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(servo_pin, GPIO.OUT)
        self.p = GPIO.PWM(servo_pin, frequency)
        self.p.start(self.locked)
        sleep(self.servo_delay)

    # Locks the door
    def lock(self):
        self.p.ChangeDutyCycle(self.locked)
        sleep(self.servo_delay)

    # Unlocks the door
    def open(self):
        self.p.ChangeDutyCycle(self.unlocked)
        sleep(self.servo_delay)

    # Unlocks the door for delay seconds and then locks the door
    def open_timed(self, delay):
        self.p.ChangeDutyCycle(self.unlocked)
        sleep(delay)
        self.p.ChangeDutyCycle(self.locked)
        sleep(self.servo_delay)


# Quick test of functions
if __name__ == "__main__":
    door = DoorActuator(12, 50)
    door.open()
    door.lock()
    door.open_timed(1)
    door.clean_up()
