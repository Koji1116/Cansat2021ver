
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
strength_l_cal = 40
strength_r_cal = -40
t_rotation_cal = 0.2
number_data = 30

# variable for panorama
strength_l_pano = 40
strength_r_pano = -40
t_rotation_pano = 0.15

# variable for GPSrun
lat2 = 35.9235914
lon2 = 139.9118100
th_distance = 5
t_adj_gps = 30

# variable for photorun
G_thd = 80
path_photo_imagerun = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}-{dateTime.minute}'

# log
log_phase = '/home/pi/Desktop/Cansat2021ver/test/log/gps1.txt'

# photo path
path_src_panorama = '/home/pi/Desktop/Cansat2021ver/src_panorama/panoramaShooting00'
path_dst_panoraam = '/home/pi/Desktop/Cansat2021ver/dst_panorama'
path_paradete = '/home/pi/Desktop/Cansat2021ver/photostorage/paradete'



def close():
    GPS.closeGPS()
    Xbee.off()


if __name__ == '__main__':
    # close()
    
    GPS.openGPS()
    motor.setup()
    #######-----------------------Setup--------------------------------#######
    try:
        print(GPS.GPS_dataread())
        t_start = time.time()
        print('#####-----Setup Phase start-----#####')
        Other.saveLog(log_phase, GPS.GPS_dataread())
        
    except Exception as e:
        tb = sys.exc_info()[2]
        print("message:{0}".format(e.with_traceback(tb)))
        print('#####-----Error(setup)-----#####')
        print('#####-----Error(setup)-----#####\n \n')
    #######-----------------------------------------------------------########

    