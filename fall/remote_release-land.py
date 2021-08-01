import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')


import BME280
import time
import Xbee

phaseLog = "/home/pi/Cansat2021ver/log/phaseLog.txt"
releaseLog = "/home/pi/Cansat2021ver/log/releaseLog.txt"
landingLog = "/home/pi/Cansat2021ver/log/landingLog.txt"

def pressdetect_release(thd_press_release):
    global presscount_release
    global pressjudge_release
    try:
        pressdata = BME280.bme280_read()
        prevpress = pressdata[1]
        time.sleep(5)
        pressdata = BME280.bme280_read()
        latestpress = pressdata[1]
        deltP = latestpress - prevpress
        if 0.0 in pressdata:
            print("BME280rror!")
            pressjudge_release = 2
            presscount_release = 0
        elif deltP > thd_press_release:
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
    global presscount_land
    global pressjudge_land
    try:
        pressdata = BME280.bme280_read()
        Prevpress = pressdata[1]
        time.sleep(1)
        pressdata = BME280.bme280_read()
        Latestpress = pressdata[1]
        deltP = abs(Latestpress - Prevpress)
        if 0.0 in pressdata:
            print("BME280error!")
            presscount_land = 0
            pressjudge_land = 2
        elif deltP < anypress:
            presscount_land += 1
            if presscount_land > 4:
                pressjudge_land = 1
                print("presslandjudge")
        else:
            presscount_land = 0
    except:
        presscount_land = 0
        pressjudge_land = 2
    return presscount_land, pressjudge_land



if __name__ == '__main__':
    BME280.bme280_setup()
    BME280.bme280_calib_param()
    t_start = time.time()
    Xbee.on()
    #放出判定用
    presscount_release = 0
    pressjudge_release = 0
    #着地判定用
    presscount_land = 0
    pressjudge_land = 0

    while 1:
        if Xbee.str_receive == 's':
            break

    try:
        while 1:
            presscount_release, pressjudge_release = pressdetect_release(0.3)
            print(f'count{presscount_release}\tjudge{pressjudge_release}')
            if Xbee.str_receive() == 'e':
                exit()
            if pressjudge_release == 1:
                print('release detected')
                break
    except KeyboardInterrupt:
        pass

    try:
        while 1:
            presscount_land, pressjudge_land = pressdetect_land(0.1)
            print(f'count{presscount_land}\tjudge{pressjudge_land}')
            if pressjudge_land == 1:
                print('land detected')
                break
    except KeyboardInterrupt:
        pass


    # try:
    #     while 1:
    #         presscount_release, pressjudge_release = pressdetect_release(0.3)
    #         print(f'count{presscount_release}\tjudge{pressjudge_release}')
    #         if pressjudge_release == 1:
    #             print('release detected')
    #             break
    #
    #     while 1:
    #         presscount_land, pressjudge_land = pressdetect_land(0.1)
    #         print(f'count{presscount_land}\tjudge{pressjudge_land}')
    #         if pressjudge_land == 1:
    #             print('land detected')
    #             break
    #
    #     print('finished')
    # except KeyboardInterrupt:
    #     print('interrupted')
    # except:
    #     print('finished')