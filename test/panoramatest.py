import cv2
import os
import glob
import time

srcdir = '/home/pi/Desktop/Cansat2021ver/test/photostorage'
dstdir = 'result'


def panorama(srcdir, dstdir, srcprefix='',srcext='.jpg',dstext='.jpg'):
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
        photos.append(cv2.imread(srcdir +'/' + '000' + str(i) + srcext))

    stitcher = cv2.Stitcher.create(0)
    status, result = stitcher.stitch(photos)
    cv2.imwrite(dstdir + '/' + srcdir + '-' + str(resultcount) + srcext, result)

    if status == 0:
        print("success")
    else:
        print('failed')


if __name__ == "__main__":
    try:
        startTime = time.time()  # プログラムの開始時刻
        panorama(srcdir, dstdir)
        endTime = time.time() #プログラムの終了時間
        runTime = endTime - startTime
        print(runTime)
    except Exception as e:
        print(e.message)
        print('Error')
