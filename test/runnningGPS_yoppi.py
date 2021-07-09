from threading import Thread
import traceback
import time
import pigpio
import Calibration
import Stuck
import motor
import stuck
import GPS
import BMC050
import Xbee
import gps_navigate
import numpy as np
import sys
# このパス後で調整必要　by oosim
sys.path.append('/home/pi/git/kimuralab/SensorModule/Communication')
sys.path.append('/home/pi/git/kimuralab/SensorModule/Camera')
sys.path.append('/home/pi/git/kimuralab/SensorModule/GPS')
sys.path.append('/home/pi/git/kimuralab/SensorModule/Motor')
sys.path.append('/home/pi/git/kimuralab//Calibration')
sys.path.append('/home/pi/git/kimuralab/IntegratedProgram/Stuck')

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


def adjust_direction():
    """
    方向調整
    """
    global theta
    Xbee.str_trans('theta = '+str(theta)+'---回転調整開始！')
    count = 0
    while abs(theta) > 30:
        Xbee.str_trans(str(count))
        if count > 8:
            Xbee.str_trans('スタックもしくはこの場所が適切ではない')
            stuck.stuck_avoid()

        if abs(theta) <= 180:
            if abs(theta) <= 60:
                Xbee.str_trans('theta = '+str(theta)+'---回転開始ver1')
                motor.motor_move(
                    np.sign(theta)*0.5, -1*np.sign(theta)*0.5, 3)
                motor.stop()

            elif abs(theta) <= 180:
                Xbee.str_trans('theta = '+str(theta)+'---回転開始ver2')
                motor.motor_move(-np.sign(theta)
                                 * 0.5, np.sign(theta)*0.5, 3)
                motor.motor_stop()
        elif abs(theta) > 180:
            if abs(theta) >= 300:
                Xbee.str_trans('theta = '+str(theta)+'---回転開始ver3')
                motor.motor_move(-np.sign(theta)
                                 * 0.5, np.sign(theta)*0.5, 5)
                motor.motor_stop()
            elif abs(theta) > 180:
                Xbee.str_trans('theta = '+str(theta)+'---回転開始ver4')
                motor.motor_move(
                    np.sign(theta)*0.5, -np.sign(theta)*0.5, 5)
                motor.motor_stop()
        count += 1
        data = Calibration.get_data()
        magx = data[0]
        magy = data[1]
        # --- 0 <= θ <= 360 ---#
        theta = Calibration.calculate_angle_2D(
            magx, magy, magx_off, magy_off)
        direction = Calibration.calculate_direction(lon2, lat2)
        azimuth = direction["azimuth1"]
        theta = theta-azimuth

    Xbee.str_trans('theta = '+str(theta)+'---回転終了!!!')


if __name__ == "__main__":
    BMC050.BMC050_setup()
    GPS.openGPS()
    print('Run Phase Start!')
    Xbee.str_trans('GPS走行開始')
    # --- difine goal latitude and longitude ---#
    lon2 = 139.90833592590076
    lat2 = 35.91817558805946

    # ------------- program start -------------#
    direction = Calibration.calculate_direction(lon2, lat2)
    goal_distance = direction['distance']
    print('goal distance = ' + str(goal_distance))
    # ------------- GPS navigate -------------#
    while goal_distance >= 15:  # この値調整必要
        # ------------- Calibration -------------#
        print('Calibration Start')
        # --- calculate offset ---#
        magdata = Calibration.magdata_matrix()
        magdata_offset = Calibration.calculate_offset(magdata)
        magx_off = magdata_offset[3]
        magy_off = magdata_offset[4]
        magz_off = magdata_offset[5]

        # --- calculate θ ---#
        data = Calibration.get_data()
        magx = data[0]
        magy = data[1]
        # --- 0 <= θ <= 360 ---#
        θ = Calibration.calculate_angle_2D(magx, magy, magx_off, magy_off)
        # ------------- rotate contorol -------------#

        adjust_direction()

        # パラメータ要確認
        Xbee.str_trans('theta = '+str(theta)+'---直進開始')
        motor.motor_move(0.8, 0.8, 0.2)
        if stuck.stuck_duj():
            stuck.stuck_avoid()
        motor.motor_move(0.8, 0.8, 10)
        motor.stop()

        # --- calculate  goal direction ---#
        direction = Calibration.calculate_direction(lon2, lat2)
        goal_distance = direction["distance"]
        if goal_distance >= 15:
            Xbee.str_trans('goal distance =' +
                           str(goal_distance)+'----GPS走行続く')
        else:
            Xbee.str_trans('goal distance =' +
                           str(goal_distance)+'----GPS走行終了！')
        print('goal distance =' + str(goal_distance))
