#
# file name: RangeFinder_stub
# Description: RangeFinder replacement code for those lacking hardware
# Author(s): Mario Shebib 
#

from time import sleep

class RangeFinder_stub:
    """
    This class is a stub that imitates the range finder sensor for running the code without the hardware
    """    
    def __init__(self):
        try:
            self.file = open("./stub_text/initial_range.txt", "r")
        except FileNotFoundError as e:
            print("Could not open test file for range finder.")
            exit(1)

    def get_range(self):
        """
        By decreasing or increasing the distance by 50 millimeters each time the code runs
        This method imitates the real life actions of a user interacting with the distance sensor.
        """
        while True:
            line = self.file.readline().strip()
            if line != '':
                break
            sleep(2)
        return int(line) 

