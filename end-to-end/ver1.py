import sys

sys.path.append('/home/pi/Desktop/Cansat2021ver/fall')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')
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
import Calibration

dateTime = datetime.datetime.now()

# variable for timeout
t_out_release = 50
t_out_land = 40

# variable for release
thd_press_release = 0.3
t_delta_release = 0.1

# variable for landing
thd_press_land = 0.15

# variable for Calibration
strength_l_cal = 20
strength_r_cal = -20
t_rotation_cal = 0.2
number_data = 30

# variable for panorama
strength_l_pano = 20
strength_r_pano = -20
t_rotation_pano = 0.15

# variable for GPSrun
lon2 = 35.
lat2 = 139.
th_distance = 10
t_adj_gps = 5

# variable for photorun
G_thd = 80
path_photo_imagerun = f'photostorage/ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}-{dateTime.minute}'

# log
log_phase = '/home/pi/Desktop/Cansat2021ver/log/phaseLog1.txt'
log_release = '/home/pi/Desktop/Cansat2021ver/log/releaselog1.txt'
log_landing = '/home/pi/Desktop/Cansat2021ver/log/landingLog1.txt'
log_melting = '/home/pi/Desktop/Cansat2021ver/log/meltingLog1.txt'
log_paraavoidance = 'home/pi/Desktop/Cansat2021ver/paraAvoidanceLog1.txt'
log_gpsrunning = '/home/pi/Desktop/Cansat2021ver/gpsrunningLog1.txt'
log_photorunning = '/home/pi/Desktop/Cansat2021ver/log/photorunning1.txt'

