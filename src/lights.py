#!/usr/bin/env python3

import configparser
#from numpy import pi
pi = 3.141592653589793
from dateutil import tz
import ephem

import sched #, time
import RPi.GPIO as GPIO

configfile = 'terrarium.conf'
cfg = configparser.ConfigParser()
cfg.read(configfile)

PIN  = int(   cfg.get('relays',   'lights'    ))
LAT  = float( cfg.get('location', 'latitude'  )) * pi / 180.0
LON  = float( cfg.get('location', 'longitude' )) * pi / 180.0
ALT  = float( cfg.get('location', 'altitude'  ))
ZONE =        cfg.get('location', 'timezone'  )

from_zone = tz.gettz('UTC')
to_zone   = tz.gettz(ZONE)

terraland           = ephem.Observer()
terraland.lat       = LAT
terraland.lon       = LON
terraland.elevation = ALT

# Switching the refraction off by setting the atmospheric pressure to
# zero, and instead correcting the angle by -34 arc minutes.  That
# should put the predictions within 30 seconds of the true timings.
# Accurate enough for us.  See
# e.g. https://github.com/brandon-rhodes/pyephem/issues/33
terraland.pressure  = 0.0
terraland.horizon   = '-0:34'

sun = ephem.Sun()

scheduler = sched.scheduler()

def suntimes(next=True):
    """suntimes(next) returns a tuple of (rise_time, set_time) in the
    local timezone.  If next=True, the times are for the next events, 
    if next=False the times are for the previous events."""
    
    if not next:
        utc_risetime = terraland.previous_rising(sun).datetime()
        utc_settime = terraland.previous_setting(sun).datetime()
    else:
        utc_risetime = terraland.next_rising(sun).datetime()
        utc_settime = terraland.next_setting(sun).datetime()
    # The rising/setting funcions return time values in UTC, but
    # without attached zone info.  So adding the zone info after
    # fetching the values.
    utc_risetime = utc_risetime.replace(tzinfo=from_zone)
    utc_settime = utc_settime.replace(tzinfo=from_zone)

    # Moving to the local time zone.
    risetime = utc_risetime.astimezone(to_zone)
    settime = utc_settime.astimezone(to_zone)
    return (risetime, settime)

def init():
    """Fetches the previous sun rise/set times, and compares them to 
    find out whether the Sun is above the horizon or not.  Sets the 
    output pin accordingly."""
    #GPIO.setwarnings(False)
    prev_risetime, prev_settime = suntimes(next=False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN, GPIO.OUT)    
    if prev_risetime > prev_settime:
        # Day now
        lights_on()
    else:
        # Night now
        lights_off()

def lights_on():
    "Sets the output pin (ie. HIGH)"
    GPIO.output(PIN, GPIO.HIGH)

def lights_off():
    "Unsets the output pin (ie. LOW)"
    GPIO.output(PIN, GPIO.LOW)

def bye():
    "Cleans the GPIO pins used in the program."
    GPIO.cleanup()
    
if __name__ == '__main__':
    init()
    while True:
        # Fetching the next rise/set times
        next_risetime, next_settime = suntimes()
        print("Visual sunrise %s" % next_risetime)
        print("Visual sunset %s"  % next_settime)

        # Datetime to timestamp (_ts_ in the variable name)
        next_ts_risetime = next_risetime.timestamp()
        next_ts_settime = next_settime.timestamp()

        scheduler.enterabs(time=next_ts_risetime, priority=1, action=lights_on)
        scheduler.enterabs(time=next_ts_ettime, priority=1, action=lights_off)
        print(scheduler.queue)
        scheduler.run()
