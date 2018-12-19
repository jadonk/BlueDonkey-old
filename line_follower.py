#!/usr/bin/env python3

# Make sure we are running as 'root' under Python 3
import os, sys
if not os.geteuid() == 0:
    sys.exit("\nPlease run as root.\n")
if sys.version_info < (3,0):
    sys.exit("\nPlease run under python3.\n")

# Load modules
print("Importing Python modules, please be patient.")
import cv2, rcpy, datetime, time, numpy, pygame, threading, math
from rcpy.servo import servo1
from rcpy.servo import servo3
from rcpy.button import mode, pause
from rcpy import button
from rcpy.led import red
from rcpy.led import green
import socket
print("Done importing Python modules!")

# Redirect input/output to a socket
SOCK_OUT = 3001
SOCK_IN = 3002
sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_out.connect(("255.255.255.255", SOCK_OUT))
sys.stdout = sock_out.makefile('w', buffering=None)
#sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock_in.connect(("127.0.0.1", SOCK_IN))
#sys.stdin = sock_in.makefile('r', buffering=None)

# Start-up in 'paused' mode and handle button presses to exit paused mode
paused = True
red.on()
green.off()
class PauseButtonEvent(button.ButtonEvent):
    def action(self, event):
        global paused
        paused = not paused
        if paused:
            red.on()
            green.off()
        else:
            green.on()
            red.off()
pause_event = PauseButtonEvent(pause, button.ButtonEvent.PRESSED)
pause_event.start()

# Enable PWM/servo outputs
def enable_steering_and_throttle():
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

# This file was originally part of the OpenMV project.
# Copyright (c) 2013-2017 Ibrahim Abdelkader <iabdalkader@openmv.io> & Kwabena W. Agyeman <kwagyeman@openmv.io>
# This work is licensed under the MIT license, see the file LICENSE for details.

###########
# Settings
###########

#IMG_DIR = "/var/lib/cloud9/mnt"
IMG_DIR = "/run/bluedonkey"
#FRAME_EXPOSURE = 0.000001
FRAME_EXPOSURE = 0
BINARY_VIEW = False # Helps debugging but costs FPS if on
COLOR_THRESHOLD_MIN = 250
COLOR_THRESHOLD_MAX = 254
COLOR_THRESHOLD_DELTA = 1
PERCENT_THRESHOLD_MIN = 2
PERCENT_THRESHOLD_MAX = 20
FRAME_WIDTH = 160
FRAME_HEIGHT = 120
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

# Array of region of interest masks in the order they should be searched
# Furthest away first
roi_masks = numpy.array([
        # Focus on the center
        # 8/20ths in from the left
        # 8/20ths down from the top
        # 1/20ths tall
        # 4x1 pixel count
        [int(8*FRAME_WIDTH/20), int(8*FRAME_HEIGHT/20), int(1*FRAME_HEIGHT/20), int((4*FRAME_WIDTH/20)*(1*FRAME_HEIGHT/20)/100)],
        # Then look wider
        # 6/20ths in from the sides
        # 9/20ths down from the top
        # 1/20ths tall
        # 8x1 pixel count
        [int(6*FRAME_WIDTH/20), int(9*FRAME_HEIGHT/20), int(1*FRAME_HEIGHT/20), int((8*FRAME_WIDTH/20)*(1*FRAME_HEIGHT/20)/100)],
        # Then look wider
        # 4/20ths in from the sides
        # 10/20ths down from the top
        # 1/20ths tall
        # 12x1 pixel count
        [int(4*FRAME_WIDTH/20), int(10*FRAME_HEIGHT/20), int(1*FRAME_HEIGHT/20), int((12*FRAME_WIDTH/20)*(1*FRAME_HEIGHT/20)/100)],
        # Then really wide and taller
        # 0/20ths in from the sides
        # 11/20ths down from the top
        # 1/20ths tall
        # 20x1 pixel count
        [int(0*FRAME_WIDTH/10), int(11*FRAME_HEIGHT/20), int(1*FRAME_HEIGHT/20), int((20*FRAME_WIDTH/20)*(1*FRAME_HEIGHT/20)/100)],
    ], dtype=numpy.int32)

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

# This function maps the output of the linear regression function to a driving vector for steering
# the robocar. See https://openmv.io/blogs/news/linear-regression-line-following for more info.

old_cx_normal = None
def figure_out_my_steering(line, img):
    global old_cx_normal
    [vx,vy,x,y] = line
    cx_middle = x - (FRAME_WIDTH / 2)
    cx_normal = cx_middle / (FRAME_WIDTH / 2)

    if old_cx_normal != None:
        old_cx_normal = (cx_normal * MIXING_RATE) + (old_cx_normal * (1.0 - MIXING_RATE))
    else: 
        old_cx_normal = cx_normal
    return old_cx_normal

def figure_out_my_throttle(steering): # steering -> [0:180]
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
def set_servos(throttle, steering):
    throttle = THROTTLE_SERVO_MIN + ((throttle/100) * (THROTTLE_SERVO_MAX - THROTTLE_SERVO_MIN))
    steering = STEERING_SERVO_MIN + ((steering/180) * (STEERING_SERVO_MAX - STEERING_SERVO_MIN))
    servo3.set(throttle)
    servo1.set(steering)

