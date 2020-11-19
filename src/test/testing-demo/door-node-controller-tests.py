#! /usr/bin/env python3

import sys

sys.path.append("../../communication")
sys.path.append("../../")

from communication import thingspeak
from communication import transport

import unittest

from DoorNodeController import DoorNodeController
from DoorNodeController import DoorType
from message import *


class DoorNodeControllerTest(unittest.TestCase):
        
        
    def test_handle_access_response(self):
        self.door_node = DoorNodeController(DoorType.ENTRANCE, 1, 0)
        message_true = AccessResponseMessage(1,True)
        
        self.assertTrue(self.door_node.handle_access_response(message_true))
        message_false = AccessResponseMessage(2, False)
        self.assertFalse(self.door_node.handle_access_response(message_false))
    
#     def test_handle_badge_tap(self, badge_id):
#         message = AccessRequest(1,badge_id)
# 
#     
#     def test_handle_information_request(self, message):
# 
#         ambient_temp = self.ir_temp_sensor.get_ambient_temp()
#         person_temp = self.ir_temp_sensor.get_ir_temp()
#         payload = TemperatureInfoPayload(ambient_temp,person_temp)
#         message = InformationResponseMessage(self.tid, InformationType.USER_TEMPERATURE, payload)
#     
    def test_handle_door_state_update(self):
        self.door_node = DoorNodeController(DoorType.ENTRANCE, 1, 0)
        message_allow = DoorStateUpdateMessage(DoorState.ALLOWING_ENTRY)
        self.assertEqual(DoorState.ALLOWING_ENTRY, self.door_node.handle_door_state_update(message_allow))
        message_not_allow = DoorStateUpdateMessage(DoorState.NOT_ALLOWING_ENTRY)
        self.assertEqual(DoorState.NOT_ALLOWING_ENTRY, self.door_node.handle_door_state_update(message_not_allow))       

if __name__ == '__main__': 
    unittest.main() 