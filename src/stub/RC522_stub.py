#Code written by Mario Shebib and taken from https://pimylifeup.com/raspberry-pi-rfid-rc522/

import os
import sqlite3
from time import sleep

class RC522_stub:
    def __init__(self):
        try:
            self.id_file = open("./stub_text/nfc_id_address.txt", "r")
        except FileNotFoundError:
            self.id_file = None

        try:
            self.data_file = open("./stub_text/nfc_data.txt", "r")
        except FileNotFoundError:
            self.data_file = None

    def read_card(self):
        while True:
            line = self.id_file.readline().strip() if seld.id_file else ''
            if line != '':
                break;
            else:
                sleep(2)
        return line
    
    def read_card_data(self):
        while True:
            line = self.data_file.readline().strip() if self.data_file else ''
            if line != '':
                break
            else:
                sleep(2)
        return line

    def close(self):
        self.id_file.close()
        self.data_file.close()

class RC522_Interactive_stub:
    def __init__(self):
        # Get a list of valid card IDs from the database if it exists
        self.valid_ids = []
        if os.path.isfile('security_system.db'):
            db = sqlite3.connect('security_system.db')
            for row in db.execute('SELECT COALESCE(first_name,"") || " " || COALESCE(middle_name,' +
                                  '"") || " " || COALESCE(last_name,"") as name, nfc_id FROM ' + 
                                  'employee_info'):
                self.valid_ids.append((row[0], row[1].hex()))

    def read_card(self):
        return read_card_data(name="Read card")

    def read_card_data(self, name="Read card data"):
        print(f"{name} - please select a card option")
        while True:
            print("1: Enter data manually")
            for i, val in enumerate(self.valid_ids):
                print(f"{i + 2}: {val[0]} ({val[1]})")

            try:
               value = int(input("> "))
            except ValueError:
                print("Invalid selection.")
                continue
            else:
                if value == 1:
                    return input("Card data: ")
                else:
                    value -= 2
                    if value < 0 or value > len(self.valid_ids):
                        print("Invalid selection.")
                        continue
                    else:
                        return self.valid_ids[value][1]

