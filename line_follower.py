#!/usr/bin/env python3
import os, sys
if not os.geteuid() == 0:
    sys.exit("\nPlease run as root.\n")
if sys.version_info < (3,0):
    sys.exit("\nPlease run under python3.\n")

import cv2, rcpy, datetime, time, numpy, pygame, threading, math

# Enable steering servo
from rcpy.servo import servo1
rcpy.servo.enable()
servo1.set(0)
servo1clk = rcpy.clock.Clock(servo1, 0.02)
servo1clk.start()

# Enable throttle
from rcpy.servo import servo3
rcpy.servo.enable()
servo3.set(0)
servo3clk = rcpy.clock.Clock(servo3, 0.02)
servo3clk.start()
time.sleep(1)
print("Arming throttle")
servo3.set(-0.1)
time.sleep(3)
servo3.set(0)

# This file was originally part of the OpenMV project.
# Copyright (c) 2013-2017 Ibrahim Abdelkader <iabdalkader@openmv.io> & Kwabena W. Agyeman <kwagyeman@openmv.io>
# This work is licensed under the MIT license, see the file LICENSE for details.

###########
# Settings
###########

IMG_DIR = "/mnt"
#IMG_DIR = "/run/bluedonkey"

COLOR_LINE_FOLLOWING = True # False to use grayscale thresholds, true to use color thresholds.
COLOR_THRESHOLDS = [( 85, 100,  -40,  -10,    0,  127)] # Yellow Line.
GRAYSCALE_THRESHOLDS = [(240, 255)] # White Line.
COLOR_HIGH_LIGHT_THRESHOLDS = [(80, 100, -10, 10, -10, 10)]
# https://pythonprogramming.net/color-filter-python-opencv-tutorial/
#COLOR_HIGH_LIGHT_THRESHOLDS_MAX = numpy.array([255,255,255])
#COLOR_HIGH_LIGHT_THRESHOLDS_MIN = numpy.array([230,230,230])
COLOR_HIGH_LIGHT_THRESHOLDS_MAX = numpy.array([255,190,50])
COLOR_HIGH_LIGHT_THRESHOLDS_MIN = numpy.array([170,0,0])
#FRAME_EXPOSURE = 0.000001
FRAME_EXPOSURE = 0
GRAYSCALE_HIGH_LIGHT_THRESHOLDS = [(250, 255)]
BINARY_VIEW = False # Helps debugging but costs FPS if on.
#BINARY_VIEW = True # Helps debugging but costs FPS if on.
DO_NOTHING = False # Just capture frames...
#FRAME_SIZE = sensor.QQVGA # Frame size.
FRAME_WIDTH = 160
FRAME_HEIGHT = 120
FRAME_REGION = 0.75 # Percentage of the image from the bottom (0 - 1.0).
FRAME_WIDE = 1.0 # Percentage of the frame width.
ROI_VERTICES = numpy.array([[0,119], [0,90], [70,20], [90,20], [159,90], [159,119]], dtype=numpy.int32)
ROI_MASK = numpy.zeros((120, 160), numpy.uint8)
cv2.fillConvexPoly(ROI_MASK, ROI_VERTICES, 255)

AREA_THRESHOLD = 0 # Raise to filter out false detections.
PIXELS_THRESHOLD = 40 # Raise to filter out false detections.
MAG_THRESHOLD = 4 # Raise to filter out false detections.
MIXING_RATE = 0.9 # Percentage of a new line detection to mix into current steering.

# Tweak these values for your robocar.
THROTTLE_CUT_OFF_ANGLE = 3.0 # Maximum angular distance from 90 before we cut speed [0.0-90.0).
THROTTLE_CUT_OFF_RATE = 0.8 # How much to cut our speed boost (below) once the above is passed (0.0-1.0].
THROTTLE_GAIN = 0.0 # e.g. how much to speed up on a straight away
THROTTLE_OFFSET = 75.0 # e.g. default speed (0 to 100)
THROTTLE_P_GAIN = 1.0
THROTTLE_I_GAIN = 0.0
THROTTLE_I_MIN = -0.0
THROTTLE_I_MAX = 0.0
THROTTLE_D_GAIN = 0.0

# Tweak these values for your robocar.
STEERING_OFFSET = 90 # Change this if you need to fix an imbalance in your car (0 to 180).
STEERING_P_GAIN = -30.0 # Make this smaller as you increase your speed and vice versa.
STEERING_I_GAIN = 0.0
STEERING_I_MIN = -0.0
STEERING_I_MAX = 0.0
STEERING_D_GAIN = -7 # Make this larger as you increase your speed and vice versa.

