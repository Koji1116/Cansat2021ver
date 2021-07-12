import sys
sys.path.append('/home/pi/git/kimuralab/SensorModule/Camera')
sys.path.append('/home/pi/git/kimuralab/SensorModule/Motor')
sys.path.append('/home/pi/git/kimuralab/Detection/ParachuteDetection')
sys.path.append('/home/pi/git/kimuralab/Other')

import time
import cv2
import numpy as np
import Capture
import ParaDetection
import Motor
import Other
import GPS
import BMC050

timeout_paradetect = 20
LuxThd_paradetect = 2000
timeout_paraStuckEscape = 20

mp_min = 10							#motor power for Low level
mp_max = 40							#motor power fot High level

photopath = 		"/home/pi/photo/photo"

H_min = 220			#Hue minimam
H_max = 20			#Hue maximam


if __name__ == '__main__':
    print('Start: Judge covered by Prachute')

    #Set up
    GPS.openGPS() #このプログラム単体で使わない場合はいらない
    BMC050.bmc050_setup()

    #Time
    t_para_start = time.time()

    #GPS
    gpsdata_landing = GPS.readGPS()
    Lat_landing = gpsdata_landing[1]
    Lon_landing = gpsdata_landing[2]
    preLat_landing = Lat_landing
    preLon_landing = Lon_landing

    #Parachute avoidance area condition
    distance_landing, _ = GPS.vincentyInverse(Lat_landing,Lon_landing,preLat_landing,preLon_landing)


    while distance_landing < 10:
        t_paraDetect_start = time.time()
        while time.time() - t_paraDetect_start < timeout_paradetect:    #パラシュートが風で飛ぶのを待つ時間
            paraLuxflug, paraLux = ParaDetection.ParaJudge()
            if paraLuxflug == 1:
                break
            time.sleep(1)
        Motor.motor(-20, -20, 0.9)
        Motor.motor(0, 0, 0, 9)
        Motor.motor(60, 60, 0.25, 1)
        Motor.motor(0, 0, 2.0)
        Motor.motor(15, 15, 0.9)
        Motor.motor(0, 0, 0.9)

        # --- Stuck Detection --- #
        # 片輪が浮いてる状態など
        print("START: Stuck Detection")
        for i in range(20):
            BMC050data = BMC050.bmc050_read()
            # Other.saveLog(paraAvoidanceLog, time.time() - t_start, GPS.readGPS(), BMC050data)
            if abs(BMC050data[2]) < 5:
                paracount = paracount + 1
                if paracount > 4:
                    break
            else:
                paracount = 0

        # --- Stuck Escape --- #
        t_paraStuckEscape_start = time.time()
        while paracount > 4:
            if time.time() - t_paraStuckEscape_start > timeout_paraStuckEscape:
                break

            #スタックから抜け出す行動(検討)
            Motor.motor(70, 70, 0.2, 1)
            Motor.motor(0, 0, 2.0)
            Motor.motor(-70, -70, 0.2, 1)
            Motor.motor(0, 0, 2.0)
            Motor.motor(-60, 60, 0.4)
            Motor.motor(0, 0, 2.0)
            Motor.motor(60, -60, 0.4)
            Motor.motor(0, 0, 2.0)
            Motor.motor(15, 15, 0.9)
            Motor.motor(0, 0, 2)

            #スタック再確認
            for i in range(20):
                BMC050data = BMC050.bmc050_read()
                # Other.saveLog(paraAvoidanceLog, time.time() - t_start, GPS.readGPS(), BMC050data)
                if abs(BMC050data[2]) < 5:
                    paracount = paracount + 1
                    if paracount > 4:
                        break
                else:
                    paracount = 0

        # --- Parachute Avoidance --- #
        print("START: Parachute Avoidance")
        for i in range(2):  # Avoid Parachute two times
            Motor.motor(0, 0, 2)
            Motor.motor(15, 15, 0.9)
            Motor.motor(0, 0, 0.9)
            paraExsist, paraArea, photoName = ParaDetection.ParaDetection(photopath, H_min, H_max, S_thd)
            print(paraExsist, paraArea, photoName)
            # --- infront of me --- #
            if paraExsist == 1:
                Motor.motor(-mp_max, -mp_max, 5)
                Motor.motor(0, 0, 1)
                Motor.motor(mp_max, mp_max, 0.5)
                Motor.motor(0, 0, 1)
                Motor.motor(mp_max, mp_min, 1.0)
                Motor.motor(0, 0, 1)

            # --- infront nothing --- #
            if paraExsist == 0:
                Motor.motor(mp_max, mp_max, 5)
                Motor.motor(0, 0, 1)
                Motor.motor(-mp_max, -mp_max, 0.5)
                Motor.motor(0, 0, 1)

            # --- broken camera --- #
            if paraExsist == -1:
                print('Camera is broken')
                Motor.motor(mp_max, mp_max, 5)
                Motor.motor(0, 0, 1)
                Motor.motor(-mp_max, -mp_max, 0.5)
                Motor.motor(0, 0, 1)

        # GPS
        gpsdata_landing = GPS.readGPS()
        Lat_landing = gpsdata_landing[1]
        Lon_landing = gpsdata_landing[2]

        # Parachute avoidance area condition
        distance_landing, _ = GPS.vincentyInverse(Lat_landing, Lon_landing, preLat_landing, preLon_landing)
