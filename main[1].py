#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

from threading import Thread
import struct
import random


controllerName = ''
controllerEvent = ''
DeviceNames = []
DeviceEvents = []

with open("/proc/bus/input/devices", 'r') as devices:

    for line in devices:

        if line[0] == 'N':
            name = line
            name = line.split('N: Name="')[1].split('"')[0].strip()
            DeviceNames.append(name)

        elif line[0] == 'H':
            ##print(line)
            event = line
            event = line.split('H: Handlers=')[1].strip()
            if 'kbd ' in event:
                event = event.split(' ')[1].strip()
            DeviceEvents.append(event)

try:
    controllerEvent = DeviceEvents[DeviceNames.index("Nintendo Wii Remote")]
    controllerName = "Nintendo Wii Remote"

except:

    try:
        controllerEvent = DeviceEvents[DeviceNames.index("Wireless Controller")]
        controllerName = "PS4 Controller"
    except:
        controllerEvent = ''
        controllerName = ''

print(DeviceNames, DeviceEvents)
item = 0
characterSelected = 0

# A helper function for converting stick values (0 to 255) to more usable numbers (-100 to 100)
def scale(val, src, dst):

    result = (float(val - src[0]) / (src[1] - src[0]))
    result = result * (dst[1] - dst[0]) + dst[0]
    return result
    
###  __    __  ____  ____ 
### |  |__|  ||    ||    |
### |  |  |  | |  |  |  | 
### |  `  '  | |  |  |  | 
###  \      /  |  |  |  | 
###   \_/\_/  |____||____|


def wiiInput():

    ## Wii Specific Buttons
    Wii_A = 304
    Wii_B = 305
    Wii_1 = 257
    Wii_2 = 258
    Wii_Minus = 412
    Wii_Plus = 407
    Wii_Home = 316
    Wii_Up = 103
    Wii_Down = 108
    Wii_Left = 105
    Wii_Right = 106

    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    wheel_diameter = 56
    axle_track = 114
    pen_angle = 0
    left_speed = 0
    right_speed = 0
    characters = ['mario','luigi','peach','toad','yoshi','dk','wario','bowser']
    ev3.screen.clear()
    ev3.screen.load_image(characters[0] + ".png")
    ev3.speaker.play_file("selectPlayer.wav")

    currentCharacter = 0
    left_speed = 0
    right_speed = 0

    forward = False
    backward = False
    turning = False

    boost = False
    slow = False
    spin = False

    global item
    global characterSelected
    

    ## cat /proc/bus/input/devices

    event = controllerEvent

    infile_path = "/dev/input/" + controllerEvent
    in_file = open(infile_path, "rb")
    FORMAT = 'llHHi'
    EVENT_SIZE = struct.calcsize(FORMAT)
    event = in_file.read(EVENT_SIZE)

    while event:

        (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)

        print (item)

        if item == 0:
            spin = False
            slow = False
            boost = False

        ## Boost
        if item == 1:
            spin = False
            slow = False
            boost = True

        ## Slow
        elif item == 2:
            spin = False
            slow = True
            boost = False

        ## Spin
        elif item == 3:
            spin = True
            slow = False
            boost = False

        # If a button was pressed or released
        if ev_type == 1:

            if characterSelected == 0:
                if code == Wii_Up and value == 1:
                    if currentCharacter > 0:
                        currentCharacter -= 1
                        ev3.screen.clear()
                        ev3.screen.load_image(characters[currentCharacter] + ".png")
                        wait(500)

                if code == Wii_Down and value == 1:
                    if currentCharacter < len(characters) -1:
                        currentCharacter += 1
                        ev3.screen.clear()
                        ev3.screen.load_image(characters[currentCharacter] + ".png")
                        wait(500)

                if code == Wii_2 and value == 1:
                    ev3.speaker.play_file(characters[currentCharacter] +".wav")
                    wait(500)
                    characterSelected = 1

            ### "PLUS BUTTON TO START RACE" --> 3 2 1 GO 


            else:
                

                ## 2 button Pressed (forward)
                if code == Wii_2 and value == 1:
                    forward = True
                    backward = False
                    left_speed = 100 * 0.8
                    right_speed = 100 * 0.8
                    
                ## 2 button Released (forward)
                elif code == Wii_2 and value == 0:
                    forward = False
                    backward = False
                    if turning == False:
                        left_speed = 0
                        right_speed = 0

                ## 1 button Pressed (backward)
                if code == Wii_1 and value == 1:
                    backward = True
                    forward = False
                    left_speed = -50
                    right_speed = -50
                ## 1 button Pressed (backward)
                if code == Wii_1 and value == 0:
                    backward = False
                    forward = False
                    if turning == False:
                        left_speed = 0
                        right_speed = 0
                    
                ## Down button pressed (turn right)
                if code == Wii_Down and value == 1:
                    turning = True
                    if forward == True:
                        left_speed = 100
                        right_speed = 50
                    if backward == True:
                        left_speed = -50
                        right_speed = -25
                    if backward == False and forward == False:
                        left_speed = 100
                        right_speed = 0
                ## Down button released (turn right)
                if code == Wii_Down and value == 0:
                    turning = False
                    if forward == True:
                        left_speed = 100
                        right_speed = 100
                    elif backward == True:
                        left_speed = -50
                        right_speed = -50
                    else:
                        left_speed = 0
                        right_speed = 0
                        
                ## Up button pressed (turn left)
                if code == Wii_Up and value == 1:
                    turning = True
                    if forward == True:
                        left_speed = 50
                        right_speed = 100
                    if backward == True:
                        left_speed = -25
                        right_speed = -50
                    if backward == False and forward == False:
                        left_speed = 0
                        right_speed = 100
                ## Up button released (turn left)
                if code == Wii_Up and value == 0:
                    turning = False
                    if forward == True:
                        left_speed = 100
                        right_speed = 100
                    elif backward == True:
                        left_speed = -50
                        right_speed = -50
                    else:
                        left_speed = 0
                        right_speed = 0

                ## Spin Test (A Button)
                ##if code == 304 and value == 1:
                    ##Spin2Win()
            
            ## This should stop it from crashing (threads)
            try:
                # Set motor speed

                ## Full Speed
                if boost == True:
                    left_motor.dc(left_speed)
                    right_motor.dc(right_speed)

                ## Slow Speed
                elif slow == True:
                    left_motor.dc(left_speed * 0.6)
                    right_motor.dc(right_speed * 0.6)

                ## Spin 360 degrees for 2 seconds
                elif spin == True:
                    robot = DriveBase(Motor(Port.B), Motor(Port.C), 56, 114)
                    robot.drive_time(0, 360, 2000)
                    robot.stop()

                ## Normal Driving Mode (80% speed)
                else:
                    left_motor.dc(left_speed * 0.8)
                    right_motor.dc(right_speed * 0.8)
            except:
                pass
        event = in_file.read(EVENT_SIZE)
    in_file.close()


