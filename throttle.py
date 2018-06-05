#!/usr/bin/env python3
import os, sys
if not os.geteuid() == 0:
    sys.exit("\nPlease run as root.\n")
if sys.version_info < (3,0):
    sys.exit("\nPlease run under python3.\n")

import rcpy, time
from rcpy.servo import servo3
rcpy.servo.enable()
servo3.set(0)
servo3clk = rcpy.clock.Clock(servo3, 0.02)
servo3clk.start()

time.sleep(1)
servo3.set(-0.1)
time.sleep(3)
servo3.set(0)
time.sleep(1)
servo3.set(0.5)
time.sleep(1)
servo3.set(0.0)
time.sleep(1)

servo3clk.stop()
rcpy.servo.disable()

