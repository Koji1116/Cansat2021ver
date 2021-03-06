import sys

sys.path.append('/home/pi/Desktop/Cansat2021ver/fall')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/fall')
sys.path.append('/home/pi/Desktop/Cansat2021ver/run')

import time
import datetime

import BME280
import Xbee
import GPS
import motor
import BMC050
import release
import land
import paradetection
import paraavoidance
import escape
import panorama
import gpsrunning_koji
import photorunning
import Other
import Calibration

dateTime = datetime.datetime.now()

# variable for timeout
t_out_release = 5
t_out_land = 5

# variable for release
thd_press_release = 0.3
t_delta_release = 1

# variable for landing
thd_press_land = 0.15

# variable for Calibration
strength_l_cal = 20
strength_r_cal = -20
t_rotation_cal = 0.2
number_data = 30

# variable for panorama
strength_l_pano = 20
strength_r_pano = -20
t_rotation_pano = 0.15

# variable for GPSrun
lat2 = 35.9235927
lon2 = 139.9119897
th_distance = 5
t_adj_gps = 30

# variable for photorun
G_thd = 80
path_photo_imagerun = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}-{dateTime.minute}'

# log
log_phase = '/home/pi/Desktop/Cansat2021ver/log/phaseLog1.txt'
log_release = '/home/pi/Desktop/Cansat2021ver/log/releaselog1.txt'
log_landing = '/home/pi/Desktop/Cansat2021ver/log/landingLog1.txt'
log_melting = '/home/pi/Desktop/Cansat2021ver/log/meltingLog1.txt'
log_paraavoidance = '/home/pi/Desktop/Cansat2021ver/log/paraAvoidanceLog1.txt'
log_gpsrunning = '/home/pi/Desktop/Cansat2021ver/log/gpsrunningLog1.txt'
log_photorunning = '/home/pi/Desktop/Cansat2021ver/log/photorunning1.txt'

# photo path
path_src_panorama = '/home/pi/Desktop/Cansat2021ver/src_panorama/panoramaShooting00'
path_dst_panoraam = '/home/pi/Desktop/Cansat2021ver/dst_panorama'
path_paradete = '/home/pi/Desktop/Cansat2021ver/photostorage/paradete'


def setup():
    global phaseChk
    BME280.bme280_setup()
    BME280.bme280_calib_param()
    BMC050.BMC050_setup()
    GPS.openGPS()
    Xbee.on()

def close():
    GPS.closeGPS()
    Xbee.off()


if __name__ == '__main__':
    # close()
    motor.setup()
    #######-----------------------Setup--------------------------------#######
    try:
        t_start = time.time()
        print('#####-----Setup Phase start-----#####')
        #Other.saveLog(log_phase, "1", "Setup phase", dateTime, time.time() - t_start)
        # phaseChk = Other.phaseCheck(log_phase)
        # print(f'Phase:\t{phaseChk}')
        setup()
        print('#####-----Setup Phase ended-----##### \n \n')
    except Exception as e:
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))
        print('#####-----Error(setup)-----#####')
        print('#####-----Error(setup)-----#####')
        print('#####-----Error(setup)-----#####\n \n')
    #######-----------------------------------------------------------########

    #######--------------------------GPS--------------------------#######
    try:
        print('#####-----gps run start-----#####')
        #Other.saveLog(log_phase, '7', 'Melting phase start', dateTime, time.time() - t_start)
        # phaseChk = Other.phaseCheck(log_phase)
        # print(f'Phase:\t{phaseChk}')
        if 1:
            gpsrunning_koji.drive(lon2, lat2, th_distance, t_adj_gps, log_gpsrunning)
    except Exception as e:
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))
        print('#####-----Error(gpsrunning)-----#####')
        print('#####-----Error(gpsrunning)-----#####')
        print('#####-----Error(gpsrunning)-----#####\n \n')

    ######------------------photo running---------------------##########
    try:
        print('#####-----photo run start-----#####')
        #Other.saveLog(log_phase, '8', 'Melting phase start', dateTime, time.time() - t_start)
        # phaseChk = Other.phaseCheck(log_phase)
        # print(f'Phase:\t{phaseChk}')
        if 1:
            photorunning.image_guided_driving(path_photo_imagerun, G_thd)
    except Exception as e:
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))
        print('#####-----Error(Photo running)-----#####')
        print('#####-----Error(Photo running)-----#####')
        print('#####-----Error(Photo running)-----#####\n \n')

