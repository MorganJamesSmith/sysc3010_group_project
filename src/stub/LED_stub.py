#GPIO pins will control the LEDs
from enum import Enum
#Enumeration with the 3 LED colours we have from the combination of Red and Green
class LEDColour(Enum) :
    RED = 1
    GREEN = 2
    YELLOW = 3
    OFF = 4
#Class that controls the LED
class LED_stub:
    
    #Initalizes the class and creates the internal colour
    #variable
    def __init__(self):
        self.colour = LEDColour(1)

    #defined method for setting LED colours
    def set_colour(self, colour):
        self.colour = colour
        print(self.colour)