# Tweak these values for your robocar.
#THROTTLE_SERVO_MIN_US = 1500
#THROTTLE_SERVO_MAX_US = 2000
THROTTLE_SERVO_MIN_US = 0
THROTTLE_SERVO_MAX_US = 0.1

# Tweak these values for your robocar.
#STEERING_SERVO_MIN_US = 700
#STEERING_SERVO_MAX_US = 2300
STEERING_SERVO_MIN_US = -1.5
STEERING_SERVO_MAX_US = 1.5

###########
# Setup
###########

FRAME_REGION = max(min(FRAME_REGION, 1.0), 0.0)
FRAME_WIDE = max(min(FRAME_WIDE, 1.0), 0.0)
MIXING_RATE = max(min(MIXING_RATE, 1.0), 0.0)

THROTTLE_CUT_OFF_ANGLE = max(min(THROTTLE_CUT_OFF_ANGLE, 89.99), 0)
THROTTLE_CUT_OFF_RATE = max(min(THROTTLE_CUT_OFF_RATE, 1.0), 0.01)

THROTTLE_OFFSET = max(min(THROTTLE_OFFSET, 100), 0)
STEERING_OFFSET = max(min(STEERING_OFFSET, 180), 0)

# Handle if these were reversed...
tmp = max(THROTTLE_SERVO_MIN_US, THROTTLE_SERVO_MAX_US)
THROTTLE_SERVO_MIN_US = min(THROTTLE_SERVO_MIN_US, THROTTLE_SERVO_MAX_US)
THROTTLE_SERVO_MAX_US = tmp

# Handle if these were reversed...
tmp = max(STEERING_SERVO_MIN_US, STEERING_SERVO_MAX_US)
STEERING_SERVO_MIN_US = min(STEERING_SERVO_MIN_US, STEERING_SERVO_MAX_US)
STEERING_SERVO_MAX_US = tmp

# This function maps the output of the linear regression function to a driving vector for steering
# the robocar. See https://openmv.io/blogs/news/linear-regression-line-following for more info.

old_cx_normal = None
def figure_out_my_steering(line, img):
    global old_cx_normal
    [vx,vy,x,y] = line
    height, width, layers = img.shape
    cx_middle = x - (width / 2)
    cx_normal = cx_middle / (width / 2)

    if old_cx_normal != None:
        old_cx_normal = (cx_normal * MIXING_RATE) + (old_cx_normal * (1.0 - MIXING_RATE))
    else: 
        old_cx_normal = cx_normal
    return old_cx_normal

# Solve: THROTTLE_CUT_OFF_RATE = pow(sin(90 +/- THROTTLE_CUT_OFF_ANGLE), x) for x...
#        -> sin(90 +/- THROTTLE_CUT_OFF_ANGLE) = cos(THROTTLE_CUT_OFF_ANGLE)
t_power = math.log(THROTTLE_CUT_OFF_RATE) / math.log(math.cos(math.radians(THROTTLE_CUT_OFF_ANGLE)))

def figure_out_my_throttle(steering): # steering -> [0:180]

    # pow(sin()) of the steering angle is only non-zero when driving straight... e.g. steering ~= 90
    t_result = math.pow(math.sin(math.radians(max(min(steering, 179.99), 0.0))), t_power)

    return (t_result * THROTTLE_GAIN) + THROTTLE_OFFSET

#
# Servo Control Code
#

# throttle [0:100] (101 values) -> [THROTTLE_SERVO_MIN_US, THROTTLE_SERVO_MAX_US]
# steering [0:180] (181 values) -> [STEERING_SERVO_MIN_US, STEERING_SERVO_MAX_US]
def set_servos(throttle, steering):
    throttle = THROTTLE_SERVO_MIN_US + ((throttle/100) * (THROTTLE_SERVO_MAX_US - THROTTLE_SERVO_MIN_US))
    steering = STEERING_SERVO_MIN_US + ((steering/180) * (STEERING_SERVO_MAX_US - STEERING_SERVO_MIN_US))
    #print(steering, end="")
    servo3.set(throttle)
    servo1.set(steering)

#
# Camera Control Code
#

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FPS, 30)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
if FRAME_EXPOSURE > 0:
    capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
    capture.set(cv2.CAP_PROP_EXPOSURE, FRAME_EXPOSURE)
