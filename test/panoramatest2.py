import cv2
import os
import glob
import time



# def panorama(srcdir,prefex='',file='.jpg'):
#     srcfilecount = len(glob.glob1(srcdir + '/', '*'+file))
#     resultfilecount = len(glob.glob1('result/', srcdir+'*.jpg'))
#     photos = []
#
#     print(srcfilecount)
#     for i in range(1, srcfilecount + 1):
#         photos.append(cv2.imread(srcdir + '/' + prefex + str(i) + file, 0))
#
#     print(len(photos))
#
#     stitcher = cv2.Stitcher.create(0)
#     status, result = stitcher.stitch(photos)
#     print(f'status:{status}')
#     cv2.imwrite('result/' + srcdir + '-' + str(resultfilecount) + '.jpg', result)
#
#     if status == 0:
#         print("success")
#     else:
#         print('failed')

def panorama(srcdir, dstdir, start, end, srcprefix='',srcext='.jpg',dstext='.jpg'):
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
    resultcount = len(glob.glob1(dstdir, '*'+dstext))

    photos = []

    for i in range(start, end):
        photos.append(cv2.imread(srcdir +'/' + srcprefix + str(i) + srcext))

    stitcher = cv2.Stitcher.create(0)
    status, result = stitcher.stitch(photos)

    if status == 0:
        print("success")
    else:
        print('failed')

    cv2.imwrite(dstdir + '/' + str(resultcount+1) + srcext, result)


#
# def panorama2(srcdir, dstdir, srcdir2, dstdir2, srcdir3, dstdir3, srcprefix='',srcext='.jpg',dstext='.jpg'):
#     """
#     パノラマを合成するための関数
#     ソースディレクトリ内に合成用の写真を番号をつけて入れておく。（例：IMG0.jpg,IMG1.jpg）
#     宛先ディレクトリ内でソースディレクトリ＋番号の形でパノラマ写真が保存される。
#     撮影された写真次第ではパノラマ写真をできずエラーが出る可能性あるからtry,except必要？
#     srcdir:ソースディレクトリ
#     dstdir:宛先ディレクトリ
#     prefix:番号の前につける文字
#     srcext:ソースの拡張子
#     dstext:できたものの拡張子
#     """
#     try:
#         stitcher = cv2.Stitcher.create(0)
#         srcfilecount = len(glob.glob1(srcdir + '/', '*'+srcext))
#
#         #--------first--------#
#         photos = []
#         for i in range(1, (srcfilecount + 1):
#             photos.append(cv2.imread(srcdir +'/' + srcprefix + str(i) + srcext))
#
#         status = []
#         result = []
#         for i in range(0, 12, 2):
#             photo2 = []
#             photo2.append(photos[i])
#             photo2.append(photos[i+1])
#             status_box, result_box = stitcher.stitch(photo2)
#             status.append(status_box)
#             result.append(result_box)
#             resultfilecount = len(glob.glob1(dstdir, '*' + dstext))
#             cv2.imwrite(dstdir + '/' + str(resultfilecount+1) + srcext, result_box)
#
#         # print(f'status_first:{status}')
#
#         #--------second--------#
#         panorama(srcdir='result', dstdir='result2')
#         # srcfilecount2 = len(glob.glob1(srcdir2 + '/', '*' + srcext))
#         # photos = []
#         # for i in range(1, srcfilecount2+1):
#         #     photos.append(cv2.imread(srcdir2 + '/' + srcprefix + str(i) + srcext))
#         #
#         # print(f'len(photos):{len(photos)}')
#         # status = []
#         # result = []
#         # for i in range(0, 6, 2):
#         #     photo2 = []
#         #     photo2.append(photos[i])
#         #     photo2.append(photos[i + 1])
#         #     status_box, result_box = stitcher.stitch(photo2)
#         #     print(f'status:{status_box}')
#         #     status.append(status_box)
#         #     result.append(result_box)
#         #     resultfilecount = len(glob.glob1(dstdir2, '*' + dstext))
#         #     cv2.imwrite(dstdir2 + '/' + str(resultfilecount+1) + srcext, result_box)
#
#         # print(f'status_second:{status}')
#
#         #--------third-------#
#         # panorama(srcdir='result2', dstdir='result3')
#         # srcfilecount3 = len(glob.glob1(srcdir3 + '/', '*' + srcext))
#         # photos =[]
#         # for i in range(1, srcfilecount3 + 1):
#         #     photos.append(cv2.imread(srcdir3 + '/' + srcprefix + str(i) + srcext))
#         # print(len(photos))
#         # status, result = stitcher.stitch(photos)
#         # resultfilecount = len(glob.glob1(dstdir3, '*' + dstext))
#         # cv2.imwrite(dstdir3 + '/' + str(resultfilecount) + srcext, result[i])
#
#
#         # if status == 0:
#         #     print("success")
#         # else:
#         #     print('failed')
#
#     except KeyboardInterrupt:
#         print('Interrupted')
#
#     except Exception as e:
#         print(e.message)
#         print('end')

