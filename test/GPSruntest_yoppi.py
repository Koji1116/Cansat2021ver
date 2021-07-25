import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
from gpiozero import Motor
import numpy as np
import mag
import BMC050
import GPS_Navigate
import GPS
import motor_koji
import motor
#import stuck
import Calibration
import pigpio
import time
import traceback
from threading import Thread


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
    
    """
    print('theta = '+str(theta)+'---rotate strat')
    count = 0
    while abs(theta) > 30:
        print(str(count))
        if count > 8:
            print('not ')
            #stuck.stuck_avoid()

        if abs(theta) <= 180:
            if abs(theta) <= 60:
                print('theta = '+str(theta)+'---ver1')
                motor.motor_move(
                    np.sign(theta)*0.5, -1*np.sign(theta)*0.5, 0.1)
                motor.stop()

            elif abs(theta) <= 180:
                print('theta = '+str(theta)+'---ver2')
                motor.motor_move(-np.sign(theta)
                                 * 0.5, np.sign(theta)*0.5, 0.1)
                motor.motor_stop()
        elif abs(theta) > 180:
            if abs(theta) >= 300:
                print('theta = '+str(theta)+'---ver3')
                motor.motor_move(-np.sign(theta)
                                 * 0.5, np.sign(theta)*0.5, 0.1)
                motor.motor_stop()
            elif abs(theta) > 180:
                print('theta = '+str(theta)+'---ver4')
                motor.motor_move(
                    np.sign(theta)*0.5, -np.sign(theta)*0.5, 0.1)
                motor.motor_stop()
        count += 1
        data = Calibration.get_data()
        magx = data[0]
        magy = data[1]
        # --- 0 <=theta<= 360 ---#
        theta = Calibration.calculate_angle_2D(
            magx, magy, magx_off, magy_off)
        direction = Calibration.calculate_direction(lon2, lat2)
        azimuth = direction["azimuth1"]
        theta = theta-azimuth

    print('theta = '+str(theta)+'---rotate fin!!!')


if __name__ == "__main__":
    mag.bmc050_setup()
    GPS.openGPS()
    print('Run Phase Start!')
    print('GPSstart')
    # --- difine goal latitude and longitude ---#
    lon2 = 139.9082386
    lat2 = 35.9184307

    # ------------- program start -------------#
    direction = Calibration.calculate_direction(lon2, lat2)
    goal_distance = direction['distance']
    print('goal distance = ' + str(goal_distance))
    # ------------- Calibration -------------#
    print('Calibration Start')
    # --- calculate offset ---#
    mag.bmc050_setup()
    ##-----------test--------
    r = float(input('migi?'))
    l = float(input('left?'))
    t = float(input('rotate time?'))
    # --- calibration ---#
    magdata_Old = Calibration.magdata_matrix(l, r, t)
    magx_array_Old, magy_array_Old, magz_array_Old, magx_off, magy_off, magz_off = Calibration.calculate_offset(magdata_Old)
    time.sleep(0.1)
    print('GPS run strat')
    # ------------- GPS navigate -------------#
    while 1:

        #----
        magdata = BMC050.mag_dataRead()
        mag_x = magdata[0]
        mag_y = magdata[1]
        theta = Calibration.angle(mag_x, mag_y, magx_off, magy_off)
        print(mag_x,mag_y)
        print(theta)
        time.sleep(0.5)
        adjust_direction(theta)

        print('theta = '+str(theta)+'--strat straight')
        motor_koji.motor_koji(0.8,0.8,6)

        # --- calculate  goal direction ---#
        direction = Calibration.calculate_direction(lon2, lat2)
        goal_distance = direction["distance"]
        print(str(goal_distance))
