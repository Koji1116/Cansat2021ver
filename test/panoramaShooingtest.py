import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Emvironmental')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
import time
import Capture
import BMC050
import Xbee
from gpiozero import Motor
import numpy as np
import motor_koji
import math
import mag

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

def angle(magx, magy, magx_off=0, magy_off=0):
    θ = math.degrees(math.atan((magy - magy_off) / (magx - magx_off)))

    if magx - magx_off > 0 and magy - magy_off > 0:  # First quadrant
        pass  # 0 <= θ <= 90
    elif magx - magx_off < 0 and magy - magy_off > 0:  # Second quadrant
        θ = 180 + θ  # 90 <= θ <= 180
    elif magx - magx_off < 0 and magy - magy_off < 0:  # Third quadrant
        θ = θ + 180  # 180 <= θ <= 270
    elif magx - magx_off > 0 and magy - magy_off < 0:  # Fourth quadrant
        θ = 360 + θ  # 270 <= θ <= 360

    θ += 90
    if 360 <= θ <= 450:
        θ -= 360

    return θ

def panorama_shooting(l, r, t, magx_off, magy_off, path):
    """
    パノラマ撮影用の関数
    引数は磁気のオフセット
    """
    # photobox = []
    magdata = BMC050.mag_dataRead()
    magx = magdata[0]
    magy = magdata[1]
    preθ = angle(magx, magy, magx_off, magy_off)
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
        latestθ = angle(magx, magy, magx_off, magy_off)
        
        #------Stuck------#
        if latestθ - preθ <= 10:
            # Xbee.str_trans('Stuck')
            print('Stuck')
            motor_koji(l, r, t)
            #----Initialize-----#
            magdata = BMC050.mag_dataRead()
            magx = magdata[0]
            magy = magdata[1]
            preθ = angle(magx, magy, magx_off, magy_off)
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

def get_data():
    """
	MBC050からデータを得る
	"""
    try:
        magData = mag.mag_dataRead()
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print()
        print(e)
    # --- get magnet sensor data ---#
    magx = magData[0]
    magy = magData[1]
    magz = magData[2]
    return magx, magy, magz

def magdata_matrix(l, r, t, t_sleeptime=0.2):
    """
	キャリブレーション用の磁気値を得るための関数
	forループ内(run)を変える必要がある2021/07/04
	"""
    try:
        magx, magy, magz = get_data()
        magdata = np.array([[magx, magy, magz]])
        for _ in range(60):
            motor_koji(l, r, t)
            magx, magy, magz = get_data()
            # --- multi dimention matrix ---#
            magdata = np.append(magdata, np.array([[magx, magy, magz]]), axis=0)
            time.sleep(t_sleeptime)
    except KeyboardInterrupt:
        print('Interrupt')
    except Exception as e:
        print(e.message())
    return magdata

def calculate_offset(magdata):
    """
    オフセットを計算する関数
    """
    # --- manage each element sepalately ---#
    magx_array = magdata[:, 0]
    magy_array = magdata[:, 1]
    magz_array = magdata[:, 2]

    # --- find maximam GPS value and minimam GPS value respectively ---#
    magx_max = magx_array[np.argmax(magx_array)]
    magy_max = magy_array[np.argmax(magy_array)]
    magz_max = magz_array[np.argmax(magz_array)]

    magx_min = magx_array[np.argmin(magx_array)]
    magy_min = magy_array[np.argmin(magy_array)]
    magz_min = magz_array[np.argmin(magz_array)]

    # --- calucurate offset ---#
    magx_off = (magx_max + magx_min) / 2
    magy_off = (magy_max + magy_min) / 2
    magz_off = (magz_max + magz_min) / 2
    return magx_array, magy_array, magz_array, magx_off, magy_off, magz_off

if __name__ == '__main__':
    path = 'photostorage/panoramaShootingtest'
    l = float(input('左モータの出力を入力してください\t'))
    r = float(input('右モータの出力を入力してください\t'))
    t = float(input('一回転の回転時間を入力してください\t'))
    t_start = time.time()
    magdata = magdata_matrix(l, r, t)
    magx_array, magy_array, magz_array, magx_off, magy_off, magz_off = calculate_offset(magdata)
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



