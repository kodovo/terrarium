# terrarium

When using a Raspberry Pi for controlling the lights, heat, and
humidity of a terrarium, one needs some code.  Here is something which
hopes to evolve into a Python implementation of that.

Please copy doc/terrarium.conf.example to the runtime work directory
as terrarium.conf, and edit it if needed.

The GPIO pins are handled via pigpio daemon (pigpiod), so you should
start it (or enable it by systemd) before launching the scripts.
