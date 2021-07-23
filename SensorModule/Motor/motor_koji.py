import sys
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Communication')
from gpiozero import Motor
from time import sleep
import time



# ピン番号は仮
Rpin1 = 5
Rpin2 = 6

Lpin1 = 9
Lpin2 = 10


def motor_stop(x=1):
    '''motor_move()とセットで使用'''
    Rpin1 = 5
    Rpin2 = 6
    Lpin1 = 9
    Lpin2 = 10
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
    Rpin1 = 5
    Rpin2 = 6
    Lpin1 = 9
    Lpin2 = 10
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
        motor_r.forkward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        time.sleep(t_moving)
    # 左回転
    elif strength_r < 0 and strength_l >= 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.backward(abs(strength_r))
        motor_l.forkward(abs(strength_l))
        time.sleep(t_moving)


def motor(strength_l, strength_r, t_moving, x=1):
    """
    急停止回避を組み込み 7/23 takayama
    テストまだ
    """
    motor_move(strength_l, strength_r, t_moving)
    t_stop = time.time()
    while time.time() - t_stop <= 1:
        coefficient_power = abs(1 - (time.time() - t_stop))
        motor_move(strength_l*coefficient_power, strength_r*coefficient_power, 0.1)
    motor_stop(x)

if __name__ == '__main__':
    while 1:
        command = input('操作\t')
        if command == 'a':
            motor(0.4, 0.8, 2)
        elif command == 'w':
            motor(0.8, 0.8, 2)
        elif command == 'd':
            motor(0.8, 0.4, 2)
        elif command == 's':
            motor(-0.5, -0.5, 2)
        elif command == 'manual':
            l = input('左の出力は？')
            r = input('右の出力は？')
            t = input('移動時間は？')
            time.sleep(0.8)
            motor(l, r, t)
        else:
            print('もう一度入力してください')