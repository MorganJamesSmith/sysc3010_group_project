#! /usr/bin/env python3
#
# file name: RangeFinder_stub
# Description: RangeFinder replacement code for those lacking hardware
# Author(s): Mario Shebib 
#
import time
import sys
from pathlib import Path
class RangeFinder_stub:
    """
    This class is a stub that imitates the range finder sensor for running the code without the hardware
    """    
    def __init__(self):
        """
        Initializes the class reading a text file to determine the starting range
        """
        try:
            with open("./stub_text/initial_range.txt", "r") as range_file:
                self.range = range_file.read().strip()
        except FileNotFoundError as e:
            print("Could not open testcase files.")
            exit(1)

    def get_range(self):
        """
        By decreasing or increasing the distance by 50 millimeters each time the code runs
        This method imitates the real life actions of a user interacting with the distance sensor.
        """
        distance = int(self.range)
        if distance < 300:
            distance += 20
        elif distance < 320:
            distance = distance
        else:
            distance = distance - 20
        print(distance)
        return distance
if __name__ == "__main__":
    range_finder = RangeFinder_stub()
    range_finder.get_range()
