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
import mag
import panorama
import gpsrunning
import photorunning
import Other


dateTime = datetime.datetime.now()



#variable for timeout
t_out_release = 50
t_out_land = 40

#variable for release
thd_press_release = 0.3
t_delta_release = 0.1

#variable for landing
thd_press_land = 0.15

#variable for GPSrun
lon2 = 35.
lat2 = 139.
t_adj_gps = 5

#variable for photorun
G_thd = 80
path_photo_imagerun = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}-{dateTime.minute}'

#log
log_phase = '/home/pi/Desktop/Cansat2021ver/log/phaseLog1.txt'
log_release = '/home/pi/Desktop/Cansat2021ver/log/releaselog1.txt'
log_landing = '/home/pi/Desktop/Cansat2021ver/log/landingLog1.txt'
log_melting = '/home/pi/Desktop/Cansat2021ver/log/meltingLog1.txt'
log_paraavoidance = 'home/pi/Desktop/Cansat2021ver/paraAvoidanceLog1.txt'
log_gpsrunning = '/home/pi/Desktop/Cansat2021ver/gpsrunningLog1.txt'
log_photorunning = '/home/pi/Desktop/Cansat2021ver/log/photorunning1.txt'

#photo path
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
        Other.saveLog(log_phase, "1", "Setup phase", dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 2:
            setup()
        Xbee.str_trans('#####-----Setup Phase ended-----##### \n \n')
    except:
        Xbee.str_trans('#####-----Error(setup)-----#####')
        Xbee.str_trans('#####-----Error(setup)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------Release--------------------------#######
    Xbee.str_trans('#####-----Release Phase start-----#####')
    Other.saveLog(log_phase, "2", "Release Phase Started", dateTime, time.time() - t_start)
    phaseChk = Other.phaseCheck(log_phase)
    Xbee.str_trans(f'Phase:\t{phaseChk}')
    if phaseChk == 2:
        t_release_start = time.time()
        i = 1
        try:
            while time.time() - t_release_start <= t_out_release:
                Xbee.str_trans(f'loop_release\t {i}')
                press_count_release, press_judge_release = release.pressdetect_release(thd_press_release,
                                                                                       t_delta_release)
                Xbee.str_trans(f'count:{press_count_release}\tjudge{press_judge_release}')
                Other.saveLog(log_release, dateTime, time.time() - t_start, GPS.readGPS,
                              BME280.bme280_read(), press_count_release, press_judge_release)
                if press_judge_release == 1:
                    Xbee.str_trans('Release\n \n')
                    break
                else:
                    Xbee.str_trans('Not Release\n \n')
                i += 1
            else:
                Xbee.str_trans('##--release timeout--##')
            Xbee.str_trans("######-----Released-----##### \n \n")
        except:
            Xbee.str_trans('#####-----Error(Release)-----#####')
            Xbee.str_trans('#####-----Error(Release)-----#####')
            Xbee.str_trans('#####-----Error(Release)-----#####')

    #######--------------------------Landing--------------------------#######
    try:
        Xbee.str_trans('#####-----Landing phase start-----#####')
        Other.saveLog(log_phase, '3', 'Landing phase', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 3:
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
                Other.saveLog(log_landing, dateTime, time.time() - t_start, GPS.readGPS(),
                              BME280.bme280_read())
                i += 1
            else:
                Xbee.str_trans('Landed Timeout')
            Other.saveLog(log_landing, dateTime, time.time() - t_start, GPS.readGPS(),
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
        Other.saveLog(log_phase, '4', 'Melting phase start', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 4:
            Other.saveLog(log_melting, dateTime, time.time() - t_start, GPS.readGPS(), "Melting Start")
            escape.escape()
            Other.saveLog(log_melting, dateTime, time.time() - t_start, GPS.readGPS(), "Melting Finished")
        Xbee.str_trans('########-----Melted-----#######\n \n')
    except:
        Xbee.str_trans('#####-----Error(melting)-----#####')
        Xbee.str_trans('#####-----Error(melting)-----#####')
        Xbee.str_trans('#####-----Error(melting)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------Paraavo--------------------------#######
    try:
        Xbee.str_trans('#####-----Para avoid start-----#####')
        Other.saveLog(log_phase, '5', 'Melting phase start', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        count_paraavo = 0
        if phaseChk == 5:
            while count_paraavo < 3:
                flug, area, gap, photoname = paradetection.ParaDetection(
                    path_paradete, 320, 240, 200, 10, 120, 1)
                Xbee.str_trans(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
                Other.saveLog(log_paraavoidance, dateTime, time.time() - t_start, GPS.readGPS, flug, area,
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
        Other.saveLog(log_phase, '6', 'Melting phase start', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 6:
            t_start_panorama = time.time()  # プログラムの開始時刻
            panorama.shooting(path_src_panorama, path_dst_panoraam, 'panoramaShootingtest00')
            Xbee.str_trans(f'runTime_panorama:\t{time.time()-t_start_panorama}')
        Xbee.str_trans('#####-----panorama ended-----##### \n \n')
    except:
        Xbee.str_trans('#####-----Error(panorama)-----#####')
        Xbee.str_trans('#####-----Error(panorama)-----#####')
        Xbee.str_trans('#####-----Error(panorama)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------GPS--------------------------#######
    try:
        Xbee.str_trans('#####-----gps run start-----#####')
        Other.saveLog(log_phase, '7', 'Melting phase start', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        Xbee.str_trans(f'Phase:\t{phaseChk}')
        if phaseChk == 7:
            gpsrunning.gps_run()

    except:
        Xbee.str_trans('#####-----Error(gpsrunning)-----#####')
        Xbee.str_trans('#####-----Error(gpsrunning)-----#####')
        Xbee.str_trans('#####-----Error(gpsrunning)-----#####')

    ######------------------photo running---------------------##########
    try:
        Xbee.str_trans('#####-----photo run start-----#####')
        photorunning.image_guided_driving(path_photo_imagerun, G_thd)

    except:
        Xbee.str_trans('#####-----Error(Photo running)-----#####')
        Xbee.str_trans('#####-----Error(Photo running)-----#####')
        Xbee.str_trans('#####-----Error(Photo running)-----#####')
