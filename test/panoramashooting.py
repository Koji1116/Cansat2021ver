import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Emvironmental')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
import panorama
import Capture
import time

srcdir = '/home/pi/Desktop/Cansat2021ver/test/photostorage'
dstdir = '/home/pi/Desktop/Cansat2021ver/test/panorama'


def panorama_shooting():
    """
    パノラマ撮影用の関数
    """
    number = int(input('何枚写真を撮りますか'))
    for i in range(number):
        print('写真を撮ります')
        for j in range(3):
            print(3-j)
            time.sleep(1)
        Captrue.Capture(path)
    
    if input('パノラマ合成しますか？y/n') == y:
        panoramatest.panorama(srcdir=srcdir, dstdir=dstdir)
    
    else:
        print('写真撮影お疲れさまでした。')


if __name__ == '__main__':
    panorama_shooting()