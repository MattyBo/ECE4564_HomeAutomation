ECE4564_HomeAutomation
======================
Introduction:
-------------
This project allows the control of an LED on multiple Raspberry Pis. 
The project includes a server to handle communication between the Pis and
the web page clients. The project also includes a web page along with all
needed scripts and images to run the page.

Structure of Repository:
------------------------
* **pi**: contains all code needed for the Raspberry Pi
* **server**: contains all code needed for the home automation server
* **Web_Page**: contains all the html/scripts/images for the web page
* **BrendanStartWebpage**: contains practice/starter code for web page

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

How to run the home_auto_server:
--------------------------------
Inside the **server** folder is the actual server. To run it use the command below:
```
sudo ./home_auto_server.py database_location web_page_location websocket_host
```
* The **database_location** is where your database file is located e.g. /home/ubuntu/home_auto.db
* The **web_page_location** is where the web page files are stored (the root) e.g. /home/ubuntu/Web_Page
* The **websocket_host** is a websocket URL (port 9998) where the web pages will connect to your server e.g. ws://localhost:9998
