#GPIO pins will control the LEDs
import RPi.GPIO as GPIO
from enum import Enum
#Enumeration with the 3 LED colours we have from the combination of Red and Green
class LEDColour(Enum) :
    RED = 1
    GREEN = 2
    YELLOW = 3
    OFF = 4
#Class that controls the LED
class LED:
    
    #Initalizes and sets the pins
    def __init__(self, red_pin, green_pin):
        self.red_pin = red_pin
        self.green_pin = green_pin
    
        GPIO.setmode(GPIO.BCM)
    
        #GPIO setup will have pin 17 and 18 as outputs controlling red and green
        GPIO.setup(self.red_pin, GPIO.OUT)
        GPIO.setup(self.green_pin, GPIO.OUT)

    #defined method for setting LED colours
    def set_colour(colour):        
        #if the selected colour is red make sure that red pin is on and green pin is off
        if (colour == RED):
            GPIO.output(self.red_pin, True)
            GPIO.output(self.green_pin, False)        
        #if the selected colour is red make sure that red pin is on and green pin is off
        elif (colour == GREEN):
            GPIO.output(self.red_pin, False)
            GPIO.output(self.green_pin, True)
        #if the selected colour is red make sure that red pin is on and green pin is on
        elif (colour == YELLOW):
            GPIO.output(self.red_pin, True)
            GPIO.output(self.green_pin, True)
        else:
            GPIO.output(self.red_pin, False)
            GPIO.output(self.green_pin, False)