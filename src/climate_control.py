#!/usr/bin/env python3
# Copyright (c) 2014, 2017 Adafruit Industries,
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
import Adafruit_DHT
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import time
import RPi.GPIO as GPIO
from datetime import datetime

configfile = 'terrarium.conf'
cfg = configparser.ConfigParser()
cfg.read(configfile)

debug     = bool( cfg.get('debug', 'debug'     ))
sensor    =       cfg.get('input', 'dhttype'   )
dhtpin    = int(  cfg.get('input', 'dhtpin'    ))
heatpin   = int(  cfg.get('output', 'heat'     ))
humpin    = int(  cfg.get('output', 'humidity' ))
humilimit = float(cfg.get('climate', 'humidity'))
heatlimit = float(cfg.get('climate', 'heat'    ))

sensor_args = { '11':   Adafruit_DHT.DHT11,
                '22':   Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }

sensor = sensor_args[sensor]


# Raspberry Pi pin configuration:
RST = 24

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Geometry
width  = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing
# shapes.
x = 0

def init():
    # Initialize PIL-library.
    disp.begin()
    # Clear display.
    disp.clear()
    disp.display()
    if debug: print("GPIO mode: ", GPIO.getmode())
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([heatpin, humpin], GPIO.OUT, initial=GPIO.LOW)


if __name__ == '__main__':
    init()
    # Get drawing object to draw on image
    draw = ImageDraw.Draw(image)

    # Load default font.
    #font = ImageFont.load_default()
    font = ImageFont.truetype('Russo_One.ttf',32)

    heating    = False
    humidating = False
    while True:
        # Try to grab a sensor reading.  Use the read_retry method which
        # will retry up to 15 times to get a sensor reading (waiting 2
        # seconds between each retry).
        humidity, temperature = Adafruit_DHT.read_retry(sensor, dhtpin)

        # Note that sometimes you won't get a reading and
        # the results will be null (because Linux can't
        # guarantee the timing of calls to read the sensor).
        # If this happens try again!
        if humidity is not None and temperature is not None:
            if humidity<humilimit:
                if not humidating:
                    humidating=True
                    if debug: print("Humidating ON,   humidity {0:0.1f}% ".format(humidity),
                                    datetime.now())
                GPIO.output(humpin, GPIO.HIGH)
            else:
                if humidating:
                    humidating=False
                    if debug: print("Humidating OFF,  humidity {0:0.1f}% ".format(humidity), datetime.now())
                GPIO.output(humpin, GPIO.LOW)
            if temperature < heatlimit:
                if not heating:
                    heating=True
                    if debug: print("Heating ON,   temperature {0:0.1f}°C".format(temperature), datetime.now())
                GPIO.output(heatpin, GPIO.HIGH)
            else:
                if heating:
                    heating=False
                    if debug: print("Heating OFF,  temperature {0:0.1f}°C".format(temperature), datetime.now())
                GPIO.output(heatpin, GPIO.LOW)
                
            # Clear the screen by drawing a black rectancle.
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.text((x, top), "{0:0.1f}°C".format(temperature), font=font,
                      fill=255)
            disp.image(image)
            disp.display()
            time.sleep(4)
        
            # Clear the screen by drawing a black rectancle.
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.text((x, top), "{0:0.1f}%".format(humidity), font=font,
                      fill=255)
            disp.image(image)
            disp.display()
            time.sleep(3)
        else:
            print("Failed to read the sensor.", datetime.now())
            time.sleep(10)
