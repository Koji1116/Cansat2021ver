from gpiozero import Motor
from time import sleep

import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')

Rpin1 = 17
Rpin2 = 18

Lpin1 = 19
Lpin2 = 20


def motor_move(strength_r, strength_l, time):
    # ピン番号は仮
    Rpin1 = 5
    Rpin2 = 6
    Lpin1 = 9
    Lpin2 = 10
    # 前進
    if strength_r >= 0 and strength_l >= 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
       
        motor_r.forward(strength_r)
        motor_l.forward(strength_l)
        sleep(time)
    # 後進
    elif strength_r < 0 & strength_l < 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
      
        motor_r.backward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        sleep(time)
    # 右回転
    elif strength_r >= 0 & strength_l < 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        
        motor_r.forkward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        sleep(time)
    # 左回転
    elif strength_r < 0 & strength_l >= 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.backward(abs(strength_r))
        motor_l.forkward(abs(strength_l))
        sleep(time)

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
    sleep(x)

motor_move(0.5, 0.5, 10)
motor_stop()


#motor = Motor(Rpin1, Rpin2)
# motor.forward(0.2)
# sleep(2)
# motor.backward(0.5)
# sleep(3)
# motor.stop()


#motor = Motor(Lpin1, Lpin2)
# motor.forward(0.2)
# sleep(2)
# motor.backward(0.5)
# sleep(3)
# motor.stop()
