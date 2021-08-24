import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')

import datetime
import cv2
import os
import glob
import time
import shutil
import random

import motor
import Capture
import BMC050
import Calibration
import Xbee
import paraavoidance
import paradetection
import stuck
import Other


def shooting_angle(theta, path_src_panorama1, path_src_panorama2, path_src_panorama3, dict_angle1, dict_angle2, dict_angle3,
                   wid, hig):
    """
    パノラマ合成用の写真を適切な枚数，適切なディレクトリに保存するための関数
    関数shooting内で使用
    """
    switch = True

    if switch:
        for i in range(12):
            if 30 * i <= theta and theta <= 10 + 30 * i and not dict_angle1[i + 1]:
                Capture.Capture(path_src_panorama1, wid, hig)
                dict_angle1[i + 1] = True
                print(dict_angle1)
                switch = False
                break

    if switch:
        for i in range(12):
            if 10 + 30 * i <= theta and theta <= 20 + 30 * i and not dict_angle2[i + 1]:
                Capture.Capture(path_src_panorama2, wid, hig)
                dict_angle2[i + 1] = True
                print(dict_angle2)
                switch = False
                break

    if switch:
        for i in range(12):
            if 20 + 30 * i <= theta and theta <= 30 + 30 * i and not dict_angle3[i + 1]:
                Capture.Capture(path_src_panorama3, wid, hig)
                dict_angle3[i + 1] = True
                print(dict_angle3)
                break
    return dict_angle1, dict_angle2, dict_angle3


def check(dict_angle1, dict_angle2, dict_angle3, path_src_panorama1, path_src_panorama2, path_src_panorama3):
    """
    12枚の写真が撮影されたかを判断するための関数
    shooting内で使用
    戻り値はsrcdir
    12枚の写真が撮影された場合は，該当するパス(''じゃない)を返す。elseの場合は''を返す。
    """
    srcdir = ''

    number_photos1 = list(dict_angle1.values()).count(True)
    number_photos2 = list(dict_angle2.values()).count(True)
    number_photos3 = list(dict_angle3.values()).count(True)

    srcdir = path_src_panorama1 if number_photos1 == 12 else srcdir
    srcdir = path_src_panorama2 if number_photos2 == 12 else srcdir
    srcdir = path_src_panorama3 if number_photos3 == 12 else srcdir

    return srcdir


def initialize(path_src_panorama1, path_src_panorama2, path_src_panorama3):
    """
    初期化のための関数
    関数shooting内で使用
    引数は撮影した写真のパス
    戻り値はshooting内で使う変数
    """
    # Initialize the directory 1
    rfd1 = path_src_panorama1.rfind('/')
    dir_src_panorama1 = path_src_panorama1[:rfd1]
    shutil.rmtree(dir_src_panorama1)
    os.mkdir(dir_src_panorama1)
    # Initialize the directory 2
    rfd2 = path_src_panorama2.rfind('/')
    dir_src_panorama2 = path_src_panorama1[:rfd2]
    shutil.rmtree(dir_src_panorama2)
    os.mkdir(dir_src_panorama2)
    # Initialize the directory 3
    rfd3 = path_src_panorama3.rfind('/')
    dir_src_panorama3 = path_src_panorama1[:rfd3]
    shutil.rmtree(dir_src_panorama3)
    os.mkdir(dir_src_panorama3)
    # Initializing variables
    count_panorama = 0
    count_stuck = 0
    dict_angle1 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False,
                   7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    dict_angle2 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False,
                   7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    dict_angle3 = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False,
                   7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
    return count_panorama, count_stuck, dict_angle1, dict_angle2, dict_angle3


