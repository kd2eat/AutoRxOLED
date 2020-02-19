# AutoRxOLED

Step 0: Set up a source directory and bin directory
   $ mkdir /home/pi/src /home/pi/bin

Step 1: Set up deprecated Adafruit Python library
   $ cd /home/pi/src
   $ git clone https://github.com/adafruit/Adafruit_Python_SSD1306/
   $ cd Adafruit_Python_SSD1306
   $ sudo python -m pip install --upgrade pip setuptools wheel
   $ sudo pip install Adafruit-SSD1306


Step 2: Pull down AutoRxOLED
   $ cd /home/pi/src
   $ git pull https://github.com/kd2eat/AutoRxOLED
   $ cd AutoRxOLED
   $ make install

Step 3: Install OLED module on Pi

Step 4: Set your pythonpath to the autorx directory.
   $ export PYTHONPATH=/home/pi/src/radiosonde_auto_rx/auto_rx

Step 5: Test with "send.py"

Step 6: Add a line to /etc/rc.local to start the module at boot time:
   $ sudo vi /etc/rc.local
	(add)  
        /bin/su --login pi -c /home/pi/bin/runoled.py > /tmp/runoled.log 2>&1 &

