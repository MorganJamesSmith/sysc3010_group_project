import smbus
import struct

class MLX90614:

    def __init__(self, bus, address = 0x5a):
        self.bus = bus
        self.address = address
    
    def get_ambient_temp(self):
        data = self.bus.read_i2c_block_data(self.address, 0x6, 3)
        ta_val, pec = struct.unpack("<HB", bytes(data))
        if ta_val & 0x8000:
            # Error flag set
            return None
        return (ta_val * 0.02) - 273.15

    def get_ir_temp(self):
        tobj1_data = self.bus.read_i2c_block_data(self.address, 0x7, 3)
        tobj1_val, pec = struct.unpack("<HB", bytes(tobj1_data))
        if tobj1_val & 0x8000:
            # Error flag set
            return None
        return (tobj1_val * 0.02) - 273.15
        
