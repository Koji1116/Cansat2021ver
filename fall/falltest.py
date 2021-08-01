# -*- coding: utf-8 -*-
import sys

sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Melting')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Illuminance')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/test')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')

import time
import datetime
import pigpio
import Xbee
import mag
import BME280
import GPS
import melt
import paradetection
import paraavoidance
import Other
import panorama
import Calibration
import release
import land

# variable for phase Check
phaseChk = 0

gpsData = [0.0, 0.0, 0.0, 0.0, 0.0]
bme280Data = [0.0, 0.0, 0.0, 0.0]
bmx055data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

t_setup = 60  # variable to set waiting time after setup
t = 1  # Unknown Variable
t_out_release = 10  # time for release(loopx)
t_out_release_safe = 1000
t_out_land = 10  # time for land(loopy)

t_start = 0.0  # time when program started

# variable used for releasejudge
thd_press_release = 0.3
press_count_release = 0
press_judge_release = 0

releasealt = 2
GArepeasecount = 0
gpsreleasejudge = 0

pi = pigpio.pi()

# variable used for landjudgment
thd_press_land = 0.15
presslandjudge = 0
gpslandjudge = 0
acclandjudge = 0
Landjudgment = [presslandjudge, gpslandjudge, acclandjudge]

# variable used for ParaDetection
LuxThd = 100
imgpath_para = "/home/pi/Desktop/Cansat2021ver/photostorage/paradetection"
width = 320
height = 240
H_min = 200
H_max = 10
S_thd = 120

paraExsist = 0  # variable used for Para Detection

phaseLog = "/home/pi/Desktop/Cansat2021ver/log/phaseLog"
waitingLog = "/home/pi/Desktop/Cansat2021ver/log/waitingLog.txt"
releaseLog = "/home/pi/Desktop/Cansat2021ver/log/releaseLog.txt"
landingLog = "/home/pi/Desktop/Cansat2021ver/log/landingLog.txt"
meltingLog = "/home/pi/Desktop/Cansat2021ver/log/meltingLog.txt"
paraAvoidanceLog = "/home/pi/Desktop/Cansat2021ver/log/paraAvoidanceLog.txt"
path_src_panorama = '/home/pi/Desktop/Cansat2021ver/panorama_src'
path_dst_panoraam = '/home/pi/Desktop/Cansat2021ver/panorama_dst'


def setup():
    global phaseChk
    BME280.bme280_setup()
    BME280.bme280_calib_param()
    phaseChk = Other.phaseCheck(phaseLog)
    GPS.openGPS()
    print(phaseChk)


def close():
    GPS.closeGPS()


