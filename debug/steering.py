#!/usr/bin/env python3
import os, sys
if not os.geteuid() == 0:
    sys.exit("\nPlease run as root.\n")
if sys.version_info < (3,0):
    sys.exit("\nPlease run under python3.\n")

import rcpy, time
from rcpy.servo import servo1
rcpy.servo.enable()
servo1.set(0)
servo1clk = rcpy.clock.Clock(servo1, 0.02)
servo1clk.start()

time.sleep(1)
servo1.set(-0.4)
time.sleep(1)
servo1.set(0.6)
time.sleep(1)
servo1.set(0)
time.sleep(1)

servo1clk.stop()
rcpy.servo.disable()

