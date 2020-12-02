#Code written by Mario Shebib and taken from https://pimylifeup.com/raspberry-pi-rfid-rc522/

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
