#!/usr/bin/env python3
# Copyright (c) 2018 Pekko Metsä

import lights

if __name__ == '__main__':
    lights.init()
    while True:
        # Fetching the next rise/set times
        next_risetime, next_settime = lights.suntimes()
        print("Visual sunrise %s" % next_risetime)
        print("Visual sunset  %s" % next_settime)

        # Datetime to timestamp (_ts_ in the variable name)
        next_ts_risetime = next_risetime.timestamp()
        next_ts_settime = next_settime.timestamp()

        lights.scheduler.enterabs(time=next_ts_risetime, priority=1,
                                  action=lights.lights_on)
        lights.scheduler.enterabs(time=next_ts_settime, priority=1,
                                  action=lights.lights_off)
        print(lights.scheduler.queue)
        lights.scheduler.run()
