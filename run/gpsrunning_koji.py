import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Casnat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')


import datetime
import time

import GPS_Navigate
import BMC050
import GPS
import motor
import Calibration
import mag
import stuck
import acc
import Xbee
import Other

lat2 = 35.9235927
lon2 = 139.9119897

def angle_goal(magx_off, magy_off):
    """
    ゴールとの相対角度を算出する関数
    -180~180度
    """
    magdata = BMC050.mag_dataRead()
    mag_x = magdata[0]
    mag_y = magdata[1]
    theta = Calibration.angle(mag_x, mag_y, magx_off, magy_off)
    direction = Calibration.calculate_direction(lon2, lat2)
    azimuth = direction["azimuth1"]
    angle_relative = azimuth - theta
    if angle_relative >= 0:
        angle_relative = angle_relative if angle_relative <= 180 else angle_relative - 360
    else:
        angle_relative = angle_relative if angle_relative >= -180 else angle_relative + 360
    return angle_relative


def adjust_direction(theta, magx_off, magy_off):
    """
    方向調整
    """
    print('ゴールとの角度theta = ' + str(theta) + '---回転調整開始！')

    stuck_count = 1
    t_small = 0.1
    t_big = 0.2
    force = 35
    while 30 < theta <= 180 or -180 < theta < -30:
        if stuck_count % 7 == 0:
            print('Increase output')
            force += 10
        if 15 <= theta <= 60:
            print(f'theta = {theta}\t---rotation_ver1 (stuck:{stuck_count})')
            motor.move(force, -force, t_small)

        elif 60 < theta <= 180:
            print(f'theta = {theta}\t---rotation_ver2 (stuck:{stuck_count})')
            motor.move(force, -force, t_big)

        elif -60 <= theta <= -15:
            print(f'theta = {theta}\t---rotation_ver3 (stuck:{stuck_count})')
            motor.move(-force, force, t_small)
        elif -180 < theta < -60:
            print(f'theta = {theta}\t---rotation_ver4 (stuck:{stuck_count})')
            motor.move(-force, force, t_big)
        else:
            print(f'theta = {theta}')

        stuck_count += 1
        theta = angle_goal(magx_off, magy_off)
        print('Calculated angle_relative: {theta}')
        time.sleep(1)
    print(f'theta = {theta} \t rotation finished!!!')

def drive(lon2, lat2, thd_distance, t_adj_gps, logpath, t_start=0):
    """
    GPS走行の関数
    統合する場合はprintをXbee.str_transに変更，Other.saveLogのコメントアウトを外す
    """
    direction = Calibration.calculate_direction(lon2, lat2)
    goal_distance = direction['distance']

    while goal_distance >= thd_distance:
        stuck.ue_jug()
        # ------------- Calibration -------------#
        # Xbee.str_trans('Calibration Start')
        print('##--Calibration Start--##')
        magx_off, magy_off = Calibration.cal(40, -40, 0.2, 30)
        theta = angle_goal(magx_off, magy_off)
        adjust_direction(theta, magx_off, magy_off)

        t_cal = time.time()
        while time.time() - t_cal <= t_adj_gps:
            lat1, lon1 = GPS.location()
            direction = GPS_Navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
            azimuth, goal_distance = direction["azimuth1"], direction["distance"]
            print(f'lat: {lat1}\tlon: {lon1}\tdistance: {goal_distance}\tazimuth: {azimuth}')
            # Xbee.str_trans(f'lat: {lat1}\tlon: {lon1}\tdistance: {direction["distance"]}\ttheta: {theta}')
            # Other.saveLog(logpath, datetime.datetime.now(), time.time() - t_start, lat1, lon1, direction['distance'],
            #               azimuth)

            if goal_distance <= thd_distance:
                break
            else:
                for _ in range(10):
                    theta = angle_goal(magx_off, magy_off)
                    if theta >= 0:
                        adj = 0 if theta <= 15 else 18
                    else:
                        adj = 0 if theta >= -15 else -10
                    print(f'angle ----- {theta}')
                    strength_l, strength_r = 70 + adj, 70 - adj
                    motor.motor_continue(strength_l, strength_r)
                    time.sleep(0.1)
        motor.deceleration(strength_l, strength_r)
        time.sleep(2)


if __name__ == '__main__':
    GPS.openGPS()
    acc.bmc050_setup()
    mag.bmc050_setup()
    motor.setup()

    drive(lon2, lat2, thd_distance=10, t_adj_gps=30, logpath='')
