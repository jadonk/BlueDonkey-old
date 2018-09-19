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
print("Arming")
servo3.set(-0.1)
time.sleep(3)
print("Idle")
servo3.set(0)
time.sleep(3)
#print("Medium")
#servo3.set(0.1)
#time.sleep(1)
print("Slow")
servo3.set(0.05)
time.sleep(3)
#print("Fast")
#servo3.set(0.2)
#time.sleep(2)
print("Brake")
servo3.set(-1)
time.sleep(1)
#print("Idle")
#servo3.set(0)
#time.sleep(2)
#print("Reverse")
#servo3.set(-0.3)
#time.sleep(1)
print("Stop")
servo3.set(0)
time.sleep(1)

servo3clk.stop()
rcpy.servo.disable()

