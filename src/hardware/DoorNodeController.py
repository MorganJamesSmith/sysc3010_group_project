
import sys
sys.path.append("../../communication")

import thingspeak
import transport
from time import sleep

from message import *
import RC522
import LED
import DoorState
import Channel
import Connection


import RangeFinder #VL53L0X
import MLX90614
import ElectronicDoorLock

class DoorNodeController:

    thingspeak_chan
    server_conn
    current_state

    indicator
    nfc_reader
    range_finder
    ir_temp_sensor
    door_lock
    dist_from_temp_sensor
    door_state
    global c

    def __init__(self,door_type):

        global thingspeak_chan
        global server_conn
        global current_state
        global c

        global indicator
        global nfc_reader
        global range_finder
        global ir_temp_sensor
        global door_lock
        global dist_from_temp_sensor
        self.door_type = door_type
        thingspeak_chan = Channel
        server_conn = Connection
        current_state = DoorState
        door_type = DoorType

        indicator = LED
        nfc_reader = RC522
        range_finder = RangeFinder
        ir_temp_sensor = MLX90614
        door_lock = ElectronicDoorLock

        dist_from_temp_sensor = 50
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

        c = transport.Connection(channel, door_type, "control_server")
        c.established.wait()
        indicator.__init__()
    
    def main_loop():
        __init__(self)
        global indicator
        global nfc_reader
        global range_finder
        global door_state
  
        while True:
            door_state = handle_door_state_update(message)
            badge_id = nfc_reader.read_card()
            handle_badge_tap(badge_id)
            if(self.door_type == 2):
                #lock = accessresponsehandle
                #door_lock(lock)
                indicator.set_colour(2)
                handle_door_state_update(message)
                continue    
            distance = 0
            distance = range_finder.get_range()
            if(distance > dist_from_temp_sensor) :
                indicator.set_colour(3)
            while(distance > dist_from_temp_sensor) :
                distance = range_finder.get_range()
            indicator.set_colour(1)
            handle_information_request()
            #lock = accessresponsehandle
            #door_lock(lock)
            indicator.set_colour(2)
            handle_door_state_update(message)
            
            

    def handle_badge_tap(badge_id):
        global c
        #first value should become variable
        #first value indicates which door it is
        message = AccessRequest(1,badge_id)
        c.send(message.to_bytes())

        
        
    def handle_information_request(request):
        global ir_temp_sensor
        global c

        ambient_temp = ir_temp_sensor.get_ambient_temp()
        person_temp = ir_temp_sensor.get_ir_temp()
        #first value should be variable not sure about information type
        message = InformationResponseMessage(1,ambient_temp,person_temp)
        
        #server side does temp check numbers
        
    def handle_door_state_update(message):
        global door_state
        global indicator
        global c
        
        c.recv()
        try:
            rsp = Message.from_bytes(data)
        except:
            print(f"Received invalid message \"{data}\"")
            exit(1)
        validate_received(data, rsp, 0)
        if(rsp.state == DoorState.ALLOWING_ENTRY):
            indicator.set_colour(RED)
            door_state = rsp.state
            return door_state
        elif(rsp.state == DoorState.NOT_ALLLOWING_ENTRY):
            indicator.set_colour(OFF)
            door_state = rsp.state
            return door_state
        else:
            print("Fail did not receive a valid DoorState update message")
            exit(1)

    
#Enumeration with the for if a DoorNodeController is an entrance or exit
class DoorType(Enum) :
    ENTRANCE = 1
    EXIT = 2