# photo path
path_src_panorama = '/home/pi/Desktop/Cansat2021ver/src_panorama/panoramaShooting00'
path_dst_panoraam = '/home/pi/Desktop/Cansat2021ver/dst_panorama'
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
        print('#####-----Setup Phase start-----#####')
        Other.saveLog(log_phase, "1", "Setup phase", dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        print(f'Phase:\t{phaseChk}')
        if phaseChk == 2:
            setup()
        print('#####-----Setup Phase ended-----##### \n \n')
    except:
        print('#####-----Error(setup)-----#####')
        print('#####-----Error(setup)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------Release--------------------------#######
    print('#####-----Release Phase start-----#####')
    Other.saveLog(log_phase, "2", "Release Phase Started", dateTime, time.time() - t_start)
    phaseChk = Other.phaseCheck(log_phase)
    print(f'Phase:\t{phaseChk}')
    if phaseChk == 2:
        t_release_start = time.time()
        i = 1
        try:
            while time.time() - t_release_start <= t_out_release:
                print(f'loop_release\t {i}')
                press_count_release, press_judge_release = release.pressdetect_release(thd_press_release,
                                                                                       t_delta_release)
                print(f'count:{press_count_release}\tjudge{press_judge_release}')
                Other.saveLog(log_release, dateTime, time.time() - t_start, GPS.readGPS,
                              BME280.bme280_read(), press_count_release, press_judge_release)
                if press_judge_release == 1:
                    print('Release\n \n')
                    break
                else:
                    print('Not Release\n \n')
                i += 1
            else:
                print('##--release timeout--##')
            print("######-----Released-----##### \n \n")
        except:
            print('#####-----Error(Release)-----#####')
            print('#####-----Error(Release)-----#####')
            print('#####-----Error(Release)-----#####')

    #######--------------------------Landing--------------------------#######
    try:
        print('#####-----Landing phase start-----#####')
        Other.saveLog(log_phase, '3', 'Landing phase', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        print(f'Phase:\t{phaseChk}')
        if phaseChk == 3:
            print(f'Landing Judgement Program Start\t{time.time() - t_start}')
            t_land_start = time.time()
            i = 1
            while time.time() - t_land_start <= t_out_land:
                print(f"loop_land\t{i}")
                press_count_release, press_judge_release = land.pressdetect_land(thd_press_land)
                print(f'count:{press_count_release}\tjudge{press_judge_release}')
                if press_judge_release == 1:
                    print('Landed')
                    break
                else:
                    print('Not Landed')
                Other.saveLog(log_landing, dateTime, time.time() - t_start, GPS.readGPS(),
                              BME280.bme280_read())
                i += 1
            else:
                print('Landed Timeout')
            Other.saveLog(log_landing, dateTime, time.time() - t_start, GPS.readGPS(),
                          BME280.bme280_read(), 'Land judge finished')
            print('######-----Landed-----######\n \n')
    except:
        print('#####-----Error(Landing)-----#####')
        print('#####-----Error(Landing)-----#####')
        print('#####-----Error(Landing)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------Escape--------------------------#######
    try:
        print('#####-----Melting phase start#####')
        Other.saveLog(log_phase, '4', 'Melting phase start', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        print(f'Phase:\t{phaseChk}')
        if phaseChk == 4:
            Other.saveLog(log_melting, dateTime, time.time() - t_start, GPS.readGPS(), "Melting Start")
            escape.escape()
            Other.saveLog(log_melting, dateTime, time.time() - t_start, GPS.readGPS(), "Melting Finished")
        print('########-----Melted-----#######\n \n')
    except:
        print('#####-----Error(melting)-----#####')
        print('#####-----Error(melting)-----#####')
        print('#####-----Error(melting)-----#####')
    #######-----------------------------------------------------------########

    exit()
    #######--------------------------Paraavo--------------------------#######
    try:
        print('#####-----Para avoid start-----#####')
        Other.saveLog(log_phase, '5', 'Melting phase start', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        print(f'Phase:\t{phaseChk}')
        count_paraavo = 0
        if phaseChk == 5:
            while count_paraavo < 3:
                flug, area, gap, photoname = paradetection.ParaDetection(
                    path_paradete, 320, 240, 200, 10, 120, 1)
                print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
                Other.saveLog(log_paraavoidance, dateTime, time.time() - t_start, GPS.readGPS, flug, area,
                              gap, photoname)
                paraavoidance.Parachute_Avoidance(flug, gap)
                if flug == -1 or flug == 0:
                    count_paraavo += 1
        print('#####-----ParaAvo Phase ended-----##### \n \n')
    except:
        print('#####-----Error(paraavo)-----#####')
        print('#####-----Error(paraavo)-----#####')
        print('#####-----Error(paraavo)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------panorama--------------------------#######
    try:
        print('#####-----panorama shooting start-----#####')
        Other.saveLog(log_phase, '6', 'panorama shooting phase start', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        print(f'Phase:\t{phaseChk}')
        if phaseChk == 6:
            t_start_panorama = time.time()  # プログラムの開始時刻
            magdata = Calibration.magdata_matrix(strength_l_cal, strength_r_cal, t_rotation_cal, number_data)
            panorama.shooting(strength_l_pano, strength_r_pano, t_rotation_pano)
            print(f'runTime_panorama:\t{time.time() - t_start_panorama}')
        print('#####-----panorama ended-----##### \n \n')
    except:
        print('#####-----Error(panorama)-----#####')
        print('#####-----Error(panorama)-----#####')
        print('#####-----Error(panorama)-----#####')
    #######-----------------------------------------------------------########

    #######--------------------------GPS--------------------------#######
    try:
        print('#####-----gps run start-----#####')
        Other.saveLog(log_phase, '7', 'Melting phase start', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        print(f'Phase:\t{phaseChk}')
        if phaseChk == 7:
            gpsrunning.drive(th_distance, t_adj_gps, log_gpsrunning)
    except:
        print('#####-----Error(gpsrunning)-----#####')
        print('#####-----Error(gpsrunning)-----#####')
        print('#####-----Error(gpsrunning)-----#####')

    ######------------------photo running---------------------##########
    try:
        print('#####-----photo run start-----#####')
        Other.saveLog(log_phase, '8', 'Melting phase start', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        print(f'Phase:\t{phaseChk}')
        if phaseChk == 8:
            photorunning.image_guided_driving(path_photo_imagerun, G_thd)
    except:
        print('#####-----Error(Photo running)-----#####')
        print('#####-----Error(Photo running)-----#####')
        print('#####-----Error(Photo running)-----#####')

    #####------------------panorama composition--------------##########
    try:
        print('#####-----panorama composition-----#####')
        Other.saveLog(log_phase, '8', 'Melting phase start', dateTime, time.time() - t_start)
        phaseChk = Other.phaseCheck(log_phase)
        print(f'Phase:\t{phaseChk}')
        if phaseChk == 9:
            panorama.composition(path_src_panorama, path_dst_panoraam)
    except:
        print('#####-----Error(panorama composition)-----#####')
        print('#####-----Error(panorama composition)-----#####')
        print('#####-----Error(panorama composition)-----#####')
