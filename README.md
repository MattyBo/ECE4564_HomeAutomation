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

Install Dependencies to Run Server:
-----------------------------------
The server requires certain Python packages to be installed, so assuming you are on
a **Debian** Linux Distribution such as **Ubuntu**, run the commands in the command line below:
```
sudo apt-get install python-twisted
sudo apt-get install python-pip
sudo pip install --no-use-wheel --upgrade distribute
sudo pip install autobahn[twisted]
sudo apt-get install sqlite3 libsqlite3-dev
```

Create the Database:
--------------------
After running the commands above, **SQLITE** should be installed. Choose a directory to make a database.
Then run the commands below:
```
sqlite3 database_file_name
create table pi(name TEXT PRIMARY KEY, description TEXT, status INTEGER)
.exit
```
**database_file_name** can be any name you want it to be. You will need to remember the path and file name
of the database. The combined path and name of the file will become the **database_location** argument for the
server which is explained in the next section.

How to run the home_auto_server:
--------------------------------
Inside the **server** folder is the actual server. To run it use the command below:
```
sudo ./home_auto_server.py database_location web_page_location websocket_host
```
* The **database_location** is where your database file is located as chosen above e.g. /home/ubuntu/home_auto.db
* The **web_page_location** is where the web page files are stored (the root) e.g. /home/ubuntu/Web_Page
* The **websocket_host** is a websocket URL (port 9998) where the web pages will connect to your server e.g. ws://localhost:9998

Use the **-h** option to get help from the command line.

How to use the web page:
------------------------
After the server is up and running, the web page can be accessed by typing in the URL of the computer where you are running your script, or through localhost at port 8000.
To access the page from localhost for example type in the following below into a browser:
```
http://localhost:8000
```
To properly configure the page, there is one line of javascript must be changed. In the **index.html** file inside the **Web_Page** folder, line **83** which is show below:
```
var ws = new WebSocket("ws://54.174.26.73:9998")
```
Must be changed so that the value inside the parenthesis is equal to **websocket_host**, so the new line should be:
```
var ws = new WebSocket("websocket_host")
```
