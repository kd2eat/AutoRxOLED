#!/usr/bin/env python
#
#   radiosonde_auto_rx - 'Horus UDP' Receiver Example
#
#   Copyright (C) 2019  Mark Jessop <vk5qi@rfhead.net>
#   Released under GNU GPL v3 or later
#
#   This code provides an example of how the Horus UDP packets emitted by auto_rx can be received
#   using Python. Horus UDP packets are simply JSON blobs, which all must at the very least contain a 'type' field, which
#   (as the name suggests) indicates the packet type. auto_rx emits packets of type 'PAYLOAD_SUMMARY', which contain a summary
#   of payload telemetry information (latitude, longitude, altitude, callsign, etc...)
#
#   Output of Horus UDP packets is enabled using the payload_summary_enabled option in the config file.
#   See here for information: https://github.com/projecthorus/radiosonde_auto_rx/wiki/Configuration-Settings#payload-summary-output
#   By default these messages are emitted on port 55672, but this can be changed.
#
#   In this example I use a UDPListener object (ripped from the horus_utils repository) to listen for UDP packets in a thread,
#   and pass packets that have a 'PAYLOAD_SUMMARY' type field to a callback, where they are printed.
#   

import datetime
import json
import pprint
import socket
import time
import traceback
from threading import Thread

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library


oled_line1 = ""
oled_line2 = ""
oled_line3 = ""
oled_line4 = ""
oled_line5 = ""
oled_line6 = ""
oled_shutdown = -1
SHUTDOWN_PIN = 22		# BCM pin 22 == Board pin 15


