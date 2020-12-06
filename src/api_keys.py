# Copyright (C) 2020 by Morgan Smith

from dataclasses import dataclass

@dataclass
class ApiKeys:
    write_key: str
    read_key: str
    def __init__(self):
        try:
            with open("api_write_key.txt", "r") as keyfile:
                self.write_key = keyfile.read().strip()
            with open("api_read_key.txt", "r") as keyfile:
                self.read_key = keyfile.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(
                'Make sure your API keys are located in' +
                '"api_write_key.txt" and "api_read_key.txt"')
