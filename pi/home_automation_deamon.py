#-------------------------------------------------------------------------------
# Name:        home_auto_daemon.py
# Purpose:     This is the process that connects any appliances to the home
# automation server. It creates a socket connection the server and passes all
# information in JSON format. Contains a list of appliances connected to the Pi.
#
# Author:      Matt Bollinger
#
# Created:     2014-11-24
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import argparse
import time
import sys
import socket
import json
from led import LED

num_devices = 0
led = None
sock = None
port = 12345

def cleanup():
    if led is not None:
        led.cleanup()
    if sock is not None:
        sock.close

def interpret_response(reply):
    if reply['result'] == 'True':
        return True
    else:
        return False

def format_registration_message(name, led):
    return json.dumps({'id':name, 'devices':{led.get_name():\
        {'description':led.get_desc(), 'state':led.get_state()}}})

def execute_command(command,led):
    result = True
    message = "All good"
    if command['device_name'] == led.get_name():
        if command['state']:
            led.turn_on()
        else:
            led.turn_off()
    else:
        result = False
        message = "I do not have a device named: " + command['device_name']
        print message

##    return json.dumps({'result':result,'message':message})
        return json.dumps({'update':{'device_name':led.get_name(), \
        'state':led.get_state()}})

def main():
    try:
        # Setup Arparse
        parser = argparse.ArgumentParser(description='Home automation daemon', \
            prefix_chars='-')

        parser.add_argument('-b', help="This is the IP address of the home \
            automation server", required=True)
        parser.add_argument('-n', help="Unique identifier for this Pi", \
        required=True)
##        parser.add_argument('-k', help="The key used to authenticate with the home \
##        automation server", required=True)

        args = parser.parse_args()

        host = args.b
        name = args.n
##        key = args.k

        if host is None:
            print("Please supply a host")
            sys.exit()
        if name is None:
            print("Please supply a name")
            sys.exit()
##        if key is None:
##            print("Please supply a key")
##            sys.exit()

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            print "Connected to host at " + host
        except socket.error, se:
            print "Problem connecting to host " + se.message
            sys.exit()

        num_devices = raw_input("Enter the number of devices on this pi \
        (right now this will be 1 no matter what you put):\n")
        num_devices = 1
        device_name = raw_input('Enter a name for device' + str(num_devices) + \
        ':')
        device_desc = raw_input('Enter a description for device' \
        + str(num_devices) + ':')

        led = LED()
        led.set_name(device_name)
        led.set_desc(device_desc)

        sock.sendall(format_registration_message(name,led))
        reply = sock.recv(4096)
        if interpret_response(json.loads(reply)) == False:
            print "The server already has a pi with the name " + name + \
            ". Please remove the pi from the server or try a enter a new name."
            cleanup()
            sys.exit()

        try:
            while True:
                data = sock.recv(4096)
                reply = execute_command(json.loads(data),led)
                sock.sendall(reply)
        except KeyboardInterrupt:
            led.cleanup()
            sock.close()
            cleanup()
    except Exception, e:
        # Unexpected error
        print "Unexpected error occured: " + e.message
        cleanup()

if __name__ == '__main__':
    main()
