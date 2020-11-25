 #! /usr/bin/env python3

from time import sleep
from enum import Enum, auto

import sys
sys.path.append("./communication")

from thingspeak import Channel
from transport import Connection
from message import *

from hardware import RangeFinder #VL53L0X
from hardware import mlx90614
from hardware import DoorActuator
from hardware import RC522
from hardware import LED

class DoorNodeController:

    def __init__(self, address, limit_distance, LED, RangeFinder,
                 DoorActuator, MLX90614, RC522):

        self.thingspeak_chan = Channel
        self.server_conn = Connection
        self.current_state = DoorState
        
        self.indicator = LED
        self.nfc_reader = RC522
        self.range_finder = RangeFinder
        self.ir_temp_sensor = mlx90614.MLX90614
        self.door_lock = DoorActuator.DoorActuator
        self.dist_from_temp_sensor = limit_distance
        self.indicator.set_colour(LED.LEDColour.RED)
        self.address = address

    
    def main_loop(self):
        # Get API keys from file
        try:
            with open("api_write_key.txt", "r") as keyfile:
                write_key = keyfile.read().strip()
            with open("api_read_key.txt", "r") as keyfile:
                read_key = keyfile.read().strip()
        except FileNotFoundError as e:
            print("Could not open keyfiles.")
            exit(1)
        
        # Get ThingSpeak channel object
        self.thingspeak_chan = Channel(1222699, write_key=write_key,
                                       read_key=read_key)
        self.server_conn = Connection(self.thingspeak_chan,
                                      self.address, "control_server")
        self.server_conn.established.wait()  
        while True:
            next_person = False
            #set up transaction id which keeps track of order of signals.
            self.tid = 0
            badge_id = self.nfc_reader.read_card()
            handle_badge_tap(badge_id)
            while next_person == False:
                data = self.server_conn.recv()
                try:
                    rsp = Message.from_bytes(data)
                except:
                    print(f"Received invalid message \"{data}\"")
                    exit(1)
                if type(rsp) == InformationRequestMessage:
                    handle_information_request(rsp)
                elif type(rsp) == AccessResponseMessage:
                    next_person = handle_access_response(rsp)
                elif type(rsp) == DoorStateUpdateMessage:
                    handle_door_state_update(rsp)
                else:
                    print(f"Received invalid message \"{data}\"")
                    exit(1)
                self.tid += 1

    def handle_badge_tap(self, badge_id):

        message = AccessRequest(self.tid,badge_id)
        self.server_conn.send(message.to_bytes())
        
    def handle_information_request(self, message):
        
        distance = 0
        distance = self.range_finder.get_range()
        self.indicator.set_colour(LEDColour.YELLOW)          
        while(distance > self.dist_from_temp_sensor) :
            distance = self.range_finder.get_range()

        ambient_temp = self.ir_temp_sensor.get_ambient_temp()
        person_temp = self.ir_temp_sensor.get_ir_temp()
        payload = TemperatureInfoPayload(ambient_temp,person_temp)
        self.indicator.set_colour(LEDColour.RED) 
        message = InformationResponseMessage(self.tid,
                        InformationType.USER_TEMPERATURE, payload)
        self.server_conn.send(message.to_bytes())
           
        
     
    def handle_door_state_update(self, message):
          
        if(message.state == DoorState.ALLOWING_ENTRY):
            self.indicator.set_colour(LED.LEDColour.RED)
            self.current_state = message.state
            return self.current_state
        elif(message.state == DoorState.NOT_ALLOWING_ENTRY):
            self.indicator.set_colour(LED.LEDColour.OFF)
            self.current_state = message.state
            return self.current_state
        else:
            msg = ("Fail, did not receive a valid DoorState "\
                   "update message.")

            print(msg)
            exit(1)

    def handle_access_response(self, message):
        
        if message.accepted:
             self.indicator.set_colour(LED.LEDColour.GREEN)
             self.door_lock.open(self)
             return True
        else:
             #door stays locked
             self.door_lock.lock(self)
             return True    
#needs to be tested with different equipment
#more comments
#hardware stubs



