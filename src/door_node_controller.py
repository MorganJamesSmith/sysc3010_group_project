#! /usr/bin/env python3

#
#Code written by Mario Shebib
#
#door_node_controller.py
#
import time
from threading import Thread, Event
#communication imports
import communication.thingspeak as thingspeak
import communication.transport as transport
import communication.message as message

VERBOSE = True

"""
This Module contains the interface for the door node to control
hardware objects and interface with the server through thingspeak
"""

class NFCReaderPoller(Thread):
    def __init__(self, nfc_reader, callback):
        Thread.__init__(self)
        self.daemon = True

        self.nfc_reader = nfc_reader
        self.callback = callback

        self.resume_polling = Event()

    def run(self):
        while True:
            data = self.nfc_reader.read_card_data()
            self.callback(data)

            self.resume_polling.wait()
            self.resume_polling.clear()
    def resume(self):
        self.resume_polling.set()

class DoorNodeController:
    """
    This class controls the hardware at the door node and communicates
    with the control server to decide whether or not to allow entry into
    the building.
    """
    def __init__(self, address, indicator, range_finder, door_lock, ir_temp_sensor, nfc_reader,
                 temp_sense_min_dist, temp_sense_max_dist):
        self.address = address

        self.indicator = indicator
        self.range_finder = range_finder
        self.door_lock = door_lock
        self.ir_temp_sensor = ir_temp_sensor
        self.nfc_reader = nfc_reader

        self.temp_sense_min_dist = temp_sense_min_dist
        self.temp_sense_max_dist = temp_sense_max_dist

        self.tid = 0
        self.transaction_ongoing = False

        self.nfc_poller = NFCReaderPoller(self.nfc_reader, self.handle_badge_tap)
        # Get API keys from file
        try:
            with open("api_write_key.txt", "r") as keyfile:
                write_key = keyfile.read().strip()
            with open("api_read_key.txt", "r") as keyfile:
                read_key = keyfile.read().strip()
        except FileNotFoundError as error:
            print("Could not open keyfiles.")
            exit(1)
        # Connect to server via ThingSpeak channel
        self.thingspeak_chan = thingspeak.Channel(1222699, write_key=write_key, read_key=read_key)
        self.server_conn = transport.Connection(self.thingspeak_chan, self.address,
                                                "control_server")
        self.current_state = message.DoorState.NOT_ALLOWING_ENTRY
        # At the initial state of the door node the door is locked.
        self.indicator.set_colour(colour.RED)

    def main_loop(self):
        try:
            """
            Main function of code that runs through the specific methods.
            """
            # Wait for conection to server to be established
            ret = self.server_conn.established.wait(timeout=10)
            if not ret:
                print("Connection to control server timed out")
                exit(1)
            # Start polling for NFC badge taps
            self.nfc_poller.start()
            # Loop that has the code run indefinitely
            while True:
                data = self.server_conn.recv()

                try:
                    rsp = message.Message.from_bytes(data)
                except message.MessageException as error:
                    print(f"Received invalid message \"{error}\"")
                else:
                    if hasattr(rsp, "transaction_id") and (rsp.transaction_id != self.tid):
                        print(f"Received message for unkown transaction: {rsp}")
                        continue

                    if isinstance(rsp, message.InformationRequestMessage):
                        self.handle_information_request(rsp)
                    elif isinstance(rsp, message.AccessResponseMessage):
                        self.handle_access_response(rsp)
                    elif isinstance(rsp, message.DoorStateUpdateMessage):
                        self.handle_door_state_update(rsp)
                    else:
                        print(f"Received unexpected message: {rsp}")
        finally:
            self.indicator.clean_up()
            self.door_lock.clean_up()
            self.nfc_reader.clean_up()
    def handle_badge_tap(self, badge_data):
        """
        sends AccessRequestMessage with badge id
        """
        if self.transaction_ongoing:
            return

        try:
            badge_id = bytes.fromhex(badge_data)
        except ValueError:
            print(f"Received invalid badge ID: \"{badge_data}\"")
            self.nfc_poller.resume()
        else: 
            if len(badge_id) != 16:
                print(f"Received badge ID with invalid length: \"{badge_id}\"")
                self.nfc_poller.resume()
                return

            if VERBOSE:
                print(f"NFC Security Badge Tapped: {badge_id.hex()}")

            self.transction_ongoing = True
            response = message.AccessRequestMessage(self.tid, badge_id)
            self.server_conn.send(response.to_bytes())

    def handle_information_request(self, request):
        """
        responds to InformationRequestMessages
        gathering temperature data.
        """

        if request.information_type == message.InformationType.USER_TEMPERATURE:
            payload = self.get_user_temperature()
        else:
            print(f"Recevied request for unkown information type: {request}")        

        response = message.InformationResponseMessage(self.tid, request.information_type, payload)
        self.server_conn.send(response.to_bytes())

    def get_user_temperature(self):
        if VERBOSE:
            print("Getting user temperature")

        self.indicator.set_colour(colour.YELLOW)
        #Constantly checks to make sure the code doesn't proceed until
        #the user is in suitable range from the temperature sensor.
        distance = self.range_finder.get_range()
        while(distance < self.temp_sense_min_dist or distance > self.temp_sense_max_dist):
            time.sleep(0.1)
            distance = self.range_finder.get_range()

        ambient_temp = self.ir_temp_sensor.get_ambient_temp()
        person_temp = self.ir_temp_sensor.get_ir_temp()

        self.indicator.set_colour(colour.OFF)

        return message.TemperatureInfoPayload(ambient_temp, person_temp)      

    def handle_door_state_update(self, update):
        """
        Allows the DoorNodeController to be aware of whether or not it
        should be allowing entry or if the building is full.
        """
        if not self.transaction_ongoing:
            # If we are not in the middle of a transaction change the LED colour to reflect the new
            # state
            if update.state == message.DoorState.ALLOWING_ENTRY:
                self.indicator.set_colour(colour.RED)
            elif update.state == message.DoorState.NOT_ALLOWING_ENTRY:
                self.indicator.set_colour(colour.OFF)
            else:
                # This should be impossible
                print(f"Recevied an invalid door state update: {update}")
                return

        self.current_state = update.state

    def handle_access_response(self, response):
        """
        Handles the AccessResponseMessage by either unlocking the door
        or leaving it locked and telling the DoorNode to deal with the
        next user.
        """
        if response.accepted:
            if VERBOSE:
                print("Access granted.")

            self.indicator.set_colour(colour.GREEN)
            self.door_lock.open_timed(10)
            self.indicator.set_colour(colour.RED if self.current_state ==
                                      message.DoorState.ALLOWING_ENTRY else colour.OFF)
        else:
            if VERBOSE:
                print("Access denied.")

            # Door stays locked, set LED red for at least 5 seconds
            self.indicator.set_colour(colour.RED)
            time.sleep(5)
            # If we are not allowing entry the LED should go off between transactions
            if self.current_state == message.DoorState.NOT_ALLOWING_ENTRY:
                self.indicator.set_colour(colour.OFF)

        # Clean up transaction
        self.tid += 1
        self.transaction_ongoing = False
        self.nfc_poller.resume()


