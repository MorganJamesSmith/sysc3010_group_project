#!/usr/bin/env python3
from time import sleep
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import sys
#Code written by Mario Shebib and taken from https://pimylifeup.com/raspberry-pi-rfid-rc522/

class RC522:

    def __init__(self):
        #creates an instance of a simple MFRC522 class
        self.reader = SimpleMFRC522()


    #method reads security badge and returns the id
    def read_card(self):
        try:
            #library includes a read function
            #id holds the unique id of the security card
            #text holds additional data on the security card
            id, text = self.reader.read()
            print(id)
            account_id = id
        finally:
            #This resets ports used by the card reader
            GPIO.cleanup()
            #returns card id
            return account_id

    #method reads the security badge and returns set text data
    def read_card_data(self):

        try:
            #library includes a read function
            #id holds the unique id of the security card
            #text holds additional data on the security card
            id, text = self.reader.read()
            print(id)
            print(text)
            data = bytes.fromhex(text)
        finally:
            #This resets ports used by the card reader
            GPIO.cleanup()
            #returns text of the card
            return data

if __name__ == "__main__":
    nfc = RC522()
    byte_id = nfc.read_card_data()
    print(byte_id)