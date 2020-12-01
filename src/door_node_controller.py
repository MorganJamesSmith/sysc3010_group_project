#! /usr/bin/env python3

#
#Code written by Mario Shebib
#
#door_node_controller.py
#
#communication imports
import communication.thingspeak as thingspeak
import communication.transport as transport
import communication.message as message
#
"""
This Module contains the interface for the door node to control
hardware objects and interface with the server through thingspeak
"""
class DoorNodeController:
#
    """
    This class controls the hardware at the door node and communicates
    with the control server to decide whether or not to allow entry into
    the building.
    """
    def __init__(self, address, limit_distance, indicator, range_finder, door_lock, ir_temp_sensor,
                 nfc_reader):
        
        self.indicator = indicator
        self.range_finder = range_finder
        self.door_lock = door_lock
        self.ir_temp_sensor = ir_temp_sensor
        self.nfc_reader = nfc_reader


        self.dist_from_temp_sensor = limit_distance
        """
        Initializes the door node.
        """
        #Communication variables, DoorState, and address of DoorNode
        temp_sensor = mlx90614()
        #are initialized.
        self.thingspeak_chan = 0
        self.server_conn = 0
        self.current_state = message.DoorState(2)
        self.address = address
        #At the initial state of the door node the door is locked.
        self.indicator.set_colour(colour.RED)

    def main_loop(self):
        """
        Main function of code that runs through the specific methods.
        """
        # Get API keys from file
        try:
            with open("api_write_key.txt", "r") as keyfile:
                write_key = keyfile.read().strip()
            with open("api_read_key.txt", "r") as keyfile:
                read_key = keyfile.read().strip()
        except FileNotFoundError as error:
            print("Could not open keyfiles.")
            exit(1)
        # Get ThingSpeak channel object
        self.thingspeak_chan = thingspeak.Channel(1222699, write_key=write_key,
                                                  read_key=read_key)
        self.server_conn = transport.Connection(self.thingspeak_chan,
                                                self.address, "control_server")
        self.server_conn.established.wait()

        #set up transaction id which keeps track of order of messages.
        tid = 0

        #Loop that has the code run indefinitely if needed
        while True:
            current_user = True
            badge_id = self.nfc_reader.read_card_data()
            self.handle_badge_tap(badge_id, tid)
            #Checks the server response and handles server messages
            #until a new person comes
            while current_user:
                data = self.server_conn.recv()
                try:
                    rsp = Message.from_bytes(data)
                except:
                    print(f"Received invalid message \"{data}\"")
                    exit(1)
                else:
                    #Series of if statements to handle the three types
                    #of messages that the DoorNodeController receives
                    if isinstance(rsp, message.InformationRequestMessage):
                        self.handle_information_request(rsp, tid)
                    elif isinstance(rsp, message.AccessResponseMessage):
                        current_user = self.handle_access_response(rsp)
                    elif isinstance(rsp, message.DoorStateUpdateMessage):
                        self.handle_door_state_update(rsp)
                    else:
                        print(f"Received invalid message \"{data}\"")
                        exit(1)
            tid += 1
#
    def handle_badge_tap(self, badge_id, tid):
        """
        sends AccessRequestMessage with badge id
        """
        response = message.AccessRequestMessage(tid, badge_id)
        self.server_conn.send(response.to_bytes())
#
    def handle_information_request(self, response, tid):
        """
        responds to InformationRequestMessages
        gathering temperature data.
        """
        self.indicator.set_colour(colour.YELLOW)
        distance = self.range_finder.get_range()
        #Constantly checks to make sure the code doesn't proceed until
        #the user is in suitable range from the temperature sensor.
        while(self.dist_from_temp_sensor > distance or distance < 300):
            distance = self.range_finder.get_range()
        ambient_temp = self.ir_temp_sensor.get_ambient_temp()
        person_temp = self.ir_temp_sensor.get_ir_temp()
        #Contains the data that will be sent to database.
        payload = message.TemperatureInfoPayload(ambient_temp, person_temp)
        self.indicator.set_colour(colour.RED)
        response = message.InformationResponseMessage(tid, message.InformationType.USER_TEMPERATURE,
                                                      payload)
        self.server_conn.send(response.to_bytes())
#
    def handle_door_state_update(self, response):
        """
        Allows the DoorNodeController to be aware of whether or not it
        should be allowing entry or if the building is full.
        """
        if response.state == message.DoorState.ALLOWING_ENTRY:
            self.indicator.set_colour(colour.RED)
        elif response.state == message.DoorState.NOT_ALLOWING_ENTRY:
            self.indicator.set_colour(colour.OFF)
        else:
            msg = ("Fail, did not receive a valid DoorState "\
                   "update message.")
            print(msg)
            exit(1)
        self.current_state = response.state
        return self.current_state
#
    def handle_access_response(self, response):
        """
        Handles the AccessResponseMessage by either unlocking the door
        or leaving it locked and telling the DoorNode to deal with the
        next user.
        """
        if response.accepted:
            self.indicator.set_colour(colour.GREEN)
            self.door_lock.open()
        else:
            #door stays locked
            self.door_lock.lock()
        return False


if __name__ == '__main__':
    #
    #   Range Finder
    #
    #from hardware.RangeFinder import RangeFinder
    from stub.RangeFinder_stub import RangeFinder_stub as RangeFinder
   
    #
    #   IR Temperature Sensor
    #
    #from hardware.mlx90614 import mlx90614
    from stub.mlx90614_stub import MLX90614_stub as mlx90614

    #
    #   Electronic Door Lock
    #
    #from hardware.DoorActuator import DoorActuator
    from stub.DoorActuator_stub import DoorActuator_stub as DoorActuator

    #
    #   NFC Security badge reader
    #
    #from hardware.RC522 import RC522
    from stub.RC522_stub import RC522_stub as RC522

    #
    #   LED
    #
    #from hardware.LED import LEDColour as colour, LED as LED
    from stub.LED_stub import LEDColour as colour, LED_stub as LED

    
    # Create hardware driver objects
    range_finder = RangeFinder()
    temp_sensor = mlx90614()
    door_lock = DoorActuator()
    badge_reader = RC522()
    led = LED()

    # Create and start door node controller
    controller = DoorNodeController("Main Entrance", 30, led, range_finder, door_lock, temp_sensor,
                                    badge_reader)
    controller.main_loop()

