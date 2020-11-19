#! /usr/bin/env python3

from time import sleep
from enum import Enum, auto

from communication.thingspeak import Channel
from communication.transport import Connection
from communication.message import *

from hardware import RangeFinder #VL53L0X
from hardware import mlx90614
from hardware import DoorActuator
from hardware import RC522
from hardware import LED

class DoorNodeController:

    def __init__(self,door_type, transaction_id,limit_distance):


        self.door_type = door_type
        self.thingspeak_chan = Channel
        self.server_conn = Connection
        self.current_state = DoorState
        self.door_type = DoorType

        self.indicator = LED.LED(17,18)
        self.nfc_reader = RC522
        self.range_finder = RangeFinder
        self.ir_temp_sensor = mlx90614.MLX90614
        self.door_lock = DoorActuator.DoorActuator

        self.tid = transaction_id

        self.dist_from_temp_sensor = limit_distance

        self.indicator.set_colour(LED.LEDColour.RED)

    
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
        channel = thingspeak.Channel(1222699, write_key=write_key, read_key=read_key)

        self.connection = transport.Connection(channel, door_type(str), "control_server")
        self.connection.established.wait()  
        while True:
            
            badge_id = nfc_reader.read_card()
            handle_badge_tap(badge_id)
            data = self.connection.recv()
            try:
                rsp = Message.from_bytes(data)
            except:
                print(f"Received invalid message \"{data}\"")
                exit(1)
            if type(rsp) == InformationRequestMessage:
                if door_type == DoorState.EXIT:
                    handle_access_response(rsp)
                    continue
                distance = 0
                distance = range_finder.get_range()
                if(distance > self.dist_from_temp_sensor) :
                    self.indicator.set_colour(LEDColour.YELLOW)
                while(distance > self.dist_from_temp_sensor) :
                    distance = range_finder.get_range()
                self.indicator.set_colour(LEDColour.RED)                
                # Send information response
                handle_information_request(rsp)
            elif type(rsp) == AccessResponseMessage:
                handle_access_response(rsp)
                continue
            elif type(rsp) == DoorStateUpdate:
                handle_door_state_update(rsp)
            else:
                print(f"Received invalid message \"{data}\"")
                exit(1)



            
            

    def handle_badge_tap(self, badge_id):

        message = AccessRequest(self.tid,badge_id)
        self.connection.send(message.to_bytes())
          
    def handle_information_request(self, message):

        ambient_temp = self.ir_temp_sensor.get_ambient_temp()
        person_temp = self.ir_temp_sensor.get_ir_temp()
        payload = TemperatureInfoPayload(ambient_temp,person_temp)
        message = InformationResponseMessage(self.tid, InformationType.USER_TEMPERATURE, payload)
        self.connection.send(message.to_bytes())
        
        #server side does temp check numbers
        
    def handle_door_state_update(self, message):
          
        if(message.state == DoorState.ALLOWING_ENTRY):
            self.indicator.set_colour(LED.LEDColour.RED)
            self.door_state = message.state
            return self.door_state
        elif(message.state == DoorState.NOT_ALLOWING_ENTRY):
            self.indicator.set_colour(LED.LEDColour.OFF)
            self.door_state = message.state
            return self.door_state
        else:
            print("Fail did not receive a valid DoorState update message")
            exit(1)

    def handle_access_response(self, message):

        if message.accepted == True:
            self.indicator.set_colour(LED.LEDColour.GREEN)
            #self.door_lock.open(self)
            return True
        else:
            #door stays locked
            #self.door_lock.lock(self)
            return False
    
#Enumeration with the for if a DoorNodeController is an entrance or exit
class DoorType(Enum) :
    ENTRANCE = auto()
    EXIT = auto()


#unit test for door node code
#need maximum capacity system
