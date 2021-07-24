import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Emvironmental')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
import time
import panorama
import Capture
import BMC050
import Xbee
import motor


import Calibration

def panorama_shooting(l, r, t, magx_off, magy_off, path):
    """
    パノラマ撮影用の関数
    引数は磁気のオフセット
    """
    # photobox = []
    magdata = BMC050.mag_dataRead()
    magx = magdata[0]
    magy = magdata[1]
    preθ = Calibration.calculate_angle_2D(magx, magy, magx_off, magy_off)
    sumθ = 0
    deltaθ = 0
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
        latestθ = Calibration.calculate_angle_2D(magx, magy, magx_off, magy_off)
        
        #------Stuck------#
        if latestθ - preθ <= 10:
            # Xbee.str_trans('Stuck')
            print('Stuck')
            motor.move(1, 1, 3)
            #----Initialize-----#
            magdata = BMC050.mag_dataRead()
            magx = magdata[0]
            magy = magdata[1]
            preθ = Calibration.calculate_angle_2D(magx, magy, magx_off, magy_off)
            sumθ = 0
            deltaθ = 0
            # Xbee.str_trans('whileスタート preθ:{0}'.format(preθ))
            print(f'whileスタート　preθ:{preθ}')
            continue
        
        if preθ >= 300 and latestθ <= 100:
            latestθ += 360
        deltaθ = preθ - latestθ
        sumθ += deltaθ
        
        if latestθ >= 360:
            latestθ -= 360
        preθ = latestθ
        # Xbee.str_trans('sumθ:', sumθ, ' preθ:', preθ, ' deltaθ:', deltaθ)
        print(f'sumθ:{sumθ} preθ:{preθ} deltaθ:{deltaθ}')


if __name__ == '__main__':
    path = 'photostorage/panoramaShootingtest'
    l = float(input('左モータの出力を入力してください\t'))
    r = float(input('右モータの出力を入力してください\t'))
    t = float(input('一回転の回転時間を入力してください\t'))
    t_start = time.time()
    magdata = Calibration.magdata_matrix(l, r, t)
    magx_array, magy_array, magz_array, magx_off, magy_off, magz_off = Calibration.calculate_offset(magdata)
    print(f'キャリブレーション終了:{time.time()-t_start}')
    while 1:
        l = float(input('左モータの出力を入力してください\t'))
        r = float(input('右モータの出力を入力してください\t'))
        t = float(input('一回転の回転時間を入力してください\t'))
        t_start = time.time()
        panorama_shooting(l, r, t, magx_off, magy_off, path)
        print(time.time() - t_start)

        composition = input('パノラマ合成しますか？')

        again = input('もう一度，写真撮影を行いますか？Y/N\t')
        if again == 'Y':
            pass
        elif again == 'N':
            print('END')
            break
        else:
            print('Y/N')



