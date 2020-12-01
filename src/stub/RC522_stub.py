#!/usr/bin/env python3


#Code written by Mario Shebib and taken from https://pimylifeup.com/raspberry-pi-rfid-rc522/
import sys

class RC522_stub:
    def __init__(self):
        # Get account id and data from file
        try:
            with open("./stub_text/nfc_id_address.txt", "r") as idfile:
                self.account_id = bytes.fromhex(idfile.read().strip())
            with open("./stub_text/nfc_data.txt", "r") as datafile:
                self.data = bytes.fromhex(datafile.read().strip())
        except FileNotFoundError as e: 
            print("RC522: Could not open testcase files.")
            exit(1)
    #method returns id from file
    def read_card(self):
        print(self.account_id.hex())
        return self.account_id
    
    #method returns data from file
    def read_card_data(self):
        print("SUCCESS")
        return self.data