if __name__ == "__main__":
    Xbee.on()
    while 1:
        Xbee.str_trans('standby')
        if Xbee.str_receive() == 's':
            Xbee.str_trans('program start')
            break

    try:
        t_start = time.time()
        # ------------------- Setup Phase --------------------- #
        Other.saveLog(phaseLog, "1", "Setup phase", time.time() - t_start)
        print(f'Program Start  {time.time()}')
        Xbee.str_trans(f'Program Start:\t{time.time() - t_start}\n')
        Xbee.str_trans(f'Program Start:\t{datetime.datetime.now()}\n')
        setup()
        print(phaseChk)
        Xbee.str_trans(f'Phase:{phaseChk}')

        # ------------------- Waiting Phase --------------------- #
        Other.saveLog(phaseLog, "2", "Waiting Phase Started", time.time() - t_start)
        phaseChk = Other.phaseCheck(phaseLog)
        Xbee.str_trans(f'Phase:{phaseChk}')
        # if phaseChk == 2:
        #     t_wait_start = time.time()
        #     while time.time() - t_wait_start <= t_setup:
        #         Other.saveLog(waitingLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read(), TSL2572.read())
        #         print('Waiting')
        #         Xbee.str_trans('Sleep')
        #         time.sleep(1)
        #     Xbee.str_trans('Waiting Finished')

        # ------------------- Release Phase ------------------- #
        Other.saveLog(phaseLog, "3", "Release Phase Started", time.time() - t_start)
        phaseChk = Other.phaseCheck(phaseLog)
        Xbee.str_trans(f'Phase:{phaseChk}')
        if phaseChk == 3:
            t_release_start = time.time()
            print(f"Releasing Judgement Program Start  {time.time() - t_start}")
            # bme280Data = BME280.bme280_read()
            i = 1
            try:
                while time.time() - t_release_start <= t_out_release:
                    Xbee.str_trans(f'loop_release\t {i}')
                    press_count_release, press_judge_release = release.pressdetect_release(thd_press_release)
                    Xbee.str_trans(f'count:{press_count_release}\tjudge{press_judge_release}')
                    if press_judge_release == 1:
                        Xbee.str_trans('Released')
                        break
                    else:
                        Xbee.str_trans('Not Released')
                    Other.saveLog(releaseLog, time.time() - t_start, GPS.readGPS, BME280.bme280_read())
                    i += 1
                else:
                    # 落下試験用の安全対策（落下しないときにXbeeでプログラム終了)
                    while time.time() - t_release_start <= t_out_release_safe:
                        Xbee.str_trans('continue? y/n')
                        if Xbee.str_receive() == 'y':
                            break
                        elif Xbee.str_receive() == 'n':
                            exit()
                    Xbee.str_trans('release timeout')
            except KeyboardInterrupt:
                print('interrupted')
            Xbee.str_trans("######-----Released-----#####")

        # ------------------- Landing Phase ------------------- #
        Xbee.str_trans('#####-----Landing Phase start-----#####\n')
        Other.saveLog(phaseLog, "4", "Landing Phase Started", time.time() - t_start)
        phaseChk = Other.phaseCheck(phaseLog)
        Xbee.str_trans(f'Phase\t{phaseChk}')
        if phaseChk == 4:
            Xbee.str_trans(f'Landing Judgement Program Start  {time.time() - t_start}')
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
                Other.saveLog(landingLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read())
                i += 1
            else:
                Xbee.str_trans('Landed Timeout')
            Other.saveLog(landingLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read(), 'Land judge finished')
            Xbee.str_trans('######-----Landed-----######\n')

        # ------------------- Melting Phase ------------------- #
        Xbee.str_trans('#####-----Melting phase start#####\n')
        Other.saveLog(phaseLog, '5', 'Melting phase start', time.time() - t_start)
        phaseChk = Other.phaseCheck(phaseLog)
        Xbee.str_trans(f'Phase:\t {phaseChk}\n')
        if phaseChk == 5:
            Xbee.str_trans('Melting Phase Started')
            Other.saveLog(meltingLog, time.time() - t_start, GPS.readGPS(), "Melting Start")
            melt.down()
            Xbee.str_trans('Melting Finished')
            Other.saveLog(meltingLog, time.time() - t_start, GPS.readGPS(), "Melting Finished")
        Xbee.str_trans('########-----Melted-----##########\n')
        # ------------------- ParaAvoidance Phase ------------------- #
        Xbee.str_trans("#####-----ParaAvo phase start-----#####\n")
        Other.saveLog(phaseLog, "6", "ParaAvoidance Phase Started", time.time() - t_start)
        phaseChk = Other.phaseCheck(phaseLog)
        Xbee.str_trans(f'Phase:{phaseChk}')
        if phaseChk == 6:
            t_ParaAvoidance_start = time.time()
            t_parajudge = time.time()
            while time.time() - t_parajudge < 60:
                Luxflug, Lux = paradetection.ParaJudge(LuxThd)
                Xbee.str_trans(f'Luxflug: {Luxflug}\t lux: {Lux}\n')
                if Luxflug == 1:
                    Xbee.str_trans(f'rover is not covered with parachute. Lux: {Lux}\n')
                    break
                else:
                    print(f'rover is covered with parachute! Lux: {Lux}\n')
                    Xbee.str_trans(f'rover is covered with parachute! Lux: {Lux}\n')
                    time.sleep(1)
            Xbee.str_trans(f'Prachute avoidance Started{time.time() - t_start}\n')
            # --- first parachute detection ---#
            count_paraavo = 0
            while count_paraavo < 3:
                flug, area, gap, photoname = paradetection.ParaDetection(
                    "photostorage/para", 320, 240, 200, 10, 120, 1)
                Xbee.str_trans(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n')
                paraavoidance.Parachute_Avoidance(flug, gap)

                if flug == -1 or flug == 0:
                    count_paraavo += 1
            Xbee.str_trans('#####-----paraavoided-----#####\n')

        # ------------------- Panorama Shooting Phase ------------------- #
        mag.bmc050_setup()
        Xbee.str_trans('#####-----Panorama-----#####\n')
        Other.saveLog(phaseLog, '7', 'Panorama Shooting phase', time.time() - t_start)
        phaseChk = Other.phaseCheck(phaseLog)
        Xbee.str_trans(f'Phase: {phaseChk}\n')
        if phaseChk <= 7:
            t_PanoramaShooting_start = time.time()
            print(f'Panorama Shooting Phase Started {time.time() - t_start}')
            magdata = Calibration.magdata_matrix()
            magx_off, magy_off = Calibration.calculate_offset(magdata)
            panorama.shooting(20, -20, 0.2, magx_off, magy_off, path_src_panorama)
            panorama.composition(srcdir=path_src_panorama, dstdir=path_dst_panoraam)
        Xbee.str_trans('Progam Finished')
        close()
    except KeyboardInterrupt:
        close()
        print("Keyboard Interrupt")
    except Exception as e:
        Xbee.str_trans("error")
        close()
        Other.saveLog("/home/pi/Desktop/log/Cansat2021ver/errorLog.txt", t_start - time.time(), "Error")