def shooting(strength_l_pano, strength_r_pano, t_rotation_pano, mag_mat, path_src_panorama1, path_src_panorama2,
             path_src_panorama3, path_paradete, log_panoramashooting, wid=320, hig=240):
    """
    パノラマ撮影用の関数
    引数は回転時のモータパワー，1回の回転時間，磁気データ，写真保存用のパス，パラシュート検知のパス，ログ保存用のパス
    スタック判定は角度変化が10度未満が4回あった場合
    スタック時はその場所からパラシュートを確認しながら離れ，やり直す
    スタックによってパノラマ撮影をやり直す回数は3回
    """
    # Initialization by function
    count_panorama, count_stuck, dict_angle1, dict_angle2, dict_angle3 = initialize(path_src_panorama1,
                                                                                    path_src_panorama2,
                                                                                    path_src_panorama3)
    _, _, _, magx_off, magy_off, _ = Calibration.calculate_offset(mag_mat)
    magdata = BMC050.mag_dataRead()
    magx = magdata[0]
    magy = magdata[1]
    preθ = Calibration.angle(magx, magy, magx_off, magy_off)
    sumθ = 0
    # Xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
    print(f'whileスタート　preθ:{preθ}')

    while 1:
        dict_angle1, dict_angle2, dict_angle3 = shooting_angle(preθ, path_src_panorama1, path_src_panorama2,
                                                               path_src_panorama3, dict_angle1, dict_angle2,
                                                               dict_angle3, wid, hig)
        srcdir = check(dict_angle1, dict_angle2, dict_angle3, path_src_panorama1, path_src_panorama2,
                           path_src_panorama3)
        if srcdir:
            break
        motor.move(strength_l_pano, strength_r_pano, t_rotation_pano)
        magdata = BMC050.mag_dataRead()
        magx = magdata[0]
        magy = magdata[1]
        latestθ = Calibration.angle(magx, magy, magx_off, magy_off)

        if preθ >= 300 and latestθ <= 100:
            latestθ += 360

        deltaθ = latestθ - preθ

        if deltaθ:
            count_stuck += 1
            # ------Stuck------#
            if count_stuck >= 4:
                count_panorama += 1
                if count_panorama >= 3:
                    break
                count_stuck = 0
                # Xbee.str_trans('Stuck')
                print(f'Stuck: {deltaθ}')
                motor.move(60, 60, 0.5)
                flug, area, gap, photoname = paradetection.ParaDetection(path_paradete, 320, 240, 200, 10, 120, 1)
                print(f'flug:{flug}\tarea:{area}\tgap:{gap}\tphotoname:{photoname}\n \n')
                paraavoidance.Parachute_Avoidance(flug, gap)
                # ----Initialize-----#
                count_panorama, count_stuck, dict_angle1, dict_angle2, dict_angle3 = initialize(path_src_panorama1,
                                                                                                path_src_panorama2,
                                                                                                path_src_panorama3)
                magdata = BMC050.mag_dataRead()
                magx = magdata[0]
                magy = magdata[1]
                preθ = Calibration.angle(magx, magy, magx_off, magy_off)
                sumθ = 0
                # Xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
                print(f'whileスタート　preθ:{preθ}')
                continue

        deltaθ = latestθ - preθ
        sumθ += deltaθ

        if latestθ >= 360:
            latestθ -= 360
        preθ2 = preθ
        preθ = latestθ
        # Xbee.str_trans(f'sumθ: {sumθ}  latestθ: {latestθ}  preθ: {preθ2}  deltaθ: {deltaθ}')
        print(f'sumθ:\t{sumθ}\tlatestθ\t{latestθ}\tpreθ\t{preθ2}\tdeltaθ\t{deltaθ}\n')
        print(dict_angle1)
        print('\n')
        print(dict_angle2)
        print('\n')
        print(dict_angle3)
        Other.saveLog(log_panoramashooting, datetime.datetime.now(), sumθ, latestθ, preθ2, deltaθ)

    return srcdir


def composition(srcdir, srcext='.jpg', dstext='.jpg'):
    """
    パノラマを合成するための関数
    ソースディレクトリ内に合成用の写真を番号をつけて入れておく。（例：IMG0.jpg,IMG1.jpg）
    宛先ディレクトリ内で番号(0~).(拡張子)の形でパノラマ写真が保存される。
    srcdir:ソースディレクトリ
    srcext:ソースの拡張子
    dstext:パノラマ写真の拡張子
    """
    srcfilecount = len(glob.glob1('/home/pi/Desktop/Cansat2021ver/src_panorama', 'panoramaShooting' + '*' + srcext))
    resultcount = len(glob.glob1('/home/pi/Desktop/Cansat2021ver/dst_panorama', '*' + dstext))
    print(srcfilecount)
    print(resultcount)

    photos = []

    for i in range(0, srcfilecount):
        if len(str(i)) == 1:
            photos.append(cv2.imread(srcdir + '000' + str(i) + srcext))
        else:
            photos.append(cv2.imread(srcdir + '00' + str(i) + srcext))
    print(photos)
    print(len(photos))

    stitcher = cv2.Stitcher.create()
    status, result = stitcher.stitch(photos)
    if status == 0:
        print('composition succeed')

    else:
        print('composition failed')
    cv2.imwrite('/home/pi/Desktop/Cansat2021ver/dst_panorama/' + str(resultcount) + '.jpg', result)


if __name__ == "__main__":
    # Initialization
    BMC050.BMC050_setup()
    motor.setup()
    path_src_panorama1 = '/home/pi/Desktop/Cansat2021ver/src_panorama1/panoramaShooting'
    path_src_panorama2 = '/home/pi/Desktop/Cansat2021ver/src_panorama2/panoramaShooting'
    path_src_panorama3 = '/home/pi/Desktop/Cansat2021ver/src_panorama3/panoramaShooting'
    path_dst_panoraam = '/home/pi/Desktop/Cansat2021ver/dst_panorama'
    path_paradete = '/home/pi/Desktop/Cansat2021ver/photostorage/paradete'
    log_panoramashooting = Other.fileName('/home/pi/Desktop/Cansat2021ver/log/panoramaLog', 'txt')

    mag_mat = Calibration.magdata_matrix(40, -40, 100)
    power = random.randint(20, 60)
    strength_l_pano = power
    strength_r_pano = power * -1
    t_rotation_pano = 0.1
    srcdir = shooting(strength_l_pano, strength_r_pano, t_rotation_pano, mag_mat, path_src_panorama1,
                      path_src_panorama2, path_src_panorama3, path_paradete, log_panoramashooting)

    if input('Composition y/n \t') == y:
        t_start = time.time()  # プログラムの開始時刻
        composition(srcdir)
        runTime = time.time() - t_start
        print(runTime)
