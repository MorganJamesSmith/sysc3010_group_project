import time
 
import board
import busio
 
import adafruit_vl53l0x

class RangeFinder:
    
    def __init__(self,activate):
        self.activate = activate
        #self.address= address
        # Initialize I2C bus and sensor.
        i2c = busio.I2C(board.SCL, board.SDA)
        vl53 = adafruit_vl53l0x.VL53L0X(i2c)
    def get_range(self):
        if self.activate == True:
            dist = vl53.range
            return dist