frame = numpy.zeros((120, 160, 3), dtype=numpy.uint8)
frame_in = numpy.zeros((120, 160, 3), dtype=numpy.uint8)

class cameraThread(threading.Thread):
    def run(self):
        global frame, frame_in
        while True:            
            ret, frametmp = capture.read()
            if ret:
                frame_in = frametmp
            k = cv2.waitKey(5) & 0xFF
            if k == ord('q'):
                break

thread = cameraThread()
thread.start()

clock = pygame.time.Clock()

###########
# Loop
###########

old_time = datetime.datetime.now()

throttle_old_result = None
throttle_i_output = 0
throttle_output = THROTTLE_OFFSET

steering_old_result = None
steering_i_output = 0
steering_output = STEERING_OFFSET

frame_cnt = 0

while True:
    clock.tick()
    #ret, frame = capture.read()
    frame = frame_in
    color_mask = cv2.inRange(frame, COLOR_HIGH_LIGHT_THRESHOLDS_MIN, COLOR_HIGH_LIGHT_THRESHOLDS_MAX)
    res = cv2.bitwise_and(frame, frame, mask=color_mask)
    res = cv2.bitwise_and(res, res, mask=ROI_MASK)
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    pixelpoints = cv2.findNonZero(gray)
    if pixelpoints is not None:
        vx = 0
        vy = 1
        x = int(pixelpoints[:,:,0].mean())
        y = 50
        line = [vx,vy,x,y]
    else:
        line = False

    print_string = ""
    if line:
        new_time = datetime.datetime.now()
        delta_time = (new_time - old_time).microseconds / 1000
        old_time = new_time

        #
        # Figure out steering and do steering PID
        #

        steering_new_result = figure_out_my_steering(line, frame)
        #print("%05.2f " % (steering_new_result), end="")
        steering_delta_result = (steering_new_result - steering_old_result) if (steering_old_result != None) else 0
        steering_old_result = steering_new_result

        steering_p_output = steering_new_result # Standard PID Stuff here... nothing particularly interesting :)
        steering_i_output = max(min(steering_i_output + steering_new_result, STEERING_I_MAX), STEERING_I_MIN)
        steering_d_output = ((steering_delta_result * 1000) / delta_time) if delta_time else 0
        steering_pid_output = (STEERING_P_GAIN * steering_p_output) + \
                              (STEERING_I_GAIN * steering_i_output) + \
                              (STEERING_D_GAIN * steering_d_output)

        # Steering goes from [-90,90] but we need to output [0,180] for the servos.
        steering_output = (STEERING_OFFSET + steering_pid_output) % 180

        #
        # Figure out throttle and do throttle PID
        #

        throttle_new_result = figure_out_my_throttle(steering_output)
        throttle_delta_result = (throttle_new_result - throttle_old_result) if (throttle_old_result != None) else 0
        throttle_old_result = throttle_new_result

        throttle_p_output = throttle_new_result # Standard PID Stuff here... nothing particularly interesting :)
        throttle_i_output = max(min(throttle_i_output + throttle_new_result, THROTTLE_I_MAX), THROTTLE_I_MIN)
        throttle_d_output = ((throttle_delta_result * 1000) / delta_time) if delta_time else 0
        throttle_pid_output = (THROTTLE_P_GAIN * throttle_p_output) + \
                              (THROTTLE_I_GAIN * throttle_i_output) + \
                              (THROTTLE_D_GAIN * throttle_d_output)

        # Throttle goes from 0% to 100%.
        throttle_output = max(min(throttle_pid_output, 100), 0)

        print_string = "Line Ok   - throttle %03d, steering %03d, frame %05d" % \
            (throttle_output , steering_output, frame_cnt)

    else:
        throttle_output = throttle_output * 0.99
        print_string = "Line Lost - throttle %03d, steering %03d, frame %05d" % \
            (throttle_output , steering_output, frame_cnt)

    set_servos(throttle_output, steering_output)
    if BINARY_VIEW:
        frame_file_name = "%s/cam%05d.png" % (IMG_DIR, frame_cnt)
        res_file_name = "%s/res%05d.png" % (IMG_DIR, frame_cnt)
        frame_cnt += 1
        cv2.imwrite(frame_file_name, frame)
        res = cv2.line(res, (x,0), (x,119), (0,255,0), 2)
        cv2.imwrite(res_file_name, res)
    print("FPS %05.2f - %s\r" % (clock.get_fps(), print_string), end="")
