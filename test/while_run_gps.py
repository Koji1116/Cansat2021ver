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

lon2 = 139.9114415
lat2 = 35.9236391
run_l = 0
run_r = 0
run = 0



def adjust_direction(theta):
    global magx_off
    global magy_off
    """
    方向調整
    """
    print('ゴールとの角度theta = ' + str(theta) + '---回転調整開始！')

    stuck_count = 1
    t_small = 0.1
    t_big = 0.2
    force = 20 
    while 15 < theta < 345:
        if stuck_count >= 7:
            print('出力強くするよ')
            force +=10
        # if count > 8:
        # print('スタックもしくはこの場所が適切ではない')
        # stuck.stuck_avoid()

        if theta <= 60:

            print('theta = ' + str(theta) + '---回転開始ver1('+str(stuck_count)+'回目)')
            motor.move(force, -force, t_small)

        elif 60 < theta <= 180:
            print('theta = ' + str(theta) + '---回転開始ver2('+str(stuck_count)+'回目)')
            motor.move(force, -force, t_big)
        elif theta >= 300:

            print('theta = ' + str(theta) + '---回転開始ver3('+str(stuck_count)+'回目)')
            motor.move(-force, force, t_small)
        elif 180 < theta < 360:

            print('theta = ' + str(theta) + '---回転開始ver4('+str(stuck_count)+'回目)')
            motor.move(-force, force, t_big)
    
        stuck_count += 1
        data = Calibration.get_data()
        magx = data[0]
        magy = data[1]
        # --- 0 <= θ <= 360 ---#
        theta = Calibration.angle(magx, magy, magx_off, magy_off)
        direction = Calibration.calculate_direction(lon2, lat2)
        azimuth = direction["azimuth1"]
        theta = azimuth - theta
        if theta < 0:
            theta = 360 + theta
        elif 360 <= theta <= 450:
            theta = theta - 360
        print('計算後のゴールとなす角度theta' + str(theta))
        time.sleep(1)

    print('theta = ' + str(theta) + '---回転終了!!!')


GPS.openGPS()
acc.bmc050_setup()
n = float(input('何秒間走る？'))

##calibration
r = float(input('右の出力は？'))
l = float(input('左の出力は？'))
t = float(input('何秒回転する？'))
n = int(input('データ数いくつ'))
if stuck.ue_jug():
    print('上だよ')
    pass
else:
    print('したーーーー')
    motor.move(12, 12, 0.2)
# ------------- Calibration -------------#
print('Calibration Start')
mag.bmc050_setup()
magdata_Old = Calibration.magdata_matrix(l, r, t, n)
_, _, _, magx_off, magy_off, _ = Calibration.calculate_offset(magdata_Old)


magdata = BMC050.mag_dataRead()
mag_x = magdata[0]
mag_y = magdata[1]
theta = Calibration.angle(mag_x, mag_y, magx_off, magy_off)
direction = Calibration.calculate_direction(lon2, lat2)
azimuth = direction["azimuth1"]
theta = azimuth - theta
if theta < 0:
    theta = 360 + theta
elif 360 <= theta <= 450:
    theta = theta - 360
adjust_direction(theta)

while 1:
    
    # print('----------------')
    # old = acc.acc_dataRead()
    # print(f'old {old}')
    # motor.motor_move(30, 30, n)
    # new = acc.acc_dataRead()
    # print(f'new {new}')

    GPSdata_old = GPS.GPSdata_read()
    motor.motor_move(30 + run, 30 - run, n)
    GPSdata_new = GPS.GPSdata_read()
    if stuck.stuck_jug(GPSdata_old[1], GPSdata_old[2], GPSdata_new[1], GPSdata_new[2], 1.0):
        pass
    else:
        pass
    direction = Calibration.calculate_direction(lon2, lat2)
    azimuth = direction['azimuth1']
    if 0 <= azimuth <= 15 or 345 <= azimuth <= 360:
        print(0)
        pass
    elif azimuth>15:
        print(1)
        run = 15
    elif azimuth < 345:
        run = -15
        print(-1)