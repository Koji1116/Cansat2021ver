import sys

sys.path.append('/home/pi/Desktop/Cansat2021ver/fall')
sys.path.append('/home/pi/Desktop/Cansat2021ver/detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/fall')

import time

import land
import BME280
import GPS
import Xbee
import motor
import Calibration
import paradetection
import paraavoidance
import Other
import datetime
import mag
import melt
import escape
import panorama
import BMC050

#variable for timeout
t_out_land = 40

#variavle for landing
thd_press_land = 0.15

#variable for GPSrun
lon2 = 35.
lat2 = 139.


#log
log_phase = '/home/pi/Desktop/Cansat2021ver/log/phaseLog1.txt'
log_landing = '/home/pi/Desktop/Cansat2021ver/log/landingLog1.txt'
log_melting = '/home/pi/Desktop/Cansat2021ver/log/meltingLog1.txt'
log_paraavoidance = 'home/pi/Desktop/Cansat2021ver/paraAvoidanceLog1.txt'
path_src_panorama = '/home/pi/Desktop/Cansat2021ver/panorama_src'
path_dst_panoraam = '/home/pi/Desktop/Cansat2021ver/panorama_dst'
path_paradete = '/home/pi/Desktop/Cansat2021ver/photostorage'


def setup():
    global phaseChk
    BME280.bme280_setup()
    BME280.bme280_calib_param()
    BMC050.BMC050_setup()
    GPS.openGPS()
    Xbee.on()
    motor.setup()


