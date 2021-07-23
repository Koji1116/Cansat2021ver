import sys
# このパス後で調整必要　by oosim
# ある程度調整したよ　07/11 takayama
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
import numpy as np
import gps_navigate
import Xbee
import BMC050
import GPS
import motor_koji
import motor
import stuck
import Calibration
import pigpio
import time
import traceback
from threading import Thread
# --- difine goal latitude and longitude ---#
lon2 = 139.90833592590076
lat2 = 35.91817558805946
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
    while abs(theta) > 30:
        print('回転'+str(count)+'回目開始')
        if abs(theta) <= 180:
            if abs(theta) <= 60:
                print('theta = '+str(theta)+'---回転開始ver1')
                motor.motor_move(np.sign(theta)*0.5, -1*np.sign(theta)*0.5, 3)
                motor.stop()

            elif abs(theta) <= 180:
                print('theta = '+str(theta)+'---回転開始ver2')
                motor.motor_move(-np.sign(theta)* 0.5, np.sign(theta)*0.5, 3)
                motor.motor_stop()
        elif abs(theta) > 180:
            if abs(theta) >= 300:
                print('theta = '+str(theta)+'---回転開始ver3')
                motor.motor_move(-np.sign(theta)* 0.5, np.sign(theta)*0.5, 5)
                motor.motor_stop()
            elif abs(theta) > 180:
                print('theta = '+str(theta)+'---回転開始ver4')
                motor.motor_move(np.sign(theta)*0.5, -np.sign(theta)*0.5, 5)
                motor.motor_stop()
        count += 1
        magdata = BMC050.mag_dataRead()
        mag_x = magdata[0]
        mag_y = magdata[1]
        theta = Calibration.angle(mag_x, mag_y, magx_off, magy_off)
        direction = Calibration.calculate_direction(lon2, lat2)
        azimuth = direction["azimuth1"]
        theta = theta-azimuth

    print('theta = '+str(theta)+'---回転終了!!!')


if __name__ == "__main__":
    BMC050.BMC050_setup()
    GPS.openGPS()
    print('Run Phase Start!')
    print('GPS走行開始')
    

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
        