def panorama3(srcdir, dstdir):
    photos = []

    for i in range(1, 13):
        photos.append(cv2.imread(srcdir + '/' + str(i) + '.jpg'))

    stitcher = cv2.Stitcher.create(0)
    status, result = stitcher.stitch(photos)
    cv2.imwrite(dstdir + '/' + srcdir + '.jpg', result)

    if status == 0:
        print("success")
    else:
        print('failed')

def cutting(srcdir, dstdir, number, w=0.02, h=0.02):
    for i in range(1, number+1):
        photo = cv2.imread(srcdir + '/' + str(i) + '.jpg')
        height, width, _ = photo.shape[:3]
        width1, width2 = int(width * w), int(width * (1-w))
        height1, height2 = int(height * h), int(height * (1-h))
        img = photo[height1 : height2, width1 : width2]
        cv2.imwrite(dstdir + '/' + str(i) + '.jpg', img)

def panorama_fast(srcdir, dstdir, dstdir2, dstdir3, srcprefix='',srcext='.jpg',dstext='.jpg'):
    number = len(glob.glob1(srcdir + '/', '*' + srcext))
    panorama(srcdir, dstdir, 1, int(number/3), srcprefix, srcext, dstext)
    panorama(srcdir, dstdir, int(number/3)-2, int(number*2/3), srcprefix, srcext, dstext)
    panorama(srcdir, dstdir, int(number*2/3)-2, number+1, srcprefix, srcext, dstext)
    cutting(dstdir, dstdir2, 3)
    panorama(dstdir2, dstdir3, 1, 4)


if __name__ == '__main__':
    srdir = '/home/pi/Desktop/Cansat2021ver/test/nisho-ground12_640×480'
    dstdir = '/home/pi/Desktop/Cansat2021ver/test/result'
    dstdir2 = '/home/pi/Desktop/Cansat2021ver/test/result2'
    dstdir3 = '/home/pi/Desktop/Cansat2021ver/test/result3'

    #----ver1----#
    # t_start = time.time()
    # panorama(srcdir='nisho-ground12', dstdir='result', start=1, end=13)
    # print(time.time()-t_start)

    #-----ver10000000000000--------#
    # t_start = time.time()
    # panorama(srcdir='nisho-ground12_640×480', dstdir='result', start=1, end=4)
    # panorama(srcdir='nisho-ground12_640×480', dstdir='result', start=3, end=9)
    # panorama(srcdir='nisho-ground12_640×480', dstdir='result', start=7, end=13)
    # print(time.time()-t_start)
    # cutting(srcdir='result', dstdir='result2', number=3)
    # print(time.time()-t_start)
    # panorama(srcdir='result2', dstdir='result3', start=0, end=3)
    # print(time.time() - t_start)


    # # ----ver2----#
    # t_start = time.time()
    # panorama2(srcdir='nisho-ground12_640×480', dstdir='result', srcdir2='result', dstdir2='result2', srcdir3='result2', dstdir3='result3', srcprefix='',srcext='.jpg',dstext='.jpg')
    # runTime = time.time() - t_start
    # print(runTime)
    #
    # # ----ver3----#
    # t_start = time.time()
    # panorama3(srcdir='nisho-ground12_640×480', dstdir='result3')
    # runTime = time.time() - t_start
    # print(runTime)


    #--------ver4--------#
    t_start = time.time()
    panorama_fast(srcdir, dstdir='result', dstdir2='result2', dstdir3='result3')
    print(time.time() - t_start)
