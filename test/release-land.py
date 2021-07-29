import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')

import BME280
import time


def pressdetect_release(anypress):
    global presscount_release
    global pressjudge_release
    try:
        pressdata = BME280.bme280_read()
        prevpress = pressdata[1]
        time.sleep(1)
        pressdata = BME280.bme280_read()
        latestpress = pressdata[1]
        deltP = latestpress - prevpress
        if 0.0 in pressdata:
            print("BME280rror!")
            pressjudge_release = 2
            presscount_release = 0
        elif deltP > anypress:
            presscount_release += 1
            if presscount_release > 2:
                pressjudge_release = 1
                print("pressreleasejudge")
        else:
            presscount_release = 0
    except:
        presscount_release = 0
        pressjudge_release = 2
    return presscount_release, pressjudge_release


def pressdetect_land(anypress):
    """
    気圧情報による着地判定用
    引数はどのくらい気圧が変化したら判定にするかの閾値
    """
    global Plandcount
    global pressdata
    presslandjudge = 0
    plandcount = 0
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
            plandcount = 0
        elif deltP < anypress:
            plandcount += 1
            if Pcount > 4:
                presslandjudge = 1
                print("presslandjudge")
        else:
            plandcount = 0
    except:
        Pcount = 0
        presslandjudge = 2
    return plandcount, presslandjudge



if __name__ == '__main__':
    BME280.bme280_setup()
    BME280.bme280_calib_param()
    startTime = time.time()
    presscount_release = 0
    try:
        while 1:
            pressdetect_release(0.3)