#
# Camera Control Code
#

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FPS, 30)
capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"Y210"))
capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH*2)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT*2)
if FRAME_EXPOSURE > 0:
    capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
    capture.set(cv2.CAP_PROP_EXPOSURE, FRAME_EXPOSURE)
frame = numpy.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=numpy.uint8)
frame_in = numpy.zeros((FRAME_HEIGHT*2, FRAME_WIDTH*2, 3), dtype=numpy.uint8)

cmd = None

class cameraThread(threading.Thread):
    def run(self):
        global frame_in, last_cmd
        while True:            
            ret, frametmp = capture.read()
            if ret:
                frame_in = frametmp
            time.sleep(0.03)
            #k = cv2.waitKey(1) & 0xFF
            #if k == ord('q'):
            #    cmd = 'q'
            #    break

thread = cameraThread()
thread.start()

clock = pygame.time.Clock()

###########
# Loop
###########

old_time = datetime.datetime.now()
msec_stamp = 0

throttle_old_result = None
throttle_i_output = 0
throttle_output = 0

steering_old_result = None
steering_i_output = 0
steering_output = STEERING_OFFSET

frame_cnt = 0
threshold = COLOR_THRESHOLD_MAX
font = cv2.FONT_HERSHEY_SIMPLEX

paused = True
pause_pressed = False
enable_steering_and_throttle()

while not (cmd == 'q'):
    clock.tick()
    line = False
    pixel_cnt = 0
    pixel_cnt_min = int(PERCENT_THRESHOLD_MIN*roi_masks[2][3])
    pixel_cnt_max = int(PERCENT_THRESHOLD_MAX*roi_masks[2][3])
    # Cconvert 320x240 to 160x120
    frame = frame_in[::2 ,::2].copy()
    for roi_mask in roi_masks:
        # roi_mask[0] pixels in from the sides
        # roi_mask[1] pixels down from the top
        # roi_mask[2] pixels high
        # roi_mask[3] number of pixels / 100
        if (not line) or (pixel_cnt < pixel_cnt_min):
            # Extract blue only in ROI 
            top = roi_mask[1]
            bottom = roi_mask[1] + roi_mask[2] - 1
            left = roi_mask[0]
            right = FRAME_WIDTH-roi_mask[0]-1
            blue = frame[ top : bottom , left : right , 0 ]
            # Zero out pixels below threshold
            thresh_mask = cv2.inRange(blue, threshold, 255)
            # Get array of pixel locations that are non-zero
            pixelpoints = cv2.findNonZero(thresh_mask)
            if pixelpoints is not None:
                pixel_cnt = pixelpoints.size
                pixel_cnt_min = int(PERCENT_THRESHOLD_MIN*roi_mask[3])
                pixel_cnt_max = int(PERCENT_THRESHOLD_MAX*roi_mask[3])
                vx = 0
                vy = 1
                y = int((top+bottom) / 2)
                x = int(pixelpoints[:,:,0].mean()) + roi_mask[0]
                line = [vx,vy,x,y]
                if BINARY_VIEW:
                    thresh_color = cv2.cvtColor(thresh_mask, cv2.COLOR_GRAY2BGR)
                    frame[ top : bottom , left : right ] = thresh_color

    # Adjust threshold if finding too few or too many pixels
    if pixel_cnt > pixel_cnt_max:
        threshold += COLOR_THRESHOLD_DELTA
        if threshold > COLOR_THRESHOLD_MAX:
            threshold = COLOR_THRESHOLD_MAX
    if pixel_cnt < pixel_cnt_min:
        threshold -= COLOR_THRESHOLD_DELTA
        if threshold < COLOR_THRESHOLD_MIN:
            threshold = COLOR_THRESHOLD_MIN

    print_string = ""
    stamp_time = datetime.datetime.now()
    msec_stamp = int((stamp_time.second * 1000) + (stamp_time.microsecond / 1000))

    if line:
        new_time = stamp_time
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
    else:
        throttle_output = throttle_output * 0.99

    if paused:
        print_string = "Paus %03d %03d %03d %05d %05d" % \
            (steering_output, throttle_output, threshold, msec_stamp, frame_cnt)
        throttle_output = 0
        steering_output = STEERING_OFFSET
        time.sleep(0.001)
    else:
        if line:
            print_string = " %03d %03d %03d %03d %05d %05d" % \
                (x, steering_output, throttle_output, threshold, msec_stamp, frame_cnt)
        else:
            print_string = "Lost %03d %03d %03d %05d %05d" % \
                (steering_output, throttle_output, threshold, msec_stamp, frame_cnt)

    set_servos(throttle_output, steering_output)

    if BINARY_VIEW:
        #frame_file_name = "%s/cam%05d.png" % (IMG_DIR, frame_cnt)
        res_file_name = "%s/res%05d.png" % (IMG_DIR, frame_cnt)
        frame_cnt += 1
        #cv2.imwrite(frame_file_name, frame)
        cv2.putText(frame, print_string, (10,FRAME_HEIGHT-(int(FRAME_HEIGHT/4))), font, 0.3, (150,150,255))
        if line:
            frame = cv2.line(frame, (x,0), (x,y), (0,255,0), 2)
        cv2.imwrite(res_file_name, frame)

    print("%06.2f %s\r" % (clock.get_fps(), print_string), end="")
