#!/usr/bin/env python
#
# Copyright 2014 Virginia Polytechnic Institute and State University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
ECE 4564
test_client.py

A simple client that simulates the raspberry pi client.
"""

__author__ = 'James Tobat'

import socket
import json

ex = {}

ex['id'] = "test pi"
ex['devices'] = {}

dev1 = {}
dev1['description'] = "light"
dev1['state'] = 0


dev2 = {}
dev2['description'] = "light"
dev2['state'] = 1

ex['devices']['light1'] = dev1
ex['devices']['light2'] = dev2

update = {}
update['update'] = {}
update['update']['device_name'] = 'kevin'
update['update']['state'] = 1

update1 = {}
update1['update'] = {}
update1['update']['device_name'] = 'devin'
update1['update']['state'] = 1

sock = None
# Create Socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect(("54.174.26.73", 12345))
   
    sent_bytes = 0
    request_buffer = json.dumps(ex)
    print request_buffer

    while sent_bytes < len(request_buffer):
        sent_bytes += sock.send(request_buffer[sent_bytes:])

    reply = sock.recv(4096)
    print reply
    while True:
      reply = sock.recv(4096)
      print reply

      cmd = json.loads(reply);
      update['update']['device_name'] = cmd['device_name']
      update['update']['state'] = cmd['state']
      sent_bytes = 0
      request_buffer = json.dumps(update)
      print request_buffer

      while sent_bytes < len(request_buffer):
        sent_bytes += sock.send(request_buffer[sent_bytes:])

    """
    sent_bytes = 0
    request_buffer = json.dumps(update)
    print request_buffer

    while sent_bytes < len(request_buffer):
        sent_bytes += sock.send(request_buffer[sent_bytes:])

    reply = sock.recv(4096)
    print reply

    sent_bytes = 0
    request_buffer = json.dumps(update1)
    print request_buffer

    while sent_bytes < len(request_buffer):
        sent_bytes += sock.send(request_buffer[sent_bytes:])

    reply = sock.recv(4096)
    print reply
    
    while True:
      sent_bytes = 0
      request_buffer = raw_input()

      while sent_bytes < len(request_buffer):
        sent_bytes += sock.send(request_buffer[sent_bytes:])
      reply = sock.recv(4096)
      print reply
    """
except Exception, local_exception:
    print "Local error: " + local_exception.message

except KeyboardInterrupt:
    sock.close()
