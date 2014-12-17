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
A Twisted Server that handles socket connections to Raspberry Pi's
and WebSockets connected to web clients connected via web page.
"""

__author__ = 'James Tobat'

import csv
import json
import sys
import sqlite3 as lite
import argparse
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory
from twisted.web import http, resource
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory

# Sets up locations/URLs needed for server to operate
parser = argparse.ArgumentParser(description='Home Automation Server')
parser.add_argument('Database_Location', type=str, help='Where database is stored')
parser.add_argument('Web_Page_Directory', type=str, help='Where web page files are stored')
parser.add_argument('WebSocket_Address', type=str, help='Where WebSocket server will be set up')

# Constants needed for server to operate
args = vars(parser.parse_args())
path = args['Web_Page_Directory'] # Directory of web page to serve
# Index locations of database, needed to parse table
name_index = 0
desc_index = 1
stat_index = 2
websocket = WebSocketServerFactory(args['WebSocket_Address'], debug = False) # WebSocket server setup
clients = [] # List used to hold websocket clients
pi_system = {} # Keeps track of connected Pis/devices
socket_clients = {} # Keeps track of Pi's connected to server, used to send messages back
con = None
cur = None
database = args['Database_Location']

# Tries to load stored Pi information in database
try:
  con = lite.connect(database)
  cur = con.cursor()

except lite.Error, e:
  
  if con:
    con.rollback()

  print "Database Error %s:" % e.args[0]
  sys.exit(1)

# Generates a json message to be sent either to a websocket or pi client
# name = name of Raspberry Pi
# devices = list of devices along with their status
# new = true if a new Raspberry Pi, false if just an update
# state = current state of Pi, 0 if inactive, 1 if active
# pi_update = true if an existing pi is being updated
def pi_status(name, devices, new, state=None, pi_update=False):
  new_message = {}
  status = None
  if new:
    status = 'new'
  else:
    status = 'update'

  new_message[status] = {}
  new_message[status][name] = {}

  if pi_update or new:
    new_message[status] = {}
    new_message[status][name] = {}
    new_message[status][name]['devices'] = devices
    new_message[status][name]['status'] = state
  else:
    new_message[status][name]['device_name'] = devices
    new_message[status][name]['state'] = state
    
  return json.dumps(new_message)

# Send a message to all websocket clients.
# Message must be in the correct format first.
def broadcast(message):
  global clients
  if len(clients) > 0:
    for c in clients:
      c.sendMessage(message)
  return

# Creates standard response message.
# result = true if message recieved/responded to
# was correct.
# message = error message if result is false.
def result(result, message=""):
  result_message = {}
  result_message['result'] = result
  result_message['message'] = message
  
  return json.dumps(result_message)

# Creates a standard command message.
# name = name of pi
# state = state of light, 1 = on, 0 = off
def command(name, state):
    cmd = {}
    cmd['device_name'] = name
    cmd['state'] = state
    
    return json.dumps(cmd)

# WebSocket Protocol
class MyServerProtocol(WebSocketServerProtocol):
   # Appends client information to list when
   # a connection is made
   def onConnect(self, request):
      global clients
      clients.append(self)
      print("Client connecting: {0}".format(request.peer))

   # Sends all Pi information to website when the web page first connects
   def onOpen(self):
      print("WebSocket connection open.")
      print pi_system
      self.sendMessage(json.dumps(pi_system))
  
   # Handles messages coming from web page clients
   def onMessage(self, payload, isBinary):
      if isBinary:
         print("Binary message received: {0} bytes".format(len(payload)))
      else:
         text = payload.decode('utf8')
         command_text = json.loads(text)
         if "id" in command_text and \
            "device_name" in command_text and \
            "state" in command_text:
           cmd = command(command_text['device_name'],command_text['state'])
           socket_clients[command_text['id']].write(cmd)
         else:
            respond = result(False,"Incorrect command format.")
            self.sendMessage(respond)

      print("Text message received: {0}".format(payload.decode('utf8')))

      ## echo back message verbatim
      #self.sendMessage(payload, isBinary)

   # Removes client from list when connection is closed
   def onClose(self, wasClean, code, reason):
      global clients
      for c in clients:
        if c == self:
          clients.remove(c)
          #print "client removed"
      print("WebSocket connection closed: {0}".format(reason))

# Handles connects from Raspberry Pis.
# A custom TCP socket protocol.
class PiHandler(Protocol):
    def __init__(self):
        self.first = True
        self.name = None
    """
    def connectionMade(self):
        global con
        con.execute("select name from pi")
        rows = con.fetchall()
        print rows
       # self.transport.write("An apple a day keeps the doctor away\r\n") 
        #self.transport.loseConnection()
    """
    # Deals with Pi disconnection
    def connectionLost(self, reason):
        #self.factory.numProtocols = self.factory.numProtocols - 1
        print "connect lost"
        print self.name
        pi_system[self.name]['status'] = 0
        pi_system[self.name]['devices'] = {}
        update = pi_status(self.name, {}, False, 0, True)
        print update
        broadcast(update)

    # Deals with messages sent from Pis
    def dataReceived(self, data):
        global pi_system
        pi_data = json.loads(data)
        # Sends a response to a Pi's attempt register.
        # Sends an error if an active Pi has the name
        # that the current pi is trying to register with.
        if self.first:
          #con.execute("select name from pi")
          #rows = con.fetchall()

          if "id" in pi_data:
            pi_name = pi_data['id']
            update = False
            new = False
            if pi_name in pi_system:
              if pi_system[pi_name]['status'] == 0:
                 update = True
              else:
                response = result(False, "id")
                self.transport.write(response)
            else:
              global cur
              pi_system[pi_name] = {}
              pi_system[pi_name]['devices'] = pi_data['devices']
              sql = 'INSERT INTO pi VALUES("%s", "", 0)' % pi_name
              print sql
              cur.execute(sql)
              con.commit()
              new = True

            if update or new:
              self.first = False
              self.name = pi_name
              socket_clients[self.name] = self.transport
              pi_system[pi_name]['status'] = 1
              pi_system[pi_name]['devices'] = pi_data['devices']
              pi_message = None
              if new:
                pi_message = pi_status(pi_name, pi_data['devices'], True, 1)
              else:
                pi_message = pi_status(pi_name, pi_data['devices'], False, 1, True)
  
              broadcast(pi_message)
              response = result(True)
              self.transport.write(response) 
        else:
          if "update" in pi_data:
            valid_data = True
            device_name = None
            state = None
   
            if "device_name" in pi_data['update']:
              device_name = pi_data['update']['device_name']
            
            if "state" in pi_data['update']:
              state = pi_data['update']['state']
            
            response = None
            if state == None or device_name == None:
              response = result(False, 'Incorrect update format')
            else:
              pi_system[self.name]['devices'][device_name]['state'] = state
              pi_message = pi_status(self.name, device_name, False, state)
              broadcast(pi_message)
              response = result(True)
          
          if "result" in pi_data:
            print pi_data
        

class PiHandlerFactory(Factory):
    def buildProtocol(self, addr):
        return PiHandler()

cur.execute("select * from pi")

rows = cur.fetchall()
for row in rows:
  name = row[name_index]
  pi_system[name] = {}
  pi_system[name]['devices'] = {}
  pi_system[name]['status'] = row[stat_index]

web_files = File(path)
factory = Site(web_files)
 
websocket.protocol = MyServerProtocol
reactor.listenTCP(9998, websocket)
reactor.listenTCP(8000, factory)
# reactor.listenTCP(8000, TownLookupServer())
reactor.listenTCP(12345, PiHandlerFactory())
# Start Twisted's event loop
reactor.run()
