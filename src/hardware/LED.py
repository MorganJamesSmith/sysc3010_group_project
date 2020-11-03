from enum import Enum
#Enumeration with the 3 LED colours we have from the combination of Red and Green
class LEDColour(Enum) :
    RED = 1
    GREEN = 2
    YELLOW = 3
    OFF = 4
#Class that controls the LED
class LED 
    
    #GPIO pins will control the LEDs
    import RPi.GPIO as GPIO

    red_pin_num = 17
    green_pin =_ 18
    
    GPIO.setmode(GPIO.BCM)
    
    #GPIO setup will have pin 17 and 18 as outputs controlling red and green
    GPIO.setup(red_pin, GPIO.OUT)
    GPIO.setup(green_pin, GPIO.OUT)

    #defined method for setting LED colours
    def set_colour(LEDColour colour)
        #if the selected colour is red make sure that red pin is on and green pin is off
        if (colour == RED)
            GPIO.output(red_pin, True)
            GPIO.output(green_pin, False)        
        #if the selected colour is red make sure that red pin is on and green pin is off
        elif (colour == GREEN)
            GPIO.output(red_pin, False)
            GPIO.output(green_pin, True)
        #if the selected colour is red make sure that red pin is on and green pin is on
        elif (colour == YELLOW)
            GPIO.output(red_pin, True)
            GPIO.output(green_pin, True)
        else
            GPIO.output(red_pin, False)
            GPIO.output(green_pin, False)
        
