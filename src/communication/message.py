#
#   Message format.
#   Samuel Dewan - 2020
#

import struct
from abc import ABC, abstractmethod
from enum import IntEnum

class MessageException(Exception):
    pass

class MessageType(IntEnum):
    ACCESS_REQUEST = 0x1
    ACCESS_RESPONSE = 0x2
    INFORMATION_REQUEST = 0x3
    INFORMATION_RESPONSE = 0x4
    DOOR_STATE_UPDATE = 0x5

class Message(ABC):
    @abstractmethod
    def to_bytes(self):
        return b''

    @classmethod
    @abstractmethod
    def _parse(cls, packet):
        return None

    @classmethod
    def from_bytes(cls, packet):
        if len(packet) < 4:
            raise MessageException(f"Message must be at least 4 bytes long ({len(packet)} bytes "
                                   f"recieved)")
        message_type_val = struct.unpack("!I", packet[0:4])[0]
        try:
            message_type = MessageType(message_type_val)
        except ValueError:
            raise MessageException(f"Invalid message type: {message_type_val}")

        if message_type == MessageType.ACCESS_REQUEST:
            return AccessRequestMessage._parse(packet)
        elif message_type == MessageType.ACCESS_RESPONSE:
            return AccessResponseMessage._parse(packet)
        elif message_type == MessageType.INFORMATION_REQUEST:
            return InformationRequestMessage._parse(packet)
        elif message_type == MessageType.INFORMATION_RESPONSE:
            return InformationResponseMessage._parse(packet)
        elif message_type == MessageType.DOOR_STATE_UPDATE:
            return DoorStateUpdateMessage._parse(packet)
        else:
            raise MessageException(f"Unkown message type: {message_type}")

#
#   Access Request
#

class AccessRequestMessage(Message):
    def __init__(self, transaction_id, badge_id):
        self.transaction_id = transaction_id
        self.badge_id = badge_id

    def to_bytes(self):
        return struct.pack("!II16p", MessageType.ACCESS_REQUEST, self.transaction_id,
                           self.badge_id)

    @classmethod
    def _parse(cls, packet):
        if len(packet) != 24:
            raise MessageException(f"Invalid length for ACCESS_REQUEST message: expected 24, got "
                                   f"{len(packet)}")
        msg_type, tid, bid = struct.unpack("!II16p", packet)
        return cls(tid, bid)

#
#   Access Response
#

class AccessResponseMessage(Message):
    def __init__(self, transaction_id, accepted):
        self.transaction_id = transaction_id
        self.accepted = accepted

    def to_bytes(self):
        accepted = 0 if not self.accepted else 1
        return struct.pack("!III", MessageType.ACCESS_RESPONSE, self.transaction_id, accepted)

    @classmethod
    def _parse(cls, packet):
        if len(packet) != 12:
            raise MessageException(f"Invalid length for ACCESS_RESPONSE message: expected 12, got "
                                   f"{len(packet)}")
        msg_type, tid, accepted = struct.unpack("!III", packet)
        return cls(tid, accepted != 0)

#
#   Information Request
#

class InformationType(IntEnum):
    USER_TEMPERATURE = 0x1

class InformationRequestMessage(Message):
    def __init__(self, transaction_id, information_type):
        self.transaction_id = transaction_id
        self.information_type = information_type

    def to_bytes(self):
        return struct.pack("!III", MessageType.INFORMATION_REQUEST, self.transaction_id,
                           self.information_type)

    @classmethod
    def _parse(cls, packet):
        if len(packet) != 12:
            raise MessageException(f"Invalid length for INFORMATION_REQUEST message: expected 12, "
                                   f"got {len(packet)}")
        msg_type, tid, info_type_val = struct.unpack("!III", packet)
        try:
            info_type = InformationType(info_type_val)
        except ValueError:
            raise MessageException(f"Invalid information type: {info_type_val}")
        else:
            return cls(tid, info_type)

#
#   Information Response
#

class InformationPayload(ABC):
    @abstractmethod
    def to_bytes(self):
        return b''

    @classmethod
    @abstractmethod
    def _parse(cls, payload):
        return None

    @classmethod
    def from_bytes(cls, info_type, payload):
        if info_type == InformationType.USER_TEMPERATURE:
            return TemperatureInfoPayload._parse(payload)
        else:
            raise MessageException(f"Unkown information type: {info_type}")

class TemperatureInfoPayload(InformationPayload):
    def __init__(self, ambient_temp, user_temp):
        self.ambient_temp = ambient_temp
        self.user_temp = user_temp

    def to_bytes(self):
        return struct.pack("!hh", int(self.ambient_temp * 100), int(self.user_temp * 100))

    @classmethod
    def _parse(cls, payload):
        if len(payload) != 4:
            raise MessageException(f"Invalid length for temperature information payload: expected "
                                   f"4, got {len(payload)}")
        ambient_temp, user_temp = struct.unpack("!hh", payload)
        return cls(ambient_temp / 100, user_temp / 100)


class InformationResponseMessage(Message):
    def __init__(self, transaction_id, information_type, payload):
        self.transaction_id = transaction_id
        self.information_type = information_type
        self.payload = payload

    def to_bytes(self):
        head = struct.pack("!III", MessageType.INFORMATION_RESPONSE, self.transaction_id,
                           self.information_type)
        return head + self.payload.to_bytes()

    @classmethod
    def _parse(cls, packet):
        if len(packet) < 12:
            raise MessageException(f"Invalid length for INFORMATION_RESPONSE message: expected at "
                                   f"least 12, got {len(packet)}")
        msg_type, tid, info_type_val = struct.unpack("!III", packet[0:12])
        try:
            info_type = InformationType(info_type_val)
        except ValueError:
            raise MessageException(f"Invalid information type: {info_type_val}")
        else:
            return cls(tid, info_type, InformationPayload.from_bytes(info_type, packet[12:]))

#
#   Door State Update
#

class DoorState(IntEnum):
    ALLOWING_ENTRY = 0x1
    NOT_ALLOWING_ENTRY = 0x2

class DoorStateUpdateMessage(Message):
    def __init__(self, state):
        self.state = state

    def to_bytes(self):
        return struct.pack("!II", MessageType.DOOR_STATE_UPDATE, self.state)

    @classmethod
    def _parse(cls, packet):
        if len(packet) != 8:
            raise MessageException(f"Invalid length for DOOR_STATE_UPADTE message: expected 8, got "
                                   f"{len(packet)}")
        msg_type, state_val = struct.unpack("!II", packet)
        try:
            state = DoorState(state_val)
        except ValueError:
            raise MessageException(f"Invalid door state: {state_val}")
        else:
            return cls(tid, state)

