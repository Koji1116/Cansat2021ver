import sys
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Environmental')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Illuminance')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/GPS')

import time
import serial
import pigpio
import BME280
import traceback
import math
import GPS
import BMC050



Plandcount = 0
GPSlandcount = 0
ACClandcount = 0
gpsdata = [0.0, 0.0, 0.0, 0.0, 0.0]
pressdata = [0.0, 0.0, 0.0, 0.0]
accdata = [0.0, 0.0, 0.0]


def Pressdetect(anypress):
    global Pcount
    global pressdata
    presslandjudge = 0
    try:

        pressdata = BME280.bme280_read()
        Prevpress = pressdata[1]
        time.sleep(1)
        pressdata = BME280.bme280_read()
        Latestpress = pressdata[1]
        deltP = abs(Latestpress - Prevpress)
        if 0.0 in pressdata:
            print("BME280error!")
            presslandjudge = 2
            Pcount = 0
        elif deltP < anypress:
            Pcount += 1
            if Pcount > 4:
                presslandjudge = 1
                print("presslandjudge")
        else:
            Pcount = 0
    except:
        print(traceback.format_exc())
        Pcount = 0
        presslandjudge = 2
    return Plandcount, presslandjudge

def gpsdetect(anyalt):
    global gpsdata
    global GPScount
    gpslandjudge = 0
    try:
        gpsdata = GPS.readGPS()
        Pregpsalt = gpsdata[3]
        time.sleep(1)
        gpsdata = GPS.readGPS()
        Latestgpsalt = gpsdata[3]
        daltGA = abs(Latestgpsalt - Pregpsalt)
        if daltGA < anyalt:
            GPScount += 1
            if GPScount > 4:
                gpslandjudge = 1
                print("gpslandjudge")
            else:
                gpslandjudge = 0
    except:
        print(traceback.format_exc())
        GPSlandcount = 0
        gpslandjudge = 2
    return GPSlandcount, gpslandjudge



def accdetect(anyacc):
    global accdata
    global ACCcount
    acclandjudge = 0
    try:
        accdata = BMC050.acc_dataRead()
        Preacc = math.sqrt(accdata[0]**2 + accdata[1]**2 + accdata[2]**2)
        time.sleep(1)
        accdata = BMC050.acc_dataRead()
        Latestaccdata = math.sqrt(accdata[0]**2 + accdata[1]**2 + accdata[2]**2)
        daltacc = abs(Latestaccdata - Preacc)
        if daltacc < anyacc:
            ACCcount += 1
            if ACCcount > 4:
                acclandjudge = 1
                print("acclandjudge")
            else:
                acclandjudge = 0
    except:
        print(traceback.format_exc())
        ACCcount = 0
        acclandjudge = 2
    return ACClandcount, acclandjudge



if __name__=="__main__":
    print("Start")

    GPS.openGPS()
    BME280.bme280_setup()
    BME280.bme280_calib_param()
    BMC050.bmc050_setup()

    while True:
        presslandjudge = 0
        gpslandjudge = 0
        acclandjudge = 0

        _, presslandjudge = Pressdetect(0.1)
        if presslandjudge == 1:
            print('Press')

        _, gpslandjudge = gpsdetect(0.5)
        if gpslandjudge == 1:
            print('GPS')

        _, acclandjudge = accdetect(0.5)
        if acclandjudge == 1:
            print('ACC')


