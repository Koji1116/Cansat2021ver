import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')

import BME280
import time

def pressdetect_land(anypress):
    """
    気圧情報による着地判定用
    引数はどのくらい気圧が変化したら判定にするかの閾値
    """
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

def pressdetect_release(anypress):

    pressreleasecount = 0
    pressreleasejudge = 0
    try:
        pressdata = BME280.bme280_read()
        prevpress = pressdata[1]
        time.sleep(1)
        pressdata = BME280.bme280_read()
        latestpress = pressdata[1]
        #print(presscount)
        deltP = latestpress - prevpress
        if 0.0 in pressdata:
            print("BME280rror!")
            pressreleasejudge = 2
            pressreleasecount = 0
        elif deltP > anypress:
            pressreleasecount += 1
            if pressreleasecount > 2:
                pressreleasejudge = 1
                print("pressreleasejudge")
        else:
            pressreleasecount = 0
        #print(str(latestpress) + "	:	" + str(prevpress))
    except:
        pressreleasecount = 0
        pressreleasejudge = 2
    return pressreleasecount, pressreleasejudge

if __name__ == '__main__':
    bme280_setup()
    bme280_calib_param()
    startTime = time.time()