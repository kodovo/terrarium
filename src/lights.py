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
# zero, and instead correcting the angle by -34 arc minutes should put
# the predictions within 30s of the true timings.  Accurate enough for
# us.  See e.g. https://github.com/brandon-rhodes/pyephem/issues/33
terraland.pressure  = 0.0
terraland.horizon   = '-0:34'

sun = ephem.Sun()

scheduler = sched.scheduler()

def suntimes(next=True):
    """suntimes(next) returns a tuple of (rise_time, set_time) in the
    local timezone.  If next=True, the times are for the next events, 
    if next=False the times are for the previous events."""
    
    if not next:
        utc_r1 = terraland.previous_rising(sun).datetime()
        utc_s1 = terraland.previous_setting(sun).datetime()
    else:
        utc_r1 = terraland.next_rising(sun).datetime()
        utc_s1 = terraland.next_setting(sun).datetime()
    # The rising/setting funcions return time values in UTC, but
    # without attached zone info.  So adding the zone info after
    # fetching the values.
    utc_r1 = utc_r1.replace(tzinfo=from_zone)
    utc_s1 = utc_s1.replace(tzinfo=from_zone)

    # Moving to the local time zone.
    r1 = utc_r1.astimezone(to_zone)
    s1 = utc_s1.astimezone(to_zone)
    return (r1, s1)

def init():
    #GPIO.setwarnings(False)
    prev_r1, prev_s1 = suntimes(next=False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN, GPIO.OUT)    
    if prev_r1 > prev_s1:
        # Night now
        lights_on()
    else:
        # Day now
        lights_off()

def lights_on():
    GPIO.output(PIN, GPIO.HIGH)

def lights_off():
    GPIO.output(PIN, GPIO.LOW)

def bye():
    GPIO.cleanup()
    
if __name__ == '__main__':
    init()
    while True:
        # Fetching the next rise/set times
        next_r1, next_s1 = suntimes()
        print("Visual sunrise %s" % next_r1)
        print("Visual sunset %s"  % next_s1)

        # Datetime to timestamp
        next_tr1 = next_r1.timestamp()
        next_ts1 = next_s1.timestamp()

        scheduler.enterabs(time=next_tr1, priority=1, action=lights_on)
        scheduler.enterabs(time=next_ts1, priority=1, action=lights_off)
        print(scheduler.queue)
        scheduler.run()
    bye()
