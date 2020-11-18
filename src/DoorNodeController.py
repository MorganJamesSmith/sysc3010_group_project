
from communication import thingspeak
from communication import transport
from time import sleep

from message import *
from hardware import RC522
from hardware import LED
from communication import Channel
from communication import Connection


from hardware import RangeFinder #VL53L0X
from hardware import MLX90614
from hardware import ElectronicDoorLock

class DoorNodeController:

    def __init__(self,door_type, transaction_id,limit_distance):


        self.door_type = door_type
        self.thingspeak_chan = Channel
        self.server_conn = Connection
        self.current_state = DoorState
        self.door_type = DoorType

        self.indicator = LED(17,18)
        self.nfc_reader = RC522
        self.range_finder = RangeFinder
        self.ir_temp_sensor = MLX90614
        self.door_lock = ElectronicDoorLock

        self.tid = transaction_id

        self.dist_from_temp_sensor = limit_distance
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
        self.indicator.set_colour(RED)

    
    def main_loop(self):
  
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
                if door_type == EXIT:
                    handle_access_response()
                    continue
                distance = 0
                distance = range_finder.get_range()
                if(distance > self.dist_from_temp_sensor) :
                    self.indicator.set_colour(YELLOW)
                while(distance > self.dist_from_temp_sensor) :
                    distance = range_finder.get_range()
                self.indicator.set_colour(RED)                
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
       
        self.connection.recv()
   
        if(rsp.state == DoorState.ALLOWING_ENTRY):
            self.indicator.set_colour(RED)
            self.door_state = rsp.state
            return self.door_state
        elif(rsp.state == DoorState.NOT_ALLLOWING_ENTRY):
            self.indicator.set_colour(OFF)
            self.door_state = rsp.state
            return self.door_state
        else:
            print("Fail did not receive a valid DoorState update message")
            exit(1)

    def handle_access_response(self, message):

        data = self.connection.recv()
        rsp = Message.from_bytes(data)
        
        if rsp.accepted == True:
            self.indicator.set_colour(GREEN)
            #door_lock
        else:
            #door stays locked
            return false
    
#Enumeration with the for if a DoorNodeController is an entrance or exit
class DoorType(Enum) :
    ENTRANCE
    EXIT


#unit test for door node code

#have it instead be checking what the response to the access_request message

#focus on having the handlers be the stars/decide what happens next