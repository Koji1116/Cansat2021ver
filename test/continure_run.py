import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Casnat2021ver/Detection')
import numpy as np
import GPS_Navigate
import Xbee
import BMC050
import GPS
import motor
import Calibration
import pigpio
from gpiozero import Motor
import time
import traceback
from threading import Thread
import math
import mag
import datetime
# import goaldetection
import Capture
import photorunning2
import stuck
import acc







motor.setup()

run = int(input('出力調整はいくつ'))
while 1:
    
    # print('----------------')
    # old = acc.acc_dataRead()
    # print(f'old {old}')
    # motor.motor_move(30, 30, n)
    # new = acc.acc_dataRead()
    # print(f'new {new}')
    a = input('入力')
    if a == 'w':
        motor.motor_continue(30,30)
    elif a == 'a':
        motor.motor_continue(30 - run,30 + run)
    elif a == 'd':
        motor.motor_continue(30 + run,30 - run)
    elif a == 's':
        motor.motor_continue(-30,-30)
    
    
    