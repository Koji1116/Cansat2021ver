import cv2
import os
import glob
import time

srcdir = '/home/pi/Desktop/Cansat2021ver/test/nisho-ground12_640_asyuku'
dstdir = '/home/pi/Desktop/Cansat2021ver/test/photostorage'


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

    for i in range(1, srcfilecount+1):
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


if __name__ == "__main__":
    try:
        startTime = time.time()  # プログラムの開始時刻
        panorama(srcdir, dstdir, 'comp_')
        endTime = time.time() #プログラムの終了時間
        runTime = endTime - startTime
        print(runTime)
    except KeyboardInterrupt:
        print('Interrupted')
