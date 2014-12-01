#-------------------------------------------------------------------------------
# Name:        led_manual_test.py
# Purpose:     A simple module to test the LED class.
#
# Author:      Matt Bollinger
#
# Created:     2014-11-29
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import argparse
import time
import sys
import socket
from led import LED

led = None
sock = None
port = 12345

def main():
    try:

        led = LED()

        try:
            while True:
                command = raw_input("\"on\" to turn the light on. \"off\" to turn the light off. \"exit\" to quit:")
                if command == "on":
                    led.turn_on()
                elif command == "off":
                    led.turn_off()
                elif command == "exit":
                    led.cleanup()
                    sys.exit()
                else:
                    print "Please enter a valid command."
        except KeyboardInterrupt:
            led.cleanup()
            print("closing")
    except Exception, e:
        # Unexpected error
        print "Unexpected error occured: " + e.message
        if led is not None:
            led.cleanup()

if __name__ == '__main__':
    main()
