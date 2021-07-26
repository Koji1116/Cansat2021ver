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
        
        #if count > 8:
           # print('スタックもしくはこの場所が適切ではない')
           # stuck.stuck_avoid()

        
        if abs(theta) <= 60:
            
            print('theta = '+str(theta)+'---回転開始ver1')
            motor.move(20,-20, t_small )
        
        elif 60<theta  <=180:
            print('theta = '+str(theta)+'---回転開始ver2')
            motor.move(20,-20, t_big)    
        elif abs(theta) >= 300:
            
            print('theta = '+str(theta)+'---回転開始ver3')
            motor.move(-20,20, t_small)
        elif 180 <theta <=360:
            
            print('theta = '+str(theta)+'---回転開始ver4')
            motor.move(-20,20, t_big)
        time.sleep(3)
        count += 1
        data = Calibration.get_data()
        magx = data[0]
        magy = data[1]
        # --- 0 <= θ <= 360 ---#
        theta = Calibration.calculate_angle_2D(magx, magy, magx_off, magy_off)
        direction = Calibration.calculate_direction(lon2, lat2)
        azimuth = direction["azimuth1"]
        theta = azimuth-theta
        if theta <0:
            theta = 360+theta

    print('theta = '+str(theta)+'---回転終了!!!')


if __name__ == "__main__":
    mag.bmc050_setup()
    GPS.openGPS()
    print('Run Phase Start!')
    print('GPS走行開始')
    # --- difine goal latitude and longitude ---#
    lon2 = 139.9089035
    lat2 = 35.9185520

    # ------------- program start -------------#
    direction = Calibration.calculate_direction(lon2, lat2)
    goal_distance = direction['distance']
    print('goal distance = ' + str(goal_distance))
    # ------------- Calibration -------------#
    print('Calibration Start')
    # --- calculate offset ---#
    mag.bmc050_setup()
    ##-----------テスト用--------
    r = float(input('右の出力は？'))
    l = float(input('左の出力は？'))
    t = float(input('一回の回転時間は？'))
    n = int(input('データ何回？'))
    # --- calibration ---#
    magdata_Old = Calibration.magdata_matrix(l, r, t,n)
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
        time.sleep(0.5)
        theta = θ
        direction = Calibration.calculate_direction(lon2, lat2)
        azimuth = direction["azimuth1"]
        theta = azimuth-theta
        if theta <0:
            theta = 360+theta
        adjust_direction(theta)

        
        print('theta = '+str(theta)+'---直進開始')
        motor.move(50,50,5)

        # --- calculate  goal direction ---#
        direction = Calibration.calculate_direction(lon2, lat2)
        goal_distance = direction["distance"]
        print(str(goal_distance))
        
