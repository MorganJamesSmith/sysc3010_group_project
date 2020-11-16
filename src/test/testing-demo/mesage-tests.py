#! /usr/bin/env python3

import unittest

import sys
sys.path.append("../../communication")
from message import *

class AccessRequestMessageTests(unittest.TestCase):
    def testConstructor(self):
        m = AccessRequestMessage(0xAAAAAAAA, bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                                                    15, 16]))

        assert m.transaction_id == 0xAAAAAAAA, "transaction_id set incorrectly"
        assert m.badge_id == bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]), \
                "badge_id set incorrectly"

    def testToBytes(self):
        m = AccessRequestMessage(0xAAAAAABB, bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                                                    15, 16]))
        b = m.to_bytes()

        assert b == bytes([0x00, 0x00, 0x00, 0x01, 0xAA, 0xAA, 0xAA, 0xBB, 0x01, 0x02, 0x03,
                           0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E,
                           0x0F, 0x10]), "Failed to convert AccessRequestMessage to bytes"
    
    def testFromBytes(self):
        m = Message.from_bytes(bytes([0x00, 0x00, 0x00, 0x01, 0xAA, 0xAA, 0xAA, 0xBB, 0x01, 0x02,
                                      0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C,
                                      0x0D, 0x0E, 0x0F, 0x10]))

        assert isinstance(m, AccessRequestMessage), "not parsed to correct message class"
        assert m.transaction_id == 0xAAAAAABB, "transaction id not parsed correctly"
        assert m.badge_id == bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]), \
               "badge id not parseed correctly"

    def testFromBytesInvalid(self):
        try:
            # Message is one byte too short, otherwise valid
            m = Message.from_bytes(bytes([0x00, 0x00, 0x00, 0x01, 0xAA, 0xAA, 0xAA, 0xBB, 0x01,
                                          0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A,
                                          0x0B, 0x0C, 0x0D, 0x0E, 0x0F]))
        except MessageException:
            pass
        else:
            fail("expected MessageException")

class AccessResponseMessageTests(unittest.TestCase):
    def testConstructor(self):
        m = AccessResponseMessage(0xAAAAAAAA, True)

        assert m.transaction_id == 0xAAAAAAAA, "transaction_id set incorrectly"
        assert m.accepted == True, "accepted set incorrectly"

    def testToBytes(self):
        m = AccessResponseMessage(0xAAAAAABB, True)
        b = m.to_bytes()

        assert b == bytes([0x00, 0x00, 0x00, 0x02, 0xAA, 0xAA, 0xAA, 0xBB, 0x00, 0x00, 0x00,
                           0x01]), "Failed to convert AccessResponseMessage to bytes"
    
    def testFromBytes(self):
        m = Message.from_bytes(bytes([0x00, 0x00, 0x00, 0x02, 0xAA, 0xAA, 0xAA, 0xBB, 0x00, 0x00,
                                      0x00, 0x01]))

        assert isinstance(m, AccessResponseMessage), "not parsed to correct message class"
        assert m.transaction_id == 0xAAAAAABB, "transaction id not parsed correctly"
        assert m.accepted == True, "accepted flag not parsed correctly"

    def testFromBytesInvalid(self):
        try:
            # Message is one byte too short, otherwise valid
            m = Message.from_bytes(bytes([0x00, 0x00, 0x00, 0x02, 0xAA, 0xAA, 0xAA, 0xBB, 0x00,
                                          0x00, 0x01]))
        except MessageException:
            pass
        else:
            fail("expected MessageException")

