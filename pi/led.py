#-------------------------------------------------------------------------------
# Name:        led.py
# Purpose:     This class represents a LED/Switch circuit connected to the Pi
# via the GPIO pins.
#
# Author:      Matt Bollinger
#
# Created:     2014-11-24
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import RPi.GPIO as GPIO
import signal
class LED(object):

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        # Pin 23 accepts the switch as input
        GPIO.setup(23,GPIO.IN)
        # Pin 25 drives the LED
        GPIO.setup(25,GPIO.OUT)
        # Add callback
        GPIO.add_event_detect(23, GPIO.BOTH, callback=self.led_callback, \
            bouncetime=200)

        # Let's start with the light on
        self.state = 1
        GPIO.output(25,True)

    def led_callback(self,channel):
        if self.state:
            self.turn_off()
        else:
            self.turn_on()
        signal.alarm(1)

    def turn_on(self):
        self.state = 1
        GPIO.output(25,True)
        print("turning light on")

    def turn_off(self):
        self.state= 0
        GPIO.output(25,False)
        print("turning light off")

    def set_name(self,name):
        self.name = name

    def get_name(self):
        return self.name

    def set_desc(self,desc):
        self.desc = desc

    def get_desc(self):
        return self.desc

    def get_state(self):
        return self.state

    def cleanup(self):
        GPIO.cleanup()

