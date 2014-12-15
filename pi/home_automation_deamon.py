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
import signal
import json
from led import LED

num_devices = 0
led = None
sock = None
port = 12345

def cleanup():
    global led
    global sock
    if led is not None:
        led.cleanup()
    if sock is not None:
        sock.close

def status_change(signal, frame):
    global sock
    global led
    if sock is not None and led is not None:
        sock.sendall(update_status(led))

def interpret_response(reply):
    if reply['result'] == True:
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

    return update_status(led)

def update_status(led):
    return json.dumps({'update':{'device_name':led.get_name(), \
    'state':led.get_state()}})

def main():
    try:
        global led
        global sock
        # Setup Arparse
        parser = argparse.ArgumentParser(description='Home automation daemon', \
            prefix_chars='-')

        parser.add_argument('-b', help="This is the IP address of the home \
            automation server", required=True)
        parser.add_argument('-n', help="Unique identifier for this Pi", \
        required=True)

        # Setup signal handlers
        try:
            signal.signal(signal.SIGALRM, status_change)
        except ValueError, ve:
            print "Unable to tie SIGALRM to custom method."

        args = parser.parse_args()

        host = args.b
        name = args.n

        if host is None:
            print("Please supply a host")
            sys.exit()
        if name is None:
            print("Please supply a name")
            sys.exit()

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

        sock.setblocking(0)
        sock.settimeout(5)

        try:
            while True:
                data = None
                try:
                    data = sock.recv(4096)
                    result = execute_command(json.loads(data),led)
                    sock.sendall(result)
                except socket.timeout, t:
                    print "no data received"

        except KeyboardInterrupt:
            cleanup()
    except Exception, e:
        # Unexpected error
        print "Unexpected error occured: " + e.message
        cleanup()

if __name__ == '__main__':
    main()
