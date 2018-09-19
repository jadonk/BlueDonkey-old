#!/usr/bin/env python3
# Run the motors
# Based on: https://github.com/mcdeoliveira/rcpy/raw/master/examples/rcpy_test_motors.py
# import python libraries

import rcpy
import rcpy.motor as motor
import sys
import time

class Manual:
    
    # CONSTANT VARIABLES #
     # CONTROL CONSTANTS #
    BACKWARD = "\033[B" # Down
    FORWARD = "\033[A" # Up
    KILLSWITCH = "^C" # Select
    LEFT = "\033[D" # Left
    RIGHT = "\033[C" # Right
    SELECT_MODE = "3" # Start / Pause
    THROTTLE_DOWN = "4" # Left Trigger
    THROTTLE_UP = "6" # Right Trigger
    
     # THROTTLE CONSTANTS (Forward and Backward) #
    DIRECTION_THROTTLE_BACKWARD = -1 # Negative to go backward
    DIRECTION_THROTTLE_FORWARD = 1 # Positive to go forward
    DIRECTION_THROTTLE_DEFAULT = DIRECTION_THROTTLE_FORWARD # The direction to start travelling in
    DUTY_THROTTLE_MAX = 1.0 # Max duty allowed for throttle
    DUTY_THROTTLE_STEPS = 10 # Number of 'gears' to max throttle
    DUTY_THROTTLE_ITERATION_VALUE = DUTY_THROTTLE_MAX / DUTY_THROTTLE_STEPS
    
     # TURN CONSTANTS (Left and Right) #
    DIRECTION_TURN_CENTER = 0 # Directional value to keep wheels straight
    DIRECTION_TURN_DEFAULT = DIRECTION_TURN_CENTER # The direction the wheels start in
    DIRECTION_TURN_LEFT = 1 # Directional value to turn wheels towards the left
    DIRECTION_TURN_RIGHT = -1 # Directional value to turn wheels towards the right
    DUTY_TURN_MAX = 1.0 # Max duty allowed for turning
    DUTY_TURN_STEPS = 30 # Number of steps before reaching max turn radius
    DUTY_TURN_ITERATION_VALUE = DUTY_TURN_MAX / DUTY_TURN_STEPS

    # CONSTRUCTOR #
    def __init__(self):
        self.direction = self.DIRECTION_THROTTLE_DEFAULT
        self.direction_turn = self.DIRECTION_TURN_DEFAULT
        self.duty_throttle = 0
        self.duty_turn = 0
        rcpy.set_state(rcpy.RUNNING)
        print("Manual Initiated.")
    
    def change_direction(self, direction):
        if abs(direction) == 1: # Check if direction is either 1 or -1
            self.duty_throttle = 0 # Stop first
            self.direction = direction
    
    def check_hold(self, direction):
        if abs(direction) == 1 or direction == 0: # Check if direction is either 1, -1 or 0
            if self.direction_turn != direction: # If the input direction doesn't match the previously chosen...
                self.direction_turn = direction # ...change to new direction
                self.duty_turn = 0 # and reset the turn duty
            
    def decrease_throttle(self):
        if self.duty_throttle >= self.DUTY_THROTTLE_ITERATION_VALUE: # Check if duty is at least what will be subtracted
            self.duty_throttle = self.duty_throttle - self.DUTY_THROTTLE_ITERATION_VALUE # Iterate negatively
        else: # Duty is less than iteration value
            self.duty_throttle = 0 # Set duty to min

    def increase_throttle(self):
        if self.duty_throttle <= self.DUTY_THROTTLE_MAX - self.DUTY_THROTTLE_ITERATION_VALUE: # Check if duty is at most one iteration from max
            self.duty_throttle = self.duty_throttle + self.DUTY_THROTTLE_ITERATION_VALUE #Iterate Positively
        else: # Duty is greater than one iteration from max
            self.duty_throttle = self.DUTY_THROTTLE_MAX # Set duty to max

    def get_duty_throttle(self):
        return self.duty_throttle * self.direction # Return duty in the current direction
    
    def get_duty_turn(self):
        return self.duty_turn * self.direction_turn # Return duty in the current direction
    
    def kill(self):
        self.direction = 1
        self.direction_turn = 0
        self.duty_throttle = 0
        self.duty_turn = 0
        motor.set(1, 0)
        motor.set(2, 0)
        print("Killswitch activated.")
    
    def read_key(self):
        key = sys.stdin.read(1)
        if ord(key) == 27:
            key = key + sys.stdin.read(2)
        elif ord(key) == 3:
            raise KeyboardInterrupt    
        return key
    
    def turning(self, key):
        # TODO: Use 'keyboard' module to read multiple keys at once
        if (key == self.LEFT) ^ (key == self.RIGHT): # If keystrokes contain -EITHER- LEFT or RIGHT...
            if key == self.LEFT: # If it's LEFT
                self.check_hold(self.DIRECTION_TURN_LEFT)
            else: # If it's RIGHT
                self.check_hold(self.DIRECTION_TURN_RIGHT)
                
            if self.duty_turn <= self.DUTY_TURN_MAX - self.DUTY_TURN_ITERATION_VALUE: # If the next iteration is at most one iteration from max duty...
                self.duty_turn = self.duty_turn + self.DUTY_TURN_ITERATION_VALUE # Iterate
            else: # Value is greater than one iteration away from max duty
                self.duty_turn = self.DUTY_TURN_MAX # Set duty to its max value
        else: # Neither or both directions selected
            self.check_hold(self.DIRECTION_TURN_CENTER) # Set direction to straight and reset duty
            
try:
    m = Manual()

    m.change_direction(m.DIRECTION_THROTTLE_BACKWARD)
    m.increase_throttle()
    
    while rcpy.get_state() != rcpy.EXITING:
        
        m.turning(m.LEFT)
        motor.set(1, m.get_duty_turn())
        motor.set(2, m.get_duty_throttle())
        
        time.sleep(.1)  # sleep some

except KeyboardInterrupt:
    m.kill()
    pass
    
finally:
    print("\nBye BeagleBone!")