class UDPListener(object):
    ''' UDP Broadcast Packet Listener 
    Listens for Horus UDP broadcast packets, and passes them onto a callback function
    '''

    def __init__(self,
        callback=None,
        summary_callback = None,
        gps_callback = None,
        port=55673):

        self.udp_port = port
        self.callback = callback

        self.listener_thread = None
        self.s = None
        self.udp_listener_running = False


    def handle_udp_packet(self, packet):
        ''' Process a received UDP packet '''
        try:
            # The packet should contain a JSON blob. Attempt to parse it in.
            print "Packet received"
            packet_dict = json.loads(packet)

            # This example only passes on Payload Summary packets, which have the type 'PAYLOAD_SUMMARY'
            # For more information on other packet types that are used, refer to:
            # https://github.com/projecthorus/horus_utils/wiki/5.-UDP-Broadcast-Messages
            if packet_dict['type'] == 'PAYLOAD_SUMMARY':
                if self.callback is not None:
                    self.callback(packet_dict)

        except Exception as e:
            print("Could not parse packet: %s" % str(e))
            traceback.print_exc()


    def udp_rx_thread(self):
        ''' Listen for Broadcast UDP packets '''

        self.s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.s.settimeout(1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            pass
        self.s.bind(('',self.udp_port))
        print("Started UDP Listener Thread on port %d." % self.udp_port)
        self.udp_listener_running = True

        # Loop and continue to receive UDP packets.
        while self.udp_listener_running:
            try:
                # Block until a packet is received, or we timeout.
                m = self.s.recvfrom(1024)
            except socket.timeout:
                # Timeout! Continue around the loop...
                m = None
            except:
                # If we don't timeout then something has broken with the socket.
                traceback.print_exc()
            
            # If we hae packet data, handle it.
            if m != None:
                self.handle_udp_packet(m[0])
        
        print("Closing UDP Listener")
        self.s.close()


    def start(self):
        if self.listener_thread is None:
            self.listener_thread = Thread(target=self.udp_rx_thread)
            self.listener_thread.start()


    def close(self):
        self.udp_listener_running = False
        self.listener_thread.join()




def handle_payload_summary(packet):
    global oled_line1
    global oled_line2
    global oled_line3
    global oled_line4
    global oled_line5
    global oled_line6

    ''' Handle a 'Payload Summary' UDP broadcast message, supplied as a dict. '''

    # Pretty-print the contents of the supplied dictionary.
    pprint.pprint(packet)

    # Extract the fields that should always be provided.
    _callsign = packet['callsign']
    _lat = packet['latitude']
    _lon = packet['longitude']
    _alt = packet['altitude']
    _time = packet['time']

    # The comment field isn't always provided.
    if 'comment' in packet:
        _comment = packet['comment']
    else:
        _comment = "No Comment Provided"

    # Do nothing with these values in this example...
    oled_line1 = oled_line2
    oled_line2 = oled_line3
    oled_line3 = oled_line4
    oled_line4 = oled_line5
    oled_line5 = oled_line6
    oled_line6 = _time + ' ' + str(_alt)


if __name__ == '__main__':

    # Initialize GPIO for shutdown pin
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BCM) # Use physical pin numbering
    GPIO.setup(SHUTDOWN_PIN , GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 15 to be an input pin and pull down initially

    # Raspberry Pi pin configuration:
    RST = None     # on the PiOLED this pin isnt used
    # Note the following are only used with SPI:
    DC = 23
    SPI_PORT = 0
    SPI_DEVICE = 0
    # 128x64 display with hardware I2C:
    disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
    # Initialize library.
    disp.begin()
    
    # Clear display.
    disp.clear()
    disp.display()
    
    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    
    # Draw some shapes.
    # First define some constants to allow easy resizing of shapes.
    padding = -2
    top = padding
    bottom = height-padding
    # Move left to right keeping track of the current x position for drawing shapes.
    x = 0

    # Load default font.
    font = ImageFont.load_default()
    draw.text((x, top),       "Booting",  font=font, fill=255)
    # Display image.
    disp.image(image)
    disp.display()
################################################################################################    
    # Instantiate the UDP listener.
    udp_rx = UDPListener(
        port=55673,
        callback = handle_payload_summary
        )
    # and start it
    udp_rx.start()

    # From here, everything happens in the callback function above.
    try:
        while True:

            # Draw a black filled box to clear the image.
            draw.rectangle((0,0,width,height), outline=0, fill=0)
        
            # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
            cmd = "hostname -I | cut -d\' \' -f1"
            IP = subprocess.check_output(cmd, shell = True )
        
            cmd = "/sbin/iwgetid"
            try:
               SSID = subprocess.check_output(cmd, shell = True )
            except:
               SSID = '"None"'
            SSID = SSID[SSID.find('"')+1:SSID.rfind('"')]

            # Shutdown Pin logic
            if GPIO.input(SHUTDOWN_PIN) != GPIO.HIGH:
               oled_shutdown = -1			# Button is not pressed, or was released.  No shutdown.
            else:
               print("Button pressed")
               # Button is pressed.  Initiate countdown.
               if (oled_shutdown == -1):		# When first pressed, set counter to 5 seconds
                  oled_shutdown = 5			# 5 Seconds to shut down
               if (oled_shutdown == 0):		# It's time to shut down completely
                  # Draw a black filled box to clear the image.
                  draw.rectangle((0,0,width,height), outline=0, fill=0)
                  # Display image.
                  disp.image(image)
                  disp.display()
                  time.sleep(1)		# Wait for display to update
                  cmd = "/sbin/shutdown -h now"
                  ignored = subprocess.check_output(cmd, shell = True )
               else:
                  oled_shutdown = oled_shutdown - 1	# Subtract 1 second for next time 'round
                  oled_line1 = oled_line2
                  oled_line2 = oled_line3
                  oled_line3 = oled_line4
                  oled_line4 = oled_line5
                  oled_line5 = oled_line6
                  oled_line6 = "SHUTDOWN"
            
            # Write two lines of text.
        
            draw.text((x, top),       "IP: " + str(IP),  font=font, fill=255)
            draw.text((x, top+8),     "SSID: " + str(SSID[0:10]), font=font, fill=255)
            draw.text((x, top+16),    oled_line1,  font=font, fill=255)
            draw.text((x, top+24),    oled_line2,  font=font, fill=255)
            draw.text((x, top+32),    oled_line3,  font=font, fill=255)
            draw.text((x, top+40),    oled_line4,  font=font, fill=255)
            draw.text((x, top+48),    oled_line5,  font=font, fill=255)
            draw.text((x, top+56),    oled_line6,  font=font, fill=255)
        
            # Display image.
            disp.image(image)
            disp.display()

            time.sleep(1)
    # Catch CTRL+C nicely.
    except KeyboardInterrupt:
        # Close UDP listener.
        udp_rx.close()
        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        # Display image.
        disp.image(image)
        disp.display()
        print("Closing.")
