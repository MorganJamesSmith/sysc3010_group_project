#
#   Message format.
#   Samuel Dewan - 2020
#

import struct
from abc import ABC, abstractmethod
from enum import IntEnum

class MessageException(Exception):
    """ Exception used for any errors related to message marshalling or unmarshalling """

class MessageType(IntEnum):
    """ Enum to associate the possible message types in our protocol with their integer values """
    ACCESS_REQUEST = 0x1
    ACCESS_RESPONSE = 0x2
    INFORMATION_REQUEST = 0x3
    INFORMATION_RESPONSE = 0x4
    DOOR_STATE_UPDATE = 0x5

class Message(ABC):
    """ Abstract class respresents a communication protocol message """

    @abstractmethod
    def to_bytes(self):
        """ Marshal message to a bytes object """

    @classmethod
    @abstractmethod
    def _parse(cls, packet):
        """ Unmarshal message from a bytes object (not ment to be called directly) """

    @classmethod
    def from_bytes(cls, packet):
        """ Unmarshal a bytes object to appropriate message class """
        if len(packet) < 4:
            raise MessageException(f"Message must be at least 4 bytes long ({len(packet)} bytes "
                                   f"recieved)")

        message_type_val = struct.unpack("!I", packet[0:4])[0]
        try:
            message_type = MessageType(message_type_val)
        except ValueError as error:
            raise MessageException(f"Invalid message type: {message_type_val}") from error

        if message_type == MessageType.ACCESS_REQUEST:
            return AccessRequestMessage._parse(packet)
        if message_type == MessageType.ACCESS_RESPONSE:
            return AccessResponseMessage._parse(packet)
        if message_type == MessageType.INFORMATION_REQUEST:
            return InformationRequestMessage._parse(packet)
        if message_type == MessageType.INFORMATION_RESPONSE:
            return InformationResponseMessage._parse(packet)
        if message_type == MessageType.DOOR_STATE_UPDATE:
            return DoorStateUpdateMessage._parse(packet)

        raise MessageException(f"Unkown message type: {message_type}")

#
#   Access Request
#

class AccessRequestMessage(Message):
    """ Representation of message used to start an access request transaction """

    def __init__(self, transaction_id, badge_id):
        self.transaction_id = transaction_id
        self.badge_id = badge_id

    def to_bytes(self):
        return struct.pack("!II16s", MessageType.ACCESS_REQUEST, self.transaction_id,
                           self.badge_id)

    @classmethod
    def _parse(cls, packet):
        if len(packet) != 24:
            raise MessageException(f"Invalid length for ACCESS_REQUEST message: expected 24, got "
                                   f"{len(packet)}")
        _, tid, bid = struct.unpack("!II16s", packet)
        return cls(tid, bid)

    def __str__(self):
        return (f"AccessRequestMessage (tid: {self.transaction_id}, "
                f"badge_id: {''.join('{:X}'.format(i) for i in self.badge_id)})")

#
#   Access Response
#

class AccessResponseMessage(Message):
    """ Representation of message used to close and access response transaction """

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
        _, tid, accepted = struct.unpack("!III", packet)
        return cls(tid, accepted != 0)

    def __str__(self):
        return f"AccessResponseMessage (tid {self.transaction_id}, accepted: {self.accepted})"

#
#   Information Request
#

class InformationType(IntEnum):
    """ Enum to represent possible data types in our message protocol """
    USER_TEMPERATURE = 0x1

class InformationRequestMessage(Message):
    """ Message used by server to ask for additonal information to inform access decision """

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
        _, tid, info_type_val = struct.unpack("!III", packet)
        try:
            info_type = InformationType(info_type_val)
        except ValueError as error:
            raise MessageException(f"Invalid information type: {info_type_val}") from error
        else:
            return cls(tid, info_type)

    def __str__(self):
        return (f"InformationRequestMessage (tid {self.transaction_id}, "
                f"type: {str(self.information_type)})")

#
#   Information Response
#

class InformationPayload(ABC):
    """ Abstract class to represent the payload for an information response message """

    @abstractmethod
    def to_bytes(self):
        """ Marshal payload to a bytes object """

    @classmethod
    @abstractmethod
    def _parse(cls, payload):
        """ Unmarshal payload from a bytes object """

    @classmethod
    def from_bytes(cls, info_type, payload):
        """ Unmarshal payload from a bytes object to the correct class """
        if info_type == InformationType.USER_TEMPERATURE:
            return TemperatureInfoPayload._parse(payload)
        
        raise MessageException(f"Unkown information type: {info_type}")

class TemperatureInfoPayload(InformationPayload):
    """ Information response payload that contains information about ambient and user
        temperatures """

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

    def __str__(self):
        return (f"[TemperatureInfoPayload (ambient temp: {self.ambient_temp}, "
                f"user temp: {self.user_temp})]")


class InformationResponseMessage(Message):
    """ Message used by door node to return requested information to control server """

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
        _, tid, info_type_val = struct.unpack("!III", packet[0:12])
        try:
            info_type = InformationType(info_type_val)
        except ValueError as error:
            raise MessageException(f"Invalid information type: {info_type_val}") from error
        else:
            return cls(tid, info_type, InformationPayload.from_bytes(info_type, packet[12:]))

    def __str__(self):
        return (f"InformationResponseMessage (tid: {self.transaction_id}, "
                f"type: {str(self.information_type)}, payload: {self.payload})")

#
#   Door State Update
#

class DoorState(IntEnum):
    """ Possible states for door node, used by door node to select LED colour """
    ALLOWING_ENTRY = 0x1
    NOT_ALLOWING_ENTRY = 0x2

class DoorStateUpdateMessage(Message):
    """ Message send by server to change state of door node """

    def __init__(self, state):
        self.state = state

    def to_bytes(self):
        return struct.pack("!II", MessageType.DOOR_STATE_UPDATE, self.state)

    @classmethod
    def _parse(cls, packet):
        if len(packet) != 8:
            raise MessageException(f"Invalid length for DOOR_STATE_UPADTE message: expected 8, got "
                                   f"{len(packet)}")
        _, state_val = struct.unpack("!II", packet)
        try:
            state = DoorState(state_val)
        except ValueError as error:
            raise MessageException(f"Invalid door state: {state_val}") from error
        else:
            return cls(state)

    def __str__(self):
        return f"DoorStateUpdateMessage (state: {str(self.state)}) "
