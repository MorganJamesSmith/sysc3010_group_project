#
#Code written by Mario Shebib
#
#door_node_controller.py
#
# TODO:
#needs to be tested with different equipment
#hardware stubs
#
#communication imports
import communication.thingspeak as thingspeak
import communication.transport as transport
import communication.message as message
#hardware imports
import hardware.RangeFinder as RangeFinder #VL53L0X
import hardware.mlx90614 as mlx90614
import hardware.DoorActuator as DoorActuator
import hardware.RC522 as RC522
import hardware.LED as LED
#
class DoorNodeController:
#
    """
    This class controls the hardware at the door node and communicates
    with the control server to decide whether or not to allow entry into
    the building.
"""
#
    def __init__(self, address, limit_distance, led: LED,
                 distance_sensor: RangeFinder, door_actuator:
                 DoorActuator, temperature_sensor: MLX90614,
                 rc522: RC522):
        """
        Initializes the door node.
        """
        #Communication variables, DoorState, and address of DoorNode
        #are initialized.
        self.thingspeak_chan = Channel()
        self.server_conn = Connection()
        self.current_state = DoorState()
        self.address = address
        #Hardware variables are initialized.
        self.indicator = led
        self.nfc_reader = rc522
        self.range_finder = distance_sensor
        self.ir_temp_sensor = temperature_sensor
        self.door_lock = door_actuator
        self.dist_from_temp_sensor = limit_distance
        #At the initial state of the door node the door is locked.
        self.indicator.set_colour(LED.LEDColour.RED)
#
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
        self.thingspeak_chan = Channel(1222699, write_key=write_key,
                                       read_key=read_key)
        self.server_conn = Connection(self.thingspeak_chan,
                                      self.address, "control_server")
        self.server_conn.established.wait()
        #Loop that has the code run indefinitely if needed
        while True:
            current_user = True
            #set up transaction id which keeps track of order of messages.
            tid = 0
            badge_id = self.nfc_reader.read_card()
            handle_badge_tap(badge_id, tid)
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
                if isinstance(rsp, InformationRequestMessage):
                    handle_information_request(rsp, tid)
                elif isinstance(rsp, AccessResponseMessage):
                    current_user = handle_access_response(rsp)
                elif isinstance(rsp, DoorStateUpdateMessage):
                    handle_door_state_update(rsp)
                else:
                    print(f"Received invalid message \"{data}\"")
                    exit(1)
                tid += 1
#
    def handle_badge_tap(self, badge_id, tid):
        """
        sends AccessRequestMessage with badge id
        """
        response = AccessRequest(tid, badge_id)
        self.server_conn.send(response.to_bytes())
#
    def handle_information_request(self, response, tid):
        """
        responds to InformationRequestMessages with
        gathering temperature data.
        """
        self.indicator.set_colour(LEDColour.YELLOW)
        distance = self.range_finder.get_range()
        #Constantly checks to make sure the code doesn't proceed until
        #the user is in suitable range from the temperature sensor.
        while(self.dist_from_temp_sensor > distance or distance < 300):
            distance = self.range_finder.get_range()
        ambient_temp = self.ir_temp_sensor.get_ambient_temp()
        person_temp = self.ir_temp_sensor.get_ir_temp()
        #Contains the data that will be sent to database.
        payload = TemperatureInfoPayload(ambient_temp, person_temp)
        self.indicator.set_colour(LEDColour.RED)
        response = InformationResponseMessage(tid,
                                              InformationType.USER_TEMPERATURE,
                                              payload)
        self.server_conn.send(response.to_bytes())
#
    def handle_door_state_update(self, response):
        """
        Allows the DoorNodeController to be aware of whether or not it
        should be allowing entry or if the building is full.
        """
        if response.state == DoorState.ALLOWING_ENTRY:
            self.indicator.set_colour(LED.LEDColour.RED)
        elif response.state == DoorState.NOT_ALLOWING_ENTRY:
            self.indicator.set_colour(LED.LEDColour.OFF)
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
            self.indicator.set_colour(LED.LEDColour.GREEN)
            self.door_lock.open(self)
        else:
            #door stays locked
            self.door_lock.lock(self)
        return False

