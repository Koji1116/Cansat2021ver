
import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')
# sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Illuminance')
# sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
# import BMC050
# import GPS
import traceback
import BME280
import pigpio
import serial
import time




Plandcount = 0
# GPSlandcount = 0
# ACClandcount = 0
pressdata = [0.0, 0.0, 0.0, 0.0]
# gpsdata = [0.0, 0.0, 0.0, 0.0, 0.0]
# accdata = [0.0, 0.0, 0.0]


def pressdetect_land(thd_press_land):
    """
    気圧情報による着地判定用
    引数はどのくらい気圧が変化したら判定にするかの閾値
    """
    global press_count_land
    global press_judge_land
    try:
        pressdata = BME280.bme280_read()
        Prevpress = pressdata[1]
        time.sleep(1)
        pressdata = BME280.bme280_read()
        Latestpress = pressdata[1]
        deltP = abs(Latestpress - Prevpress)
        if 0.0 in pressdata:
            print("BME280error!")
            press_count_land = 0
            press_judge_land = 2
        elif deltP < thd_press_land:
            press_count_land += 1
            if press_count_land > 4:
                press_judge_land = 1
                print("presslandjudge")
        else:
            press_count_land = 0
            press_judge_land = 0
    except:
        press_count_land = 0
        press_judge_land = 2
    return press_count_land, press_judge_land


if __name__ == "__main__":
    print("Start")

    BME280.bme280_setup()
    BME280.bme280_calib_param()

    while True:
        presslandjudge = 0

        Plandcount, presslandjudge = pressdetect_land(0.1)                                            #調整するところ
        print(f'count:{Plandcount}\tjudge:{presslandjudge}')
        if presslandjudge == 1:
            print('Press')
        else:
            print('Press unfulfilled')




#
# def gpsdetect(anyalt):
#     """
#     GPSの高度情報による着地判定用
#     引数はどのくらいGPS高度が変化したら判定にするかの閾値
#     """
#     global gpsdata
#     global GPScount
#     gpslandjudge = 0
#     try:
#         gpsdata = GPS.readGPS()
#         Pregpsalt = gpsdata[3]
#         time.sleep(1)
#         gpsdata = GPS.readGPS()
#         Latestgpsalt = gpsdata[3]
#         daltGA = abs(Latestgpsalt - Pregpsalt)
#         if daltGA < anyalt:
#             GPScount += 1
#             if GPScount > 4:
#                 gpslandjudge = 1
#                 print("gpslandjudge")
#             else:
#                 gpslandjudge = 0
#     except:
#         print(traceback.format_exc())
#         GPSlandcount = 0
#         gpslandjudge = 2
#     return GPSlandcount, gpslandjudge
#
#
# def accdetect(anyacc):
#     """
#     着地判定用の加速度
#     time.sleepがあるからaccdetect2と比べ時間がかかる
#     """
#     global accdata
#     global ACCcount
#     acclandjudge = 0
#     try:
#         accdata = BMC050.acc_dataRead()
#         Preacc = math.sqrt(accdata[0]**2 + accdata[1]**2 + accdata[2]**2)
#         time.sleep(1)
#         accdata = BMC050.acc_dataRead()
#         Latestaccdata = math.sqrt(accdata[0]**2 + accdata[1]**2 + accdata[2]**2)
#         daltacc = abs(Latestaccdata - Preacc)
#         if daltacc < anyacc:
#             ACCcount += 1
#             if ACCcount > 4:
#                 acclandjudge = 1
#                 print("acclandjudge")
#             else:
#                 acclandjudge = 0
#     except:
#         print(traceback.format_exc())
#         ACCcount = 0
#         acclandjudge = 2
#     return ACClandcount, acclandjudge
#
#
#
# def accdetect2(lowerAcc, upperAcc):
#     """
#     着地判定用の加速度
#     time.sleepがないからaccdetectと比べ時間がかからない
#     """
#     global accdata
#     global ACCcount
#     acclandjudge = 0
#     try:
#         accdata = BMC050.acc_dataRead()
#         acc = math.sqrt(accdata[0]**2 + accdata[1]**2 + accdata[2]**2)
#         if lowerAcc < acc < upperAcc:
#             ACCcount += 1
#             if ACCcount > 4:
#                 acclandjudge = 1
#                 print("acclandjudge")
#             else:
#                 acclandjudge = 0
#     except:
#         print(traceback.format_exc())
#         ACCcount = 0
#         acclandjudge = 2
#     return ACClandcount, acclandjudge




# if __name__ == "__main__":
#     print("Start")
#
#     GPS.openGPS()
#     BME280.bme280_setup()
#     BME280.bme280_calib_param()
#     BMC050.bmc050_setup()
#
#     while True:
#         presslandjudge = 0
#         gpslandjudge = 0
#         acclandjudge = 0
#
#         _, presslandjudge = Pressdetect(0.1)
#         if presslandjudge == 1:
#             print('Press')
#         else:
#             print('Press unfulfilled')
#
#         _, gpslandjudge = gpsdetect(0.5)
#         if gpslandjudge == 1:
#             print('GPS')
#         else:
#             print('GPS unfulfilled')
#
#         # _, acclandjudge = accdetect(0.5)
#         # if acclandjudge == 1:
#         #     print('ACC')
#         # else:
#         #     print('ACC unfulfilled')
#
#         _, acclandjudge = accdetect2(9, 11)
#         if acclandjudge == 1:
#             print('ACC')
#         else:
#             print('ACC unfulfilled')
#
#         landjudge = [presslandjudge, gpslandjudge, acclandjudge]
#
#         if landjudge.count(1) >= 2:
#             print('Landed')
#         else:
#             print('Land not yet')
        
