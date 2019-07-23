#!/usr/bin/env python3.7
import os, sys

# Make sure we are running as 'root' under Python 3.7
# This is only required for rcpy access through the PRU
if not os.geteuid() == 0:
    sys.exit("\nPlease run as root.\n")
if sys.version_info < (3,7):
    sys.exit("\nPlease run under python3.7\n")

# Enable GPIO for XXX
if not os.path.exists('/sys/class/gpio/gpio69'):
    exportFile = open("/sys/class/gpio/export", "w")
    exportFile.write("69\n")
    exportFile.close

print("Loading Python modules for car_control. Please be patient.")
import rcpy, datetime, time, pygame, math
from rcpy.servo import servo1
from rcpy.servo import servo3
from rcpy.button import mode, pause
from rcpy import button
from rcpy.led import red
from rcpy.led import green
import socket
print("Done importing modules for now!")

# This car_control routine was originally part of the OpenMV project.
# Copyright (c) 2013-2017 Ibrahim Abdelkader <iabdalkader@openmv.io> & Kwabena W. Agyeman <kwagyeman@openmv.io>
# This work is licensed under the MIT license, see the file LICENSE for details.

###########
# Settings
###########
FRAME_WIDTH = 160
MIXING_RATE = 0.9 # Percentage of a new line detection to mix into current steering.

# Tweak these values for your robocar.
THROTTLE_CUT_OFF_ANGLE = 3.0 # Maximum angular distance from 90 before we cut speed [0.0-90.0).
THROTTLE_CUT_OFF_RATE = 0.9 # How much to cut our speed boost (below) once the above is passed (0.0-1.0].
THROTTLE_GAIN = 60.0 # e.g. how much to speed up on a straight away
THROTTLE_OFFSET = 40.0 # e.g. default speed (0 to 100)
THROTTLE_P_GAIN = 1.0
THROTTLE_I_GAIN = 0.0
THROTTLE_I_MIN = -0.0
THROTTLE_I_MAX = 0.0
THROTTLE_D_GAIN = 0.0

# Tweak these values for your robocar.
STEERING_OFFSET = 90 # Change this if you need to fix an imbalance in your car (0 to 180).
STEERING_P_GAIN = -10.0 # Make this smaller as you increase your speed and vice versa.
STEERING_I_GAIN = 0.0
STEERING_I_MIN = -0.0
STEERING_I_MAX = 0.0
STEERING_D_GAIN = -7 # Make this larger as you increase your speed and vice versa.

# Tweak these values for your robocar.
THROTTLE_SERVO_MIN = 0
THROTTLE_SERVO_MAX = 0.15

# Tweak these values for your robocar.
STEERING_SERVO_MIN = -1.5
STEERING_SERVO_MAX = 1.5

###########
# Setup
###########

MIXING_RATE = max(min(MIXING_RATE, 1.0), 0.0)

THROTTLE_CUT_OFF_ANGLE = max(min(THROTTLE_CUT_OFF_ANGLE, 89.99), 0)
THROTTLE_CUT_OFF_RATE = max(min(THROTTLE_CUT_OFF_RATE, 1.0), 0.01)

THROTTLE_OFFSET = max(min(THROTTLE_OFFSET, 100), 0)
STEERING_OFFSET = max(min(STEERING_OFFSET, 180), 0)

# Handle if these were reversed...
tmp = max(THROTTLE_SERVO_MIN, THROTTLE_SERVO_MAX)
THROTTLE_SERVO_MIN = min(THROTTLE_SERVO_MIN, THROTTLE_SERVO_MAX)
THROTTLE_SERVO_MAX = tmp

# Handle if these were reversed...
tmp = max(STEERING_SERVO_MIN, STEERING_SERVO_MAX)
STEERING_SERVO_MIN = min(STEERING_SERVO_MIN, STEERING_SERVO_MAX)
STEERING_SERVO_MAX = tmp

