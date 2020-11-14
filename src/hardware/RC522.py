#!/usr/bin/env python3

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
#Code written by Mario Shebib and taken from https://pimylifeup.com/raspberry-pi-rfid-rc522/

class RC522:

    #method reads security badge and returns the id
    def read_card():
        #creates an instance of a simple MFRC522 class
        reader = SimpleMFRC522()
        #account_id holds id data outside of try loop
        account_id
        try:
            #library includes a read function
            #id holds the unique id of the security card
            #text holds additional data on the security card
            id, text = reader.read()
            print(id)
            account_id = id
        finally:
            #This resets ports used by the card reader
            GPIO.cleanup()
            #returns card id
            return account_id

    #method reads the security badge and returns set text data
    def read_card_data(adr):
        #creates an instance
        reader = SimpleMFRC522()
        #data is a variable to hold data outside of try loop
        data
        try:
            #library includes a read function
            #id holds the unique id of the security card
            #text holds additional data on the security card
            id, text = reader.read()
            print(id)
            print(text)
            data = text
        finally:
            #This resets ports used by the card reader
            GPIO.cleanup()
            #returns text of the card
            return data

