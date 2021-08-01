import cv2
import os
import glob
import time

def panorama(srcdir, dstdir, srcprefix='', dstprefix='',srcext='.jpg',dstext='.jpg'):
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
            photos.append(cv2.imread(srcdir +'/' + srcprefix + '0' +  str(i) + srcext))
        else:
            photos.append(cv2.imread(srcdir + '/' + srcprefix + str(i) + srcext))




    stitcher = cv2.Stitcher.create(0)
    status, result = stitcher.stitch(photos)
    cv2.imwrite(dstdir + '/' + dstprefix + str(resultcount) + srcext, result)

    if status == 0:
        print("success")
    else:
        print('failed')

def shooting(l, r, t, magx_off, magy_off, path):
    """
    パノラマ撮影用の関数
    引数は磁気のオフセット
    """
    # photobox = []
    magdata = BMC050.mag_dataRead()
    magx = magdata[0]
    magy = magdata[1]
    preθ = Calibration.angle(magx, magy, magx_off, magy_off)
    sumθ = 0
    # Xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
    print(f'whileスタート　preθ:{preθ}')

    while sumθ <= 360:
        Capture.Capture(path)
        # filename = Capture.Capture(path)
        # photobox.append(filename)
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
        # Xbee.str_trans('sumθ:', sumθ, ' preθ:', preθ, ' deltaθ:', deltaθ)
        print(f'sumθ: {sumθ}  latestθ: {latestθ}  preθ: {preθ2}  deltaθ: {deltaθ}')


if __name__ == "__main__":
    try:
        srcdir = '/home/pi/Desktop/Cansat2021ver/test/nisho-ground12_640_asyuku'
        dstdir = '/home/pi/Desktop/Cansat2021ver/test/photostorage'
        startTime = time.time()  # プログラムの開始時刻
        panorama(srcdir, dstdir, 'panoramaShootingtest00')
        endTime = time.time() #プログラムの終了時間
        runTime = endTime - startTime
        print(runTime)
    except KeyboardInterrupt:
        print('Interrupted')
