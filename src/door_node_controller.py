#
#Code written by Mario Shebib
#
#door_node_controller.py
#
# TODO:
#needs to be tested with different equipment
#
#communication imports
import communication.thingspeak as thingspeak
import communication.transport as transport
import communication.message as message
#
class DoorNodeController:
#
    """
    This class controls the hardware at the door node and communicates
    with the control server to decide whether or not to allow entry into
    the building.
    """
    def __init__(self, address, limit_distance, led,
                 distance_sensor, door_actuator, temperature_sensor, rc522):
    #hardware imports
        if distance_sensor is not None:
            import hardware.RangeFinder as RangeFinder #VL53L0X
            self.range_finder = distance_sensor
        else:
            import stub.RangeFinder_stub as RangeFinder
            self.range_finder = RangeFinder.RangeFinder_stub()
        if temperature_sensor is not None:
            import hardware.mlx90614 as mlx90614
            self.ir_temp_sensor = temperature_sensor
        else:
            import stub.mlx90614_stub as mlx90614
            self.ir_temp_sensor = mlx90614.MLX90614_stub()
        if door_actuator is not None:
            import hardware.DoorActuator as DoorActuator
            self.door_lock = door_actuator
        else:
            import stub.DoorActuator_stub as DoorActuator
            self.door_lock = DoorActuator.DoorActuator_stub()
        if rc522 is not None:
            import hardware.RC522 as RC522
            self.nfc_reader = rc522
        else:
            import stub.RC522_stub as RC522
            self.nfc_reader = RC522.RC522_stub()
        if led is not None:
            import hardware.LED as LED
            from hardware.LED import LEDColour as colour
            self.indicator = led
        else:
            import stub.LED_stub as LED
            from stub.LED_stub import LEDColour as colour
            self.indicator = LED.LED_stub()
        self.dist_from_temp_sensor = limit_distance
        """
        Initializes the door node.
        """
        #Communication variables, DoorState, and address of DoorNode
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
        #Loop that has the code run indefinitely if needed
        while True:
            current_user = True
            #set up transaction id which keeps track of order of messages.
            tid = 0
            badge_id = self.nfc_reader.read_card()
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
        badge_message = badge_id.to_bytes(16, byteorder='little')
        response = message.AccessRequestMessage(tid, badge_message)
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
            self.door_lock.open(self)
        else:
            #door stays locked
            self.door_lock.lock()
        return False

if __name__ == "__main__":
    door = DoorNodeController("Entrance", 300, None, None, None, None, None)
    door.main_loop()
