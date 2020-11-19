#! /usr/bin/env python3

import sys

sys.path.append("../../communication")
sys.path.append("../../")

from communication import thingspeak
from communication import transport

import unittest

import DoorNodeController


class DoorNodeControllerTest(unittest.TestCase):
    def __init__(self,door_type, transaction_id,limit_distance):
        self.door_node = DoorNodeController(ENTRANCE, 1, 0)
        
    def test_handle_access_response(self):
        message_true = AccessResponseMessage(1,True)
        self.assertTrue(self.door_node.handle_access_response(self, message_true))
        message_false = AccessResponseMessage(2, False)
        self.assertFalse(self.door_node.handle_access_response(self, message_false))
    
    def test_handle_badge_tap(self, badge_id):
        message = AccessRequest(1,badge_id)

    
    def test_handle_information_request(self, message):

        ambient_temp = self.ir_temp_sensor.get_ambient_temp()
        person_temp = self.ir_temp_sensor.get_ir_temp()
        payload = TemperatureInfoPayload(ambient_temp,person_temp)
        message = InformationResponseMessage(self.tid, InformationType.USER_TEMPERATURE, payload)
    
    def test_handle_door_state_update(self, message):
        message_allow = DoorStateUpdateMessage(DoorState.ALLOWING_ENTRY)
        self.assertTrue(self.door_node.handle_door_state_update(self, message_allow))
        message_not_allow = AccessResponseMessage(DoorState.NOT_ALLOWING_ENTRY)
        self.assertFalse(self.door_node.handle_door_state_update(self, message_not_allow))       

