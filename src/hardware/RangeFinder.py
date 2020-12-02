#! /usr/bin/env python3

#
# file name: tof_code_v1
# Description: RangeFinder functional code
# Author(s): Sunjeevani Pujari 
#
import time
 
import board
import busio
 
import adafruit_vl53l0x

class RangeFinder:
    
    def __init__(self):
        #self.address= address
        # Initialize I2C bus and sensor.
        i2c = busio.I2C(board.SCL, board.SDA)
        self.vl53 = adafruit_vl53l0x.VL53L0X(i2c)

    def get_range(self):
        return self.vl53.range
