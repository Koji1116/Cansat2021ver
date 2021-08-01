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

#写真内の赤色面積で進時間を決める用　調整必要
area_short = 20
area_middle = 6
area_long = 1

G_thd = 80  # 調整するところ
goalflug = 1
startTime = time.time()
dateTime = datetime.datetime.now()
path = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}:{dateTime.minute}'


def adjust_direction(theta):
    global magx_off
    global magy_off
    """
    方向調整
    """
    Xbee.str_trans('ゴールとの角度theta = ' + str(theta) + '---回転調整開始！')

    count = 0
    t_small = 0.1
    t_big = 0.2
    while 15 < theta < 345:

        # if count > 8:
        # Xbee.str_trans('スタックもしくはこの場所が適切ではない')
        # stuck.stuck_avoid()

        if theta <= 60:

            Xbee.str_trans('theta = ' + str(theta) + '---回転開始ver1')
            motor.move(20, -20, t_small)

        elif 60 < theta <= 180:
            Xbee.str_trans('theta = ' + str(theta) + '---回転開始ver2')
            motor.move(20, -20, t_big)
        elif theta >= 300:

            Xbee.str_trans('theta = ' + str(theta) + '---回転開始ver3')
            motor.move(-20, 20, t_small)
        elif 180 < theta < 360:

            Xbee.str_trans('theta = ' + str(theta) + '---回転開始ver4')
            motor.move(-20, 20, t_big)

        # count += 1
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
        Xbee.str_trans('計算後のゴールとなす角度theta' + str(theta))

    Xbee.str_trans('theta = ' + str(theta) + '---回転終了!!!')

if __name__ == "__main__":
    mag.bmc050_setup()
    GPS.openGPS()
    Xbee.str_trans('Run Phase Start!')
    Xbee.str_trans('GPS走行開始')
    # --- difine goal latitude and longitude ---#
    lon2 = 139.9082128
    lat2 = 35.9185224

    # ------------- program start -------------#
    direction = Calibration.calculate_direction(lon2, lat2)
    goal_distance = direction['distance']
    aaa = direction['azimuth1']
    Xbee.str_trans('goal distance = ' + str(goal_distance))
    Xbee.str_trans('goal direction = ' + str(aaa))
    count = 0
    ##-----------テスト用--------
    r = float(input('右の出力は？'))
    l = float(input('左の出力は？'))
    t = float(input('何秒回転する？'))
    n = int(input('データ数いくつ'))
    while goal_distance >= 10:
        if count % 4 == 0:
            # ------------- Calibration -------------#
            Xbee.str_trans('Calibration Start')
            mag.bmc050_setup()
            magdata_Old = Calibration.magdata_matrix(l, r, t, n)
            _, _, _, magx_off, magy_off, _ = Calibration.calculate_offset(magdata_Old)
        Xbee.str_trans('GPS run strat')
        # ------------- GPS navigate -------------#
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
        Xbee.str_trans('theta = ' + str(theta) + '---直進開始')
        ######直進するように左の出力強くしてます↓ 7/28 by oosima
        motor.move(65, 50, 6)

        # --- calculate  goal direction ---#
        direction = Calibration.calculate_direction(lon2, lat2)
        goal_distance = direction["distance"]
        Xbee.str_trans('------ゴールとの距離は' + str(goal_distance) + 'm------')
        count += 1
    Xbee.str_trans('!!!!!GPS走行終了。次は画像誘導!!!!!!!!!!!!')

    #-----------photo_run------------#
    goalflug = 1
    startTime = time.time()
    dateTime = datetime.datetime.now()
    path_photo_imagerun = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}:{dateTime.minute}'
    photorunning2.image_guided_driving(path_photo_imagerun, 50)