##  _____   _____   _  _   
## |  __ \ / ____| | || |  
## | |__) | (___   | || |_ 
## |  ___/ \___ \  |__   _|
## | |     ____) |   | |  
## |_|    |_____/    |_|  
                       



def ps4Input():
    ## PS4 Specific Input
    PS4_X = 304
    PS4_O = 305
    PS4_Triangle = 307 
    PS4_Square = 308
    PS4_L1 = 310
    PS4_L2 = 312
    PS4_R1 = 311
    PS4_R2 = 313

    ## Dpad uses -1, 0, 1 in value for each axis
    PS4_DX = 16
    PS4_DY = 17

    PS4_LAnX = 0
    PS4_LAnY = 1

    PS4_RAnX = 3
    PS4_RAnY = 4

    ev3 = EV3Brick()
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
    wheel_diameter = 56
    axle_track = 114
    pen_angle = 0
    left_speed = 0
    right_speed = 0
    characters = ['mario','luigi','peach','toad','yoshi','dk','wario','bowser']
    ev3.screen.clear()
    ev3.screen.load_image(characters[0] + ".png")
    ev3.speaker.play_file("selectPlayer.wav")

    currentCharacter = 0
    left_speed = 0
    right_speed = 0

    forward = False
    backward = False
    turning = False

    boost = False
    slow = False
    spin = False

    global item
    global characterSelected
    

    ## cat /proc/bus/input/devices
    event = controllerEvent

    infile_path = "/dev/input/" + controllerEvent
    in_file = open(infile_path, "rb")
    FORMAT = 'llHHi'
    EVENT_SIZE = struct.calcsize(FORMAT)
    event = in_file.read(EVENT_SIZE)

    while event:

        (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)

        if item == 0:
            spin = False
            slow = False
            boost = False

        ## Boost
        if item == 1:
            spin = False
            slow = False
            boost = True

        ## Slow
        elif item == 2:
            spin = False
            slow = True
            boost = False

        ## Spin
        elif item == 3:
            spin = True
            slow = False
            boost = False

        if characterSelected == 0:

            ## Dpad is considered an axis
            if ev_type == 3:

                ## Left
                if code == PS4_DX and value == -1:
                    if currentCharacter > 0:
                        currentCharacter -= 1
                        ev3.screen.clear()
                        ev3.screen.load_image(characters[currentCharacter] + ".png")
                        wait(500)

                ## Right
                if code == PS4_DX and value == 1:
                    if currentCharacter < len(characters) -1:
                        currentCharacter += 1
                        ev3.screen.clear()
                        ev3.screen.load_image(characters[currentCharacter] + ".png")
                        wait(500)

            ## Check buttons
            elif ev_type == 1:
                if code == PS4_X and value == 1:
                    ev3.speaker.play_file(characters[currentCharacter] +".wav")
                    wait(500)
                    characterSelected = 1


        ## Character has been selected, prepare movement
        else:

            if ev_type == 1:

                ## R2 button Pressed (forward)
                if code == PS4_R2 and value == 1:
                    forward = True
                    backward = False
                    left_speed = 100 * 0.8
                    right_speed = 100 * 0.8
                    
                ## R2 button Released (forward)
                elif code == PS4_R2 and value == 0:
                    forward = False
                    backward = False
                    if turning == False:
                        left_speed = 0
                        right_speed = 0

                ## L2 button Pressed (backward)
                elif code == PS4_L2 and value == 1:
                    backward = True
                    forward = False
                    left_speed = -50
                    right_speed = -50

                ## L2 button Released (backward)
                elif code == PS4_L2 and value == 0:
                    backward = False
                    forward = False
                    if turning == False:
                        left_speed = 0
                        right_speed = 0

            ## Analog Stick Control
            elif ev_type == 3:

                if code == PS4_LAnX:
                    xAxis = scale(value, (0, 255), (100, -100))

                    ## Left = 100
                    ## Right = -100
                    ## Neutral = 0

                    ## Left Turn (50% deadzone so it's not too sensitive)
                    if xAxis > 50:
                        turning = True
                        if forward == True:
                            left_speed = abs(xAxis) * 0.5
                            right_speed = abs(xAxis)
                        if backward == True:
                            left_speed = -abs(xAxis) * 0.25
                            right_speed = -abs(xAxis) * 0.5
                        if backward == False and forward == False:
                            left_speed = 0
                            right_speed = abs(xAxis)

                    ## Right Turn (50% deadzone so it's not too sensitive)
                    elif xAxis < -50:
                        turning = True
                        if forward == True:
                            left_speed = abs(xAxis)
                            right_speed = abs(xAxis) * 0.5
                        if backward == True:
                            left_speed = -abs(xAxis) * 0.5
                            right_speed = -abs(xAxis) * 0.25
                        if backward == False and forward == False:
                            left_speed = abs(xAxis)
                            right_speed = 0

                    ## Stick in Neutral Zone 
                    else:
                        turning = False
                        if forward == True:
                            left_speed = 100
                            right_speed = 100
                        elif backward == True:
                            left_speed = -50
                            right_speed = -50
                        else:
                            left_speed = 0
                            right_speed = 0


                ## D-Pad Control Turn Left
                elif code == PS4_DX and value == -1:
                    turning = True
                    if forward == True:
                        left_speed = 50
                        right_speed = 100
                    if backward == True:
                        left_speed = -25
                        right_speed = -50
                    if backward == False and forward == False:
                        left_speed = 0
                        right_speed = 100

                ## D-Pad Control Turn Right
                elif code == PS4_DX and value == 1:
                    turning = True
                    if forward == True:
                        left_speed = 100
                        right_speed = 50
                    if backward == True:
                        left_speed = -50
                        right_speed = -25
                    if backward == False and forward == False:
                        left_speed = 100
                        right_speed = 0

                ## Released Dpad
                elif code == PS4_DX and value == 0:
                    turning = False
                    if forward == True:
                        left_speed = 100
                        right_speed = 100
                    elif backward == True:
                        left_speed = -50
                        right_speed = -50
                    else:
                        left_speed = 0
                        right_speed = 0

            ## This should stop it from crashing (threads)
            try:
                ## Full Speed
                if boost == True:
                    left_motor.dc(left_speed)
                    right_motor.dc(right_speed)

                ## Slow Speed
                elif slow == True:
                    left_motor.dc(left_speed * 0.6)
                    right_motor.dc(right_speed * 0.6)

                ## Spin 360 degrees for 2 seconds
                elif spin == True:
                    robot = DriveBase(Motor(Port.B), Motor(Port.C), 56, 114)
                    robot.drive_time(0, 360, 2000)
                    robot.stop()

                ## Normal Driving Mode (80% speed)
                else:
                    left_motor.dc(left_speed * 0.8)
                    right_motor.dc(right_speed * 0.8)
            except:
                pass
        event = in_file.read(EVENT_SIZE)
    in_file.close()

## Run WiiInput Thread if Wiimote is connected
if controllerName == "Nintendo Wii Remote":
    t = Thread(target=wiiInput)
    t.start()

## Otherwise run PS4Input THread is a PS4 Controller is connected
elif controllerName == "PS4 Controller":
    t = Thread(target=ps4Input)
    t.start()


while True:

    ## Wait until the character is selected before begining item selection

    if characterSelected == 1:

        ## Generate item every 10 seconds
        wait(10000)
        item = random.randint(1,3)
        

        ## Boost is 1, Slow is 2, Spin is 3
        if item == 1:
            EV3Brick().speaker.play_file('starman.wav')
            wait(1000)

        ## Slow Down for 5 seconds
        if item == 2:
            EV3Brick().speaker.play_notes(['E2/4', 'E2/4', 'E2/4'], tempo=320)
            wait(3000)

        ## Spin Once (set to 0 to stop spinning)
        
        if item == 3:
            EV3Brick().speaker.play_notes(['C4/4', 'C4/4', 'G4/4', 'G4/4'], tempo=220)
            wait(500)

        item = 0
