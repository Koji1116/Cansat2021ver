import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')

import motor
import BME280
import BMC050
import GPS
import Xbee

def setup(lat_goal, lon_goal):
    global lat2, lon2
    global phaseChk
    lat2, lon2 = lat_goal, lon_goal
    motor.setup()
    BME280.bme280_setup()
    BME280.bme280_calib_param()
    BMC050.BMC050_setup()
    GPS.openGPS()
    Xbee.on()
