ECE4564_HomeAutomation
======================

How to setup your pi:
---------------------
Example circuit diagrams and pictures are provided to show how to setup the LED
circuit. Currently, the code is setup for only one LED (connected to pin 25) to
work. Future development will allow for more than one device to be hooked up to
a single pi.

How to run the home_automation_deamon:
-------------------------
To run the client deamon you need to know the IP address of the Home Automation
server and a unique name for your pi. Once you have both run the deamon with 
the following command:

sudo python home_automation_deamon.py -b [ IP address ] -n [ Unique name ]

After the deamon has successfully connected to the server, follow the prompts
to complete registering your pi with the home automation server.