if __name__ == '__main__':
    #######-----------------------Setup--------------------------------#######
    try:
        t_start = time.time()
        Xbee.str_trans('#####-----Setup Phase start-----#####')
        Other.saveLog(log_phase, "1", "Setup phase", time.time() - t_start, datetime.datetime.now())
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        setup()
        Xbee.str_trans('#####-----Setup Phase ended-----##### \n \n')
    except:
        Xbee.str_trans('#####-----Error(setup)-----#####')
        Xbee.str_trans('#####-----Error(setup)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------Landing--------------------------#######
    try:
        Xbee.str_trans('#####-----Landing phase start-----#####')
        Other.saveLog(log_phase, '2', 'Landing phase', time.time() - t_start, datetime.datetime.now())
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 2:
            Xbee.str_trans(f'Landing Judgement Program Start\t{time.time() - t_start}')
            t_land_start = time.time()
            i = 1
            while time.time() - t_land_start <= t_out_land:
                Xbee.str_trans(f"loop_land\t{i}")
                press_count_release, press_judge_release = land.pressdetect_land(thd_press_land)
                Xbee.str_trans(f'count:{press_count_release}\tjudge{press_judge_release}')
                if press_judge_release == 1:
                    Xbee.str_trans('Landed')
                    break
                else:
                    Xbee.str_trans('Not Landed')
                Other.saveLog(log_landing, datetime.datetime.now(), time.time() - t_start, GPS.readGPS(),
                              BME280.bme280_read())
                i += 1
            else:
                Xbee.str_trans('Landed Timeout')
            Other.saveLog(log_landing, datetime.datetime.now(), time.time() - t_start, GPS.readGPS(),
                          BME280.bme280_read(), 'Land judge finished')
            Xbee.str_trans('######-----Landed-----######\n \n')
    except:
        Xbee.str_trans('#####-----Error(Landing)-----#####')
        Xbee.str_trans('#####-----Error(Landing)-----#####')
        Xbee.str_trans('#####-----Error(Landing)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------Escape--------------------------#######
    try:
        Xbee.str_trans('#####-----Melting phase start#####')
        Other.saveLog(log_phase, '3', 'Melting phase start', time.time() - t_start, datetime.datetime.now())
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 3:
            Other.saveLog(log_melting, datetime.datetime.now(), time.time() - t_start, GPS.readGPS(), "Melting Start")
            escape.escape()
            time.sleep(3)
            Other.saveLog(log_melting, datetime.datetime.now(), time.time() - t_start, GPS.readGPS(), "Melting Finished")
        Xbee.str_trans('########-----Melted-----#######\n \n')
    except:
        Xbee.str_trans('#####-----Error(melting)-----#####')
        Xbee.str_trans('#####-----Error(melting)-----#####')
        Xbee.str_trans('#####-----Error(melting)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------Paraavo--------------------------#######
    try:
        Xbee.str_trans('#####-----Para avoid start-----#####')
        Other.saveLog(log_phase, '4', 'Melting phase start', time.time() - t_start, datetime.datetime.now())
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        count_paraavo = 0
        if phaseChk == 4:
            while count_paraavo < 3:
                flug, area, gap, photoname = paradetection.ParaDetection(
                    path_paradete, 320, 240, 200, 10, 120, 1)
                Xbee.str_trans(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
                Other.saveLog(log_paraavoidance, datetime.datetime.now(), time.time() - t_start, GPS.readGPS, flug, area,
                              gap, photoname)
                paraavoidance.Parachute_Avoidance(flug, gap)
                if flug == -1 or flug == 0:
                    count_paraavo += 1
        Xbee.str_trans('#####-----ParaAvo Phase ended-----##### \n \n')
    except:
        Xbee.str_trans('#####-----Error(paraavo)-----#####')
        Xbee.str_trans('#####-----Error(paraavo)-----#####')
        Xbee.str_trans('#####-----Error(paraavo)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------panorama--------------------------#######
    try:
        Xbee.str_trans('#####-----panorama start-----#####')
        Other.saveLog(log_phase, '4', 'Melting phase start', time.time() - t_start, datetime.datetime.now())
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 4:
            t_start_panorama = time.time()  # プログラムの開始時刻
            panorama(path_src_panorama, path_dst_panoraam, 'panoramaShootingtest00')
            Xbee.str_trans(f'runTime:\t{time.time()-t_start_panorama}')
        Xbee.str_trans('#####-----panorama ended-----##### \n \n')
    except:
        Xbee.str_trans('#####-----Error(panorama)-----#####')
        Xbee.str_trans('#####-----Error(panorama)-----#####')
        Xbee.str_trans('#####-----Error(panorama)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------GPS--------------------------#######
    try:
        Xbee.str_trans('#####-----panorama start-----#####')
        Other.saveLog(log_phase, '5', 'Melting phase start', time.time() - t_start, datetime.datetime.now())
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 5:
            direction = Calibration.calculate_direction(lon2, lat2)
            goal_distance = direction['distance']
            aaa = direction['azimuth1']
            Xbee.str_trans('goal distance = ' + str(goal_distance))
            Xbee.str_trans('goal direction = ' + str(aaa))
            count = 0
            while goal_distance >= 10:
                if count % 4 == 0:
                    # ------------- Calibration -------------#
                    Xbee.str_trans('Calibration Start')
                    mag.bmc050_setup()
                    magdata_Old = Calibration.magdata_matrix(20, -20, 0.2, 30)
                    _, _, _, magx_off, magy_off, _ = Calibration.calculate_offset(magdata_Old)
                Xbee.str_trans('GPS run strat')
                # ------------- GPS navigate -------------#
                magdata = BMC050.mag_dataRead()
                mag_x = magdata[0]
                mag_y = magdata[1]
                theta = Calibration.angle(mag_x, mag_y, magx_off, magy_off)
                direction = Calibration.calculate_direction(lon2, lat2)
                azimuth = direction["azimuth1"]
                theta = azimuth - theta
                if theta < 0:
                    theta = 360 + theta
                elif 360 <= theta <= 450:
                    theta = theta - 360

                adjust_direction(theta)
                Xbee.str_trans('theta = ' + str(theta) + '---直進開始')
                ######直進するように左の出力強くしてます↓ 7/28 by oosima
                motor.move(65, 50, 6)

                # --- calculate  goal direction ---#
                direction = Calibration.calculate_direction(lon2, lat2)
                goal_distance = direction["distance"]
                Xbee.str_trans('------ゴールとの距離は' + str(goal_distance) + 'm------')
                count += 1
            Xbee.str_trans('!!!!!GPS走行終了。次は画像誘導!!!!!!!!!!!!')
    except:


    # -----------photo_run------------#
    G_thd = 80  # 調整するところ
    goalflug = 1
    startTime = time.time()
    dateTime = datetime.datetime.now()
    path_photo_imagerun = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}:{dateTime.minute}'
    photorunning.image_guided_driving(path_photo_imagerun, 50)
