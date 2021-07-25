import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
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


# --- original module ---#

# --- must be installed module ---#
# import numpy as np

# --- default module ---#
# import difflib

GPS_data = [0.0, 0.0, 0.0, 0.0, 0.0]


def timer(t):
    global cond
    time.sleep(t)
    cond = False


def adjust_direction(theta):
    """
    方向調整
    """
    print('theta = '+str(theta)+'---回転調整開始！')
    count = 0
    t_small = 0.1
    t_big = 0.2
    while abs(theta) > 30:
        print(str(count))
        
        #if count > 8:
           # print('スタックもしくはこの場所が適切ではない')
           # stuck.stuck_avoid()

        if abs(theta) <= 180:
            if abs(theta) <= 60:
                
                print('theta = '+str(theta)+'---回転開始ver1')
                motor.move(20,-20, t_small )
            
            else:
                print('theta = '+str(theta)+'---回転開始ver2')
                motor.move(20,-20, t_big)
                
        elif abs(theta) > 180:
            if abs(theta) >= 300:
                
                print('theta = '+str(theta)+'---回転開始ver3')
                motor.move(-20,20, t_small)
                
            else:
                
                print('theta = '+str(theta)+'---回転開始ver4')
                motor.move(-20,20, t_big)
               
        count += 1
        data = Calibration.get_data()
        magx = data[0]
        magy = data[1]
        # --- 0 <= θ <= 360 ---#
        theta = Calibration.calculate_angle_2D(magx, magy, magx_off, magy_off)
        direction = Calibration.calculate_direction(lon2, lat2)
        azimuth = direction["azimuth1"]
        theta = theta-azimuth

    print('theta = '+str(theta)+'---回転終了!!!')


if __name__ == "__main__":
    mag.bmc050_setup()
    GPS.openGPS()
    print('Run Phase Start!')
    print('GPS走行開始')
    # --- difine goal latitude and longitude ---#
    lon2 = 139.90833592590076
    lat2 = 35.91817558805946

    # ------------- program start -------------#
    direction = Calibration.calculate_direction(lon2, lat2)
    goal_distance = direction['distance']
    print('goal distance = ' + str(goal_distance))
    # ------------- Calibration -------------#
    print('Calibration Start')
    # --- calculate offset ---#
    BMC050.bmc050_setup()
    ##-----------テスト用--------
    r = float(input('右の出力は？'))
    l = float(input('左の出力は？'))
    t = float(input('一回の回転時間は？'))
    # --- calibration ---#
    magdata_Old = Calibration.magdata_matrix(l, r, t)
    magx_array_Old, magy_array_Old, magz_array_Old, magx_off, magy_off, magz_off = Calibration.calculate_offset(magdata_Old)
    time.sleep(0.1)
    print('GPS run strat')
    # ------------- GPS navigate -------------#
    while 1:  # この値調整必要

        

        #----
        magdata = BMC050.mag_dataRead()
        mag_x = magdata[0]
        mag_y = magdata[1]
        θ = Calibration.angle(mag_x, mag_y, magx_off, magy_off)
        print(mag_x,mag_y)
        print(θ)
        time.sleep(0.5)
        theta = θ
        adjust_direction(theta)

        
        print('theta = '+str(theta)+'---直進開始')
        motor_koji.motor_koji(0.8,0.8,6)

        # --- calculate  goal direction ---#
        direction = Calibration.calculate_direction(lon2, lat2)
        goal_distance = direction["distance"]
        print(str(goal_distance))
        