class InformationRequestMessageTests(unittest.TestCase):
    def testConstructor(self):
        m = InformationRequestMessage(0xAAAAAAAA, InformationType.USER_TEMPERATURE)

        assert m.transaction_id == 0xAAAAAAAA, "transaction_id set incorrectly"
        assert m.information_type == InformationType.USER_TEMPERATURE, \
               "information type set incorrectly"

    def testToBytes(self):
        m = InformationRequestMessage(0xAAAAAABB, InformationType.USER_TEMPERATURE)
        b = m.to_bytes()

        assert b == bytes([0x00, 0x00, 0x00, 0x03, 0xAA, 0xAA, 0xAA, 0xBB, 0x00, 0x00, 0x00,
                           0x01]), "Failed to convert InformationRequestMessage to bytes"
    
    def testFromBytes(self):
        m = Message.from_bytes(bytes([0x00, 0x00, 0x00, 0x03, 0xAA, 0xAA, 0xAA, 0xBB, 0x00, 0x00,
                                      0x00, 0x01]))

        assert isinstance(m, InformationRequestMessage), "not parsed to correct message class"
        assert m.transaction_id == 0xAAAAAABB, "transaction id not parsed correctly"
        assert m.information_type == InformationType.USER_TEMPERATURE, \
               "information type parsed incorrectly"

    def testFromBytesInvalid(self):
        try:
            # Message is one byte too short, otherwise valid
            m = Message.from_bytes(bytes([0x00, 0x00, 0x00, 0x03, 0xAA, 0xAA, 0xAA, 0xBB, 0x00,
                                          0x00, 0x01]))
        except MessageException:
            pass
        else:
            fail("expected MessageException")

class InformationResponseMessageTests(unittest.TestCase):
    def testConstructor(self):
        t = TemperatureInfoPayload(20.0, 37.5)
        m = InformationResponseMessage(0xAAAAAAAA, InformationType.USER_TEMPERATURE, t)

        assert m.transaction_id == 0xAAAAAAAA, "transaction_id set incorrectly"
        assert m.information_type == InformationType.USER_TEMPERATURE, \
               "information type set incorrectly"
        assert m.payload == t, "payload set incorrectly"

    def testToBytes(self):
        t = TemperatureInfoPayload(20.0, 37.5)
        m = InformationResponseMessage(0xAAAAAABB, InformationType.USER_TEMPERATURE, t)
        b = m.to_bytes()

        assert b == bytes([0x00, 0x00, 0x00, 0x04, 0xAA, 0xAA, 0xAA, 0xBB, 0x00, 0x00, 0x00,
                           0x01, 0x07, 0xd0, 0x0e, 0xa6]), \
                    "Failed to convert InformationResponseMessage to bytes"
    
    def testFromBytes(self):
        m = Message.from_bytes(bytes([0x00, 0x00, 0x00, 0x04, 0xAA, 0xAA, 0xAA, 0xBB, 0x00, 0x00,
                                      0x00, 0x01, 0x07, 0xd0, 0x0e, 0xa6]))

        assert isinstance(m, InformationResponseMessage), "not parsed to correct message class"
        assert m.transaction_id == 0xAAAAAABB, "transaction id not parsed correctly"
        assert m.information_type == InformationType.USER_TEMPERATURE, \
               "information type parsed incorrectly"
        assert isinstance(m.payload, TemperatureInfoPayload), \
               "payload not parsed to correct message type"
        assert m.payload.ambient_temp == 20.0, "ambient temperature parsed incorrectly"
        assert m.payload.user_temp == 37.5, "user temperature parsed incorrectly"

    def testFromBytesInvalid(self):
        try:
            # Message is one byte too short, otherwise valid
            m = Message.from_bytes(bytes([0x00, 0x00, 0x00, 0x04, 0xAA, 0xAA, 0xAA, 0xBB, 0x00,
                                          0x00, 0x00, 0x01, 0x00, 0x00, 0x00]))
        except MessageException:
            pass
        else:
            fail("expected MessageException")

class DoorStateUpdateMessagedTests(unittest.TestCase):
    def testConstructor(self):
        m = DoorStateUpdateMessage(DoorState.NOT_ALLOWING_ENTRY)

        assert m.state == DoorState.NOT_ALLOWING_ENTRY, "state set incorrectly"

    def testToBytes(self):
        m = DoorStateUpdateMessage(DoorState.NOT_ALLOWING_ENTRY)
        b = m.to_bytes()

        assert b == bytes([0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x02]), \
                    "Failed to convert DoorStateUpdateMessage to bytes"
    
    def testFromBytes(self):
        m = Message.from_bytes(bytes([0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x02]))

        assert isinstance(m, DoorStateUpdateMessage), "not parsed to correct message class"
        assert m.state == DoorState.NOT_ALLOWING_ENTRY, "state not parsed correctly"

    def testFromBytesInvalid(self):
        try:
            # Message has invalid door state
            m = Message.from_bytes(bytes([0x00, 0x00, 0x00, 0x05, 0x12, 0x34, 0x56, 0x78]))
        except MessageException:
            pass
        else:
            fail("expected MessageException")


if __name__ == "__main__":
    unittest.main()

