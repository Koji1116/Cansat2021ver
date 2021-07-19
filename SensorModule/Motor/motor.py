import sys
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Communication')
from gpiozero import Motor
from time import sleep
import time
import BMC050
import stuck
import Xbee


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


def motor_move(strength_l, strength_r, time):
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
        sleep(time)
    # 後進
    elif strength_r < 0 and strength_l < 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.backward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        sleep(time)
    # 右回転
    elif strength_r >= 0 and strength_l < 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.forkward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        sleep(time)
    # 左回転
    elif strength_r < 0 and strength_l >= 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.backward(abs(strength_r))
        motor_l.forkward(abs(strength_l))
        sleep(time)


def motor(strength_l, strength_r, time, x=1):
    motor_move(strength_l, strength_r, time)
    motor_stop(x)

#motor(0.8,0.8,3)
motor_r = Motor(5, 6)
motor_l = Motor(9, 10)
motor_r.stop()
motor_l.stop()