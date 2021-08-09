import datetime
import sys

sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Casnat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Casnat2021ver/Other')
import numpy as np
import GPS_Navigate
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
import stuck
import acc
import Xbee
import Other

lon2 = 139.908905
lat2 = 35.918543
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
            force += 10
        # if count > 8:
        # print('スタックもしくはこの場所が適切ではない')
        # stuck.stuck_avoid()

        if theta <= 60:

            print('theta = ' + str(theta) + '---回転開始ver1(' + str(stuck_count) + '回目)')
            motor.move(force, -force, t_small)

        elif 60 < theta <= 180:
            print('theta = ' + str(theta) + '---回転開始ver2(' + str(stuck_count) + '回目)')
            motor.move(force, -force, t_big)
        elif theta >= 300:

            print('theta = ' + str(theta) + '---回転開始ver3(' + str(stuck_count) + '回目)')
            motor.move(-force, force, t_small)
        elif 180 < theta < 360:

            print('theta = ' + str(theta) + '---回転開始ver4(' + str(stuck_count) + '回目)')
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


##calibration
def gps_run():
    t_tyousei = float(input('何秒おきにキャリブレーションする？'))

    direction = Calibration.calculate_direction(lon2, lat2)
    goal_distance = direction["distance"]
    while goal_distance <= 15:
        stuck.ue_jug()

        # ------------- Calibration -------------#
        print('Calibration Start')

        magdata_Old = Calibration.magdata_matrix(20, -20, 0.2, 30)
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
        t_cal = time.time()

        while time.time() - t_cal <= t_tyousei:
            _, lat1, lon1, _, _ = GPS.GPSdata_read()
            direction = GPS_Navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
            azimuth = direction["azimuth1"]
            goal_distance = direction["distance"]
            if goal_distance <= 15:
                break
            else:
                for _ in range(10):
                    magdata = BMC050.mag_dataRead()
                    mag_x = magdata[0]
                    mag_y = magdata[1]
                    theta = Calibration.angle(mag_x, mag_y, magx_off, magy_off)
                    theta = azimuth - theta
                    if theta < 0:
                        theta = 360 + theta
                    elif 360 <= theta <= 450:
                        theta = theta - 360
                    if 0 <= theta <= 15 or 345 <= theta <= 360:
                        print(f'0--- {theta}')
                        pass
                    elif 15 < theta < 180:
                        print(f'-1--- {theta}')
                        run = 6.5
                    elif 180 < theta < 345:
                        run = -2.5
                        print(f'1---{theta}')
                    motor.motor_continue(30 + run, 30 - run)
                    time.sleep(0.1)
            for i in range(10):
                coefficient_power = 10 - i
                coefficient_power /= 10
                motor.motor_move(30 * coefficient_power, 30 * coefficient_power, 0.1)
                if i == 9:
                    motor.motor_stop(2)


def drive(th_distance, t_adj_gps, logpath):
    global t_start
    direction = Calibration.calculate_direction(lon2, lat2)
    goal_distance = direction["distance"]
    while goal_distance <= th_distance:
        stuck.ue_jug()
        # ------------- Calibration -------------#
        Xbee.str_trans('Calibration Start')

        magdata_Old = Calibration.magdata_matrix(20, -20, 0.2, 30)
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
        t_cal = time.time()

        while time.time() - t_cal <= t_adj_gps:
            _, lat1, lon1, _, _ = GPS.GPSdata_read()
            direction = GPS_Navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
            azimuth = direction["azimuth1"]
            goal_distance = direction["distance"]
            # Xbee.str_trans(f'lat: {lat1}\tlon: {lon1}\tdistance: {direction["distance"]}\ttheta: {theta}')
            print(f'lat: {lat1}\tlon: {lon1}\tdistance: {direction["distance"]}\ttheta: {theta}')
            Other.saveLog(logpath, datetime.datetime.now(), time.time() - t_start, lat1, lon2, direction['distance'], azimuth)

            if goal_distance <= th_distance:
                break
            else:
                for _ in range(10):
                    magdata = BMC050.mag_dataRead()
                    mag_x = magdata[0]
                    mag_y = magdata[1]
                    theta = Calibration.angle(mag_x, mag_y, magx_off, magy_off)
                    theta = azimuth - theta
                    if theta < 0:
                        theta = 360 + theta
                    elif 360 <= theta <= 450:
                        theta = theta - 360
                    if 0 <= theta <= 15 or 345 <= theta <= 360:
                        Xbee.str_trans(f'0--- {theta}')
                        pass
                    elif 15 < theta < 180:
                        Xbee.str_trans(f'-1--- {theta}')
                        run = 6.5
                    elif 180 < theta < 345:
                        run = -2.5
                        Xbee.str_trans(f'1---{theta}')
                    motor.motor_continue(30 + run, 30 - run)
                    time.sleep(0.1)
            for i in range(10):
                coefficient_power = 10 - i
                coefficient_power /= 10
                motor.motor_move(30 * coefficient_power, 30 * coefficient_power, 0.1)
                if i == 9:
                    motor.motor_stop(2)

if __name__ == '__main__':
    GPS.openGPS()
    acc.bmc050_setup()
    motor.setup()
    mag.bmc050_setup()
    gps_run()
