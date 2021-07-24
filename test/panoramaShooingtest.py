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
from gpiozero import Motor
import Calibration

Rpin1 = 5
Rpin2 = 6

Lpin1 = 9
Lpin2 = 10

def motor_stop(x=1):
    '''motor_move()とセットで使用'''
    motor_r = Motor(Rpin1, Rpin2)
    motor_l = Motor(Lpin1, Lpin2)
    motor_r.stop()
    motor_l.stop()
    time.sleep(x)


def motor_move(strength_l, strength_r, t_moving):
    '''
    引数は左のmotorの強さ、右のmotorの強さ、走る時間。
    strength_l、strength_rは-1~1で表す。負の値だったら後ろ走行。
    必ずmotor_stop()セットで用いる。めんどくさかったら下にあるmotor()を使用
    '''
    # 前進するときのみスタック判定
    if strength_r >= 0 and strength_l >= 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.forward(strength_r)
        motor_l.forward(strength_l)
        time.sleep(t_moving)
    # 後進
    elif strength_r < 0 and strength_l < 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.backward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        time.sleep(t_moving)
    # 右回転
    elif strength_r >= 0 and strength_l < 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.forward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        time.sleep(t_moving)
    # 左回転
    elif strength_r < 0 and strength_l >= 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.backward(abs(strength_r))
        motor_l.forward(abs(strength_l))
        time.sleep(t_moving)


def motor_koji(strength_l, strength_r, t_moving, x=1):
    """
    急停止回避を組み込み 7/23 takayama
    テストまだ
    """
    strength_r /= 100
    strength_l /= 100
    motor_move(strength_l, strength_r, t_moving)
    t_stop = time.time()
    if abs(strength_l) == abs(strength_r):
        motor_stop(x)
    else:
        while time.time() - t_stop <= 1:
            coefficient_power = abs(1 - (time.time() - t_stop))
            motor_move(strength_l*coefficient_power, strength_r*coefficient_power, 0.1)
    motor_stop(x)

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
        motor_koji(l, r, t)
        magdata = BMC050.mag_dataRead()
        magx = magdata[0]
        magy = magdata[1]
        latestθ = Calibration.calculate_angle_2D(magx, magy, magx_off, magy_off)
        
        #------Stuck------#
        if latestθ - preθ <= 10:
            # Xbee.str_trans('Stuck')
            print('Stuck')
            motor_koji(l, r, t)
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