class car_control:
    old_cx_normal = None

    throttle_old_result = None
    throttle_i_output = 0
    throttle_output = 0

    steering_old_result = None
    steering_i_output = 0
    steering_output = STEERING_OFFSET
    
    def figure_out_my_steering(self, line):
        [vx,vy,x,y] = line
        cx_middle = x - (FRAME_WIDTH / 2)
        cx_normal = cx_middle / (FRAME_WIDTH / 2)
    
        if self.old_cx_normal != None:
            self.old_cx_normal = (cx_normal * MIXING_RATE) + \
                (self.old_cx_normal * (1.0 - MIXING_RATE))
        else: 
            self.old_cx_normal = cx_normal
        return self.old_cx_normal

    def figure_out_my_throttle(self, steering): # steering -> [0:180]
        # Solve: THROTTLE_CUT_OFF_RATE = pow(sin(90 +/- THROTTLE_CUT_OFF_ANGLE), x) for x...
        #        -> sin(90 +/- THROTTLE_CUT_OFF_ANGLE) = cos(THROTTLE_CUT_OFF_ANGLE)
        t_power = math.log(THROTTLE_CUT_OFF_RATE) / math.log(math.cos(math.radians(THROTTLE_CUT_OFF_ANGLE)))
    
        # pow(sin()) of the steering angle is only non-zero when driving straight... e.g. steering ~= 90
        t_result = math.pow(math.sin(math.radians(max(min(steering, 179.99), 0.0))), t_power)
        return (t_result * THROTTLE_GAIN) + THROTTLE_OFFSET
    
    #
    # Servo Control Code
    #
    
    # throttle [0:100] (101 values) -> [THROTTLE_SERVO_MIN, THROTTLE_SERVO_MAX]
    # steering [0:180] (181 values) -> [STEERING_SERVO_MIN, STEERING_SERVO_MAX]
    def set_servos(self, throttle, steering):
        throttle = THROTTLE_SERVO_MIN + ((throttle/100) * (THROTTLE_SERVO_MAX - THROTTLE_SERVO_MIN))
        steering = STEERING_SERVO_MIN + ((steering/180) * (STEERING_SERVO_MAX - STEERING_SERVO_MIN))
        servo3.set(throttle)
        servo1.set(steering)
    
    # Enable PWM/servo outputs
    def enable_steering_and_throttle(self):
        rcpy.servo.enable()
        
        # Enable steering servo
        servo1.set(0)
        servo1clk = rcpy.clock.Clock(servo1, 0.02)
        servo1clk.start()
        
        # Enable throttle
        servo3.set(0)
        servo3clk = rcpy.clock.Clock(servo3, 0.02)
        servo3clk.start()
        time.sleep(1)
        print("Arming throttle")
        servo3.set(-0.1)
        time.sleep(3)
        servo3.set(0)

    def tick(self):
        self.fps.tick()

    def update(self, line):
        print_string = ""
        self.fps.stamp()
        if line:
            self.fps.update()
    
            #
            # Figure out steering and do steering PID
            #
    
            steering_new_result = self.figure_out_my_steering(line)
            steering_delta_result = (steering_new_result - self.steering_old_result) if (self.steering_old_result != None) else 0
            self.steering_old_result = steering_new_result
    
            steering_p_output = steering_new_result # Standard PID Stuff here... nothing particularly interesting :)
            self.steering_i_output = max(min(self.steering_i_output + steering_new_result, STEERING_I_MAX), STEERING_I_MIN)
            steering_d_output = ((steering_delta_result * 1000) / self.fps.delta()) if self.fps.delta() else 0
            steering_pid_output = (STEERING_P_GAIN * steering_p_output) + \
                                  (STEERING_I_GAIN * self.steering_i_output) + \
                                  (STEERING_D_GAIN * steering_d_output)
    
            # Steering goes from [-90,90] but we need to output [0,180] for the servos.
            self.steering_output = (STEERING_OFFSET + steering_pid_output) % 180
    
            #
            # Figure out throttle and do throttle PID
            #
    
            throttle_new_result = figure_out_my_throttle(self.steering_output)
            throttle_delta_result = (throttle_new_result - self.throttle_old_result) if (self.throttle_old_result != None) else 0
            self.throttle_old_result = throttle_new_result
    
            throttle_p_output = throttle_new_result # Standard PID Stuff here... nothing particularly interesting :)
            self.throttle_i_output = max(min(self.throttle_i_output + throttle_new_result, THROTTLE_I_MAX), THROTTLE_I_MIN)
            throttle_d_output = ((throttle_delta_result * 1000) / self.fps.delta()) if self.fps.delta() else 0
            throttle_pid_output = (THROTTLE_P_GAIN * throttle_p_output) + \
                                  (THROTTLE_I_GAIN * self.throttle_i_output) + \
                                  (THROTTLE_D_GAIN * throttle_d_output)
    
            # Throttle goes from 0% to 100%.
            self.throttle_output = max(min(throttle_pid_output, 100), 0)
        else:
            self.throttle_output = self.throttle_output * 0.99
    
        if self.paused.state():
            print_string = "Paus %03d %03d %03d %05d %05d" % \
                (self.steering_output, self.throttle_output, 0, 0, 0)
            self.throttle_output = 0
            self.steering_output = STEERING_OFFSET
            time.sleep(0.001)
        else:
            if line:
                print_string = " %03d %03d %03d %03d %05d %05d" % \
                    (x, self.steering_output, self.throttle_output, 0, 0, 0)
            else:
                print_string = "Lost %03d %03d %03d %05d %05d" % \
                    (self.steering_output, self.throttle_output, 0, 0, 0)
    
        self.set_servos(self.throttle_output, self.steering_output)
        print("%06.2f %s\r" % (self.fps.get(), print_string), end="")
        return print_string

    def __init__(self):
        # Display link to stream and dashboard
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_addr = s.getsockname()[0]
        s.close()
        print("Open http://" + str(ip_addr) + ":8090 for video stream")
        print("Open http://" + str(ip_addr) + ":1880/ui for dashboard")

        # Start up the pause button handler
        self.paused = PauseButtonEvent()
        self.paused.start()

        self.enable_steering_and_throttle()

        self.fps = track_fps()

class PauseButtonEvent(button.ButtonEvent):
    state = True
    def __init__(self):
        # Start-up in 'paused' mode and handle button presses to exit paused mode
        red.on()
        green.off()
        button.ButtonEvent.__init__(self, pause, button.ButtonEvent.PRESSED)
        #self.start()
    def action(self, event):
        self.state = not self.state
        if paused:
            red.on()
            green.off()
        else:
            green.on()
            red.off()
    def state(self):
        return self.state
        
class track_fps:
    delta_time = 0
    stamp_time = 0
    old_time = 0
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.old_time = datetime.datetime.now()
    def tick(self):
        self.clock.tick()
    def get(self):
        return self.clock.get_fps()
    def stamp(self):
        self.stamp_time = datetime.datetime.now()
        msec_stamp = int((self.stamp_time.second * 1000) + (self.stamp_time.microsecond / 1000))
        return msec_stamp
    def update(self):
        self.delta_time = (self.stamp_time - self.old_time).microseconds / 1000
        self.old_time = self.stamp_time
    def delta(self):
        return self.delta_time
