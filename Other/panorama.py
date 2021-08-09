import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')



import cv2
import os
import glob
import time
import panorama
import motor
import Capture
import BMC050
import Calibration
import Xbee


def composition(srcdir, dstdir, srcext='.jpg',dstext='.jpg'):
    """
    パノラマを合成するための関数
    ソースディレクトリ内に合成用の写真を番号をつけて入れておく。（例：IMG0.jpg,IMG1.jpg）
    宛先ディレクトリ内でソースディレクトリ＋番号の形でパノラマ写真が保存される。
    撮影された写真次第ではパノラマ写真をできずエラーが出る可能性あるからtry,except必要？
    srcdir:ソースディレクトリ
    dstdir:宛先ディレクトリ
    prefix:番号の前につける文字
    srcext:ソースの拡張子
    dstext:できたものの拡張子
    """
    srcfilecount = len(glob.glob1(srcdir + '/', '*'+srcext))
    resultcount = len(glob.glob1(dstdir, srcdir + '*'+dstext))
    print(srcfilecount)
    print(resultcount)

    photos = []

    for i in range(0, srcfilecount):
        if len(str(i)) == 1:
            photos.append(cv2.imread(srcdir +'/' + '0' +  str(i) + srcext))
        else:
            photos.append(cv2.imread(srcdir + '/' + str(i) + srcext))




    stitcher = cv2.Stitcher.create(0)
    status, result = stitcher.stitch(photos)
    cv2.imwrite(dstdir + '/' + str(resultcount) + srcext, result)

    if status == 0:
        print('composition succeed')

    else:
        print('composition failed')

def shooting(l, r, t, mag_mat, path):
    """
    パノラマ撮影用の関数
    引数は磁気のオフセット
    """
    # photobox = []
    _, _, _, magx_off, magy_off, _ = Calibration.calculate_offset(mag_mat)
    magdata = BMC050.mag_dataRead()
    magx = magdata[0]
    magy = magdata[1]
    preθ = Calibration.angle(magx, magy, magx_off, magy_off)
    sumθ = 0
    # Xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
    print(f'whileスタート　preθ:{preθ}')

    while sumθ <= 360:
        Capture.Capture(path)
        motor.move(l, r, t)
        magdata = BMC050.mag_dataRead()
        magx = magdata[0]
        magy = magdata[1]
        latestθ = Calibration.angle(magx, magy, magx_off, magy_off)

        # ------Stuck------#
        if preθ >= 300 and latestθ <= 100:
            latestθ += 360
            if latestθ - preθ <= 10:
                # Xbee.str_trans('Stuck')
                print('Stuck')
                motor.move(l, r, t)
                # ----Initialize-----#
                magdata = BMC050.mag_dataRead()
                magx = magdata[0]
                magy = magdata[1]
                preθ = Calibration.angle(magx, magy, magx_off, magy_off)
                sumθ = 0
                # Xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
                print(f'whileスタート　preθ:{preθ}')
                continue

        if preθ >= 300 and latestθ <= 100:
            latestθ += 360
        deltaθ = latestθ - preθ
        sumθ += deltaθ

        if latestθ >= 360:
            latestθ -= 360
        preθ2 = preθ
        preθ = latestθ
        # Xbee.str_trans(f'sumθ: {sumθ}  latestθ: {latestθ}  preθ: {preθ2}  deltaθ: {deltaθ}')
        print(f'sumθ: {sumθ}  latestθ: {latestθ}  preθ: {preθ2}  deltaθ: {deltaθ}')


if __name__ == "__main__":
    BMC050.BMC050_setup()
    motor.setup()
    try:
        srcdir = '/home/pi/Desktop/Cansat2021ver/photostorage/src_panorama/panoramaShooting'
        dstdir = '/home/pi/Desktop/Cansat2021ver/photostorage/dst_panorama'
        l = float(input('左の出力'))
        r = float(input('右の出力'))
        t = float(input('回転時間'))
        n = int(input('取得データ数は？'))
        magdata = Calibration.magdata_matrix(l, r, t, n)

        l = float(input('左の出力'))
        r = float(input('右の出力'))
        t = float(input('回転時間'))
        shooting(l, r, t, magdata, srcdir)
        t_start = time.time()  # プログラムの開始時刻
        composition(srcdir, dstdir)
        runTime = time.time() - t_start
        print(runTime)
    except KeyboardInterrupt:
        print('Interrupted')
