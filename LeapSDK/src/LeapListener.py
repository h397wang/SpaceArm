import os, sys
sys.path.insert(0, "../lib")
sys.path.insert(0, "../lib/x64")

import Leap, thread, time, serial
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

from inverse_kinematics import end_effector_position

PRINT = 0

COM_PORT = 'COM3'
BAUD_RATE = 9600

class LeapListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        print "Initialized"
        self.serialConnection = None 
        self.previous_angles = []

    def on_connect(self, controller):
        print "Connected"
        self.serialConnection = serial.Serial(COM_PORT, BAUD_RATE)
        

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    # For some reason the axis are reversed?? works for now
    def is_fist(self, hand):
        for finger in hand.fingers: # skip the thumb
            if self.finger_names[finger.type] == "Thumb": # skip thumb
                thumb_distal = finger.bone(3)
                if thumb_distal.direction.x < 0:
                    #print("Right thumb is pointing right")
                    print("");
                else:
                    #print("Right thumb is pointing left")
                    return False
            else:
                distal = finger.bone(3) # distal is the tip bone
                #print(distal.direction)
                if distal.direction.z < 0:
                    #print("finger is pointing towards user")
                    print("");
                else:
                    #print("finger is pointing away from user")
                    return False
        print("Fist detected")
        return True # Hand is making a fist

    def angle(self, hand):
        if self.is_fist(hand) is True:
            return '180'
        else:
            return '0'

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # Get hands
        for hand in frame.hands:

            # No left hand inputs allowed
            if hand.is_left: 
                break
 
            # We need to return the palm position, or alternatively the wrist position
            hand.palm_position
            hand.arm.wrist_position
            
            # We need to return direction vector of the hand
            hand.direction

            # Return the state of the fist
            self.is_fist(hand)

            # We need to return the direction vector of the arm
            hand.arm.direction
            # the yaw can be deduced from this
            
            # Call Richard's math function
            theta_values = end_effector_position(hand.arm.wrist_position, hand.direction)
            if theta_values == None:
                return

            angles =  self.angle(hand) + ', ' + str(theta_values).strip("[]") 
     
            # compare to previous angles
            # angle_adjusted limit the delta values
            if self.serialConnection == None:
                print("No serial connection")
            else:
                self.serialConnection.write(angles)

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

