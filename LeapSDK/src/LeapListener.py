import os, sys
sys.path.insert(0, "../lib")
sys.path.insert(0, "../lib/x64")

import Leap, thread, time, serial
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

from inverse_kinematics import end_effector_position, calculateInverseKinematics


PRINT = 0
PINCER_ANGLE = 50
VEL_SCALE = 0.4
FRAME_PAUSE = 1.6 # in seconds

COM_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

class LeapListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        print "Initialized"
        self.serialConnection = None 
        self.previous_angles = []
        self.previous_wrist_position = Leap.Vector(0,0,0)
        self.theta1 = 0;
        self.theta2 = 0;
        self.theta3 = 0;

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
        if self.is_fist(hand) == True:
            return '40' #closed
        else:
            return '0'

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # Get hands
        for hand in frame.hands:

            # No left hand inputs allowed
            if hand.is_left: 
                # if a left hand is detected, then reset
                print("Left hand shown, reset robot arm")
                angles = "0 0 20 0 0 0"
                self.serialConnection.write(angles)
                time.sleep(2.0)
                break
 
            # We need to return the palm position, or alternatively the wrist position
            hand.palm_position
            
            
            # We need to return direction vector of the hand
            hand.direction

            # Return the state of the fist
            self.is_fist(hand)

            # We need to return the direction vector of the arm
            hand.arm.direction
            # the yaw can be deduced from this

            wrist_movement_direction = Leap.Vector(0,0,0)

            if self.previous_wrist_position != Leap.Vector(0,0,0):
                wrist_movement_direction = hand.arm.wrist_position - self.previous_wrist_position; 
            
            # move it forward
            self.theta1 = self.theta1 - wrist_movement_direction.z*VEL_SCALE
            self.theta2 = self.theta2 - wrist_movement_direction.y*VEL_SCALE
            #self.theta3 = self.theta3 - wrist_movement_direction.y*VEL_SCALE
            print(wrist_movement_direction)
            
            self.previous_wrist_position = hand.arm.wrist_position

            # Call Richard's math function
            #theta_values = end_effector_position(hand.arm.wrist_position, hand.direction)

            #theta1, theta2 = calculateInverseKinematics(hand.arm.wrist_position.y, -hand.arm.wrist_position.z)
           
            if self.is_fist(hand) == True:
                pincer_value = PINCER_ANGLE
            else:
                pincer_value = 0


            angles = "0 " + str(self.theta1) + " " + str(20+self.theta1) + " " + str(self.theta2) + " " + "0 " + str(pincer_value)


            #angles.strip()
            print(angles)
            self.serialConnection.write(angles)
            time.sleep(FRAME_PAUSE)