if __name__ == '__main__':
    bus = None

    #
    #   Range Finder
    #
    from hardware.RangeFinder import RangeFinder
    #from stub.RangeFinder_stub import RangeFinder_stub as RangeFinder
    #from stub.RangeFinder_stub import RangeFinder_Interactive_stub as RangeFinder   

    #
    #   IR Temperature Sensor
    #
    import smbus
    bus = smbus.SMBus(1)
    from hardware.mlx90614 import MLX90614 as mlx90614
    #from stub.mlx90614_stub import MLX90614_stub as mlx90614
    #from stub.mlx90614_stub import MLX90614_Interactive_stub as mlx90614

    #
    #   Electronic Door Lock
    #
    #from hardware.DoorActuator import DoorActuator
    from stub.DoorActuator_stub import DoorActuator_stub as DoorActuator

    #
    #   NFC Security badge reader
    #
    #from hardware.RC522 import RC522
    #from stub.RC522_stub import RC522_stub as RC522
    from stub.RC522_stub import RC522_Interactive_stub as RC522

    #
    #   LED
    #
    from hardware.LED import LEDColour as colour, LED as LED
    #from stub.LED_stub import LEDColour as colour, LED_stub as LED
    
    # Create hardware driver objects
    led = LED(17, 18)
    range_finder = RangeFinder()
    temp_sensor = mlx90614(bus)
    door_lock = DoorActuator(12, 50)
    badge_reader = RC522()

    # Create and start door node controller
    controller = DoorNodeController("Sam's Entrance", led, range_finder, door_lock, temp_sensor,
                                    badge_reader, 20, 150)
    controller.main_loop()
