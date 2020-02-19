# AutoRxOLED

Step 0: Set up a source directory and bin directory
   $ mkdir /home/pi/src /home/pi/bin

Step 1: Set up deprecated Adafruit Python library
   $ cd /home/pi/src
   $ git pull https://github.com/adafruit/Adafruit_Python_SSD1306/
   $ cd Adafruit_Python_SSD1306
   $ ./setup.py

Step 2: Pull down AutoRxOLED
   $ cd /home/pi/src
   $ git pull https://github.com/kd2eat/AutoRxOLED
   $ cd AutoRxOLED
   $ make install

Step 3: Install OLED module on Pi

Step 4: Test with "send.py"
