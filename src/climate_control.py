#!/usr/bin/env python3
# Copyright (c) 2017 Adafruit Industries,
# Copyright (c) 2018 Pekko Metsä
# Author: Tony DiCola, James DeVito, Pekko Metsä

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import configparser
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import time
import pigpio
from datetime import datetime
import sys
sys.path.append('lib')
import DHT22

configfile = 'terrarium.conf'
cfg = configparser.ConfigParser()
cfg.read(configfile)

debug     = bool( cfg.get('debug', 'debug'     ))
dhtpin    = int(  cfg.get('input', 'dhtpin'    ))
heatpin   = int(  cfg.get('output', 'heat'     ))
humpin    = int(  cfg.get('output', 'humidity' ))
humilimit = float(cfg.get('climate', 'humidity'))
heatlimit = float(cfg.get('climate', 'heat'    ))

# DHT reader config
INTERVAL = 3.0  # 2 seconds or less will eventually hang the DHT22
p = pigpio.pi()
#sensor = DHT22.sensor(p, dhtpin, LED=None, power=8)
sensor = DHT22.sensor(p, dhtpin, LED=None)

# Raspberry Pi pin configuration:
RST = 24

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Geometry
width  = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Define some constants to allow easy resizing of shapes.
top = -2
# Move left to right keeping track of the current x position for drawing
# shapes.
x = 0

p = pigpio.pi()

def init():
    # Initialize PIL-library.
    disp.begin()
    # Clear display.
    disp.clear()
    disp.display()


if __name__ == '__main__':
    init()
    # Get drawing object to draw on image
    draw = ImageDraw.Draw(image)

    # Load default font.
    #font = ImageFont.load_default()
    font = ImageFont.truetype('Russo_One.ttf',32)

    heating    = False
    humidating = False
    r=0
    next_reading = time.time()
    while True:
        # Try to grab a sensor readings.
        sensor.trigger()
        humidity    = sensor.humidity()
        temperature = sensor.temperature()

        # Note that sometimes you won't get a reading and the results
        # will be large negative values (because Linux can't guarantee
        # the timing of calls to read the sensor).  If this happens
        # try again!
        if humidity > -1.0 and temperature > -273.15:
            if humidity<humilimit:
                if not humidating:
                    humidating=True
                    if debug: print("Humidating ON,   humidity {0:0.1f}% ".format(humidity),
                                    datetime.now())
                    p.write(humpin, pigpio.HIGH)
            else:
                if humidating:
                    humidating=False
                    if debug: print("Humidating OFF,  humidity {0:0.1f}% ".format(humidity), datetime.now())
                    p.write(humpin, pigpio.LOW)
            if temperature < heatlimit:
                if not heating:
                    heating=True
                    if debug: print("Heating ON,   temperature {0:0.1f}°C".format(temperature), datetime.now())
                    p.write(heatpin, pigpio.HIGH)
            else:
                if heating:
                    heating=False
                    if debug: print("Heating OFF,  temperature {0:0.1f}°C".format(temperature), datetime.now())
                    p.write(heatpin, pigpio.LOW)
                
            # Clear the screen by drawing a black rectancle.
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.text((x, top), "{0:0.1f}°C".format(temperature), font=font,
                      fill=255)
            disp.image(image)
            disp.display()
            time.sleep(INTERVAL/2.0)
        
            # Clear the screen by drawing a black rectancle.
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.text((x, top), "{0:0.1f}%".format(humidity), font=font,
                      fill=255)
            disp.image(image)
            disp.display()
            time.sleep(INTERVAL/2.0)
        else:
            print("Failed to read the sensor.", datetime.now())
            time.sleep(INTERVAL)
