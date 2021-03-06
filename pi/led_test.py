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
import signal
import sys
import socket
from led import LED

led = None
sock = None
port = 12345

def sig_caught(signal, frame):
    print "Caught signal. The LED status has changed"

def main():
    try:
        # Setup signal handlers
        try:
            signal.signal(signal.SIGALRM, sig_caught)
        except ValueError, ve:
            print "Unable to tie SIGALRM to custom method."

        led = LED()
        device_name = raw_input('Enter a name for the led: ')
        device_desc = raw_input('Enter a description for the led: ')
        led.set_name(device_name)
        led.set_desc(device_desc)

        print "Name: " + led.get_name()
        print "Description: " + led.get_desc()

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
