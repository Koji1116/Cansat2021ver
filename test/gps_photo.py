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
import goaldetection
import Capture

#写真内の赤色面積で進時間を決める用　調整必要
area_short = 100
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
    print('ゴールとの角度theta = ' + str(theta) + '---回転調整開始！')

    count = 0
    t_small = 0.1
    t_big = 0.2
    while 15 < theta < 345:

        # if count > 8:
        # print('スタックもしくはこの場所が適切ではない')
        # stuck.stuck_avoid()

        if theta <= 60:

            print('theta = ' + str(theta) + '---回転開始ver1')
            motor.move(20, -20, t_small)

        elif 60 < theta <= 180:
            print('theta = ' + str(theta) + '---回転開始ver2')
            motor.move(20, -20, t_big)
        elif theta >= 300:

            print('theta = ' + str(theta) + '---回転開始ver3')
            motor.move(-20, 20, t_small)
        elif 180 < theta < 360:

            print('theta = ' + str(theta) + '---回転開始ver4')
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
        print('計算後のゴールとなす角度theta' + str(theta))

    print('theta = ' + str(theta) + '---回転終了!!!')

if __name__ == "__main__":
    mag.bmc050_setup()
    GPS.openGPS()
    print('Run Phase Start!')
    print('GPS走行開始')
    # --- difine goal latitude and longitude ---#
    lon2 = 139.9105443
    lat2 = 35.9233106

    # ------------- program start -------------#
    direction = Calibration.calculate_direction(lon2, lat2)
    goal_distance = direction['distance']
    aaa = direction['azimuth1']
    print('goal distance = ' + str(goal_distance))
    print('goal direction = ' + str(aaa))
    count = 0
    ##-----------テスト用--------
    r = float(input('右の出力は？'))
    l = float(input('左の出力は？'))
    t = float(input('何秒回転する？'))
    n = int(input('データ数いくつ'))
    while goal_distance >= 10:
        if count % 4 == 0:
            # ------------- Calibration -------------#
            print('Calibration Start')
            mag.bmc050_setup()
            ##-----------テスト用--------
            r = float(input('右の出力は？'))
            l = float(input('左の出力は？'))
            t = float(input('難病回転する？'))
            n = int(input('データ数いくつ'))
            magdata_Old = Calibration.magdata_matrix(l, r, t, n)
            _, _, _, magx_off, magy_off, _ = Calibration.calculate_offset(magdata_Old)
        print('GPS run strat')
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
        print('theta = ' + str(theta) + '---直進開始')
        ######直進するように左の出力強くしてます↓ 7/28 by oosima
        motor.move(65, 50, 6)

        # --- calculate  goal direction ---#
        direction = Calibration.calculate_direction(lon2, lat2)
        goal_distance = direction["distance"]
        print('------ゴールとの距離は' + str(goal_distance) + 'm------')
        count += 1

    #-----------photo_run------------#
    while goalflug != 0:
        photoName = Capture.Capture(path, 320, 320)  # 解像度調整するところ？
        goalflug, goalarea, gap, imgname = goaldetection.GoalDetection(photoName, 200, 20, 80, 50)
        print(f'goalflug:{goalflug}\tgoalarea:{goalarea}%\tgap:{gap}\timagename:{imgname}')
        # Xbee.str_trans('goalflug', goalflug, ' goalarea', goalarea, ' goalGAP', goalGAP)
        # Other.saveLog(path,startTime - time.time(), goalflug, goalarea, goalGAP)
        if -100 <= gap and gap <= -65:  # 調整するところ
            print('Turn left')
            # Xbee.str_trans('Turn left')
            motor.move(-40, 40, 0.1)  # 調整するところ
            # print('motor.motor(-0.2, 0.2, 0.3)')
        elif 65 <= gap and gap <= 100:
            print('Turn right')
            # Xbee.str_trans('Turn right')
            motor.move(40, -40, 0.1)  # 調整するところ
            # print('motor.motor(0.2, -0.2, 0.3)')
        elif gap == 1000 or gap == 1000000:
            print('Nogoal detected')
            motor.move(40, -40, 0.1)  # 調整するところ
            # print('motor.motor(0.2, -0.2, 0.5)')
        else:
            print('Go straight')
            if goalarea <= area_long:
                motor.move(80, 80, 3)  # 調整するところ
                # print('motor.motor(1, 1, 10)')
                print('long')
            elif goalarea <= area_middle:
                motor.move(80, 80, 1)  # 調整するところ
                # print('motor.motor(1, 1, 5)')
                print('middle')
            elif goalarea <= area_short:
                motor.move(80, 80, 0.2)  # 調整するところ
                # print('motor.motor(1, 1, 2)')
                print('short')