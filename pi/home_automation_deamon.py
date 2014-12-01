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
from led import LED

led = None
sock = None
port = 12345

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
            sock.connect(host, port)
            print "Connected to host at " + host
        except socket.error, se:
            print "Problem connecting to host " + se.message
            print "Closing"
            sys.exit()

        led = LED()

        try:
            while True:
                time.sleep(100)
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
