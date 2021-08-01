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
        if Xbee.str_receive() == 's':
            Xbee.str_trans('program start')
            break
        else:
            Xbee.str_trans('standby')

    try:
        while time.time() - t_release_start <= t_out_release:
            i = 1
            Xbee.str_trans(f'loop_release\t {i}')
            press_count_release, press_judge_release = release.pressdetect_release(thd_press_release)
            Xbee.str_trans(f'count:{press_count_release}\tjudge{press_judge_release}')
            if press_judge_release == 1:
                Xbee.str_trans('Released')
                break
            else:
                Xbee.str_trans('Not Released')
            i += 1
        else:
            #落下試験用の安全対策（落下しないときにXbeeでプログラム終了)
            while time.time() - t_release_start <= t_out_release_safe:
                Xbee.str_trans('continue? y/n')
                if Xbee.str_receive() == 'y':
                    break
                elif Xbee.str_receive() == 'n':
                    exit()
            Xbee.str_trans('release timeout')
        Xbee.str_trans("######-----Released-----#####")
    except KeyboardInterrupt:
        pass

    try:
         while time.time() - t_land_start <= t_out_land:
                        i = 1
                        Xbee.str_trans(f"loop_land\t{i}")
                        press_count_release, press_judge_release = land.pressdetect_land()
                        Xbee.str_trans(f'count:{press_count_release}\tjudge{press_judge_release}')
                        if press_judge_release == 1:
                            Xbee.str_trans('Landed')
                            break
                        else:
                            Xbee.str_trans('Not Landed')
                        Other.saveLog(landingLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read(), BMC050.bmc050_read())
                        i += 1                    
                    else:
                        Xbee.str_trans('Landed Timeout')
                    Other.saveLog(landingLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read(), BMC050.bmc050_read(), 'Land judge finished')
                    Xbee.str_trans('######-----Landed-----######\n')
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