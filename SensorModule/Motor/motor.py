from gpiozero import Motor
from time import sleep
# ピン番号は仮
Rpin1 = 17
Rpin2 = 18

Lpin1 = 19
Lpin2 = 20


def motor_move(strength_r, strength_l, time):
    # ピン番号は仮
    Rpin1 = 17
    Rpin2 = 18
    Lpin1 = 19
    Lpin2 = 20
    # 前進
    if strength_r >= 0 & strength_l >= 0:
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


motor = Motor(Rpin1, Rpin2)
motor.forward(0.2)
sleep(2)
motor.backward(0.5)
sleep(3)
motor.stop()


motor = Motor(Lpin1, Lpin2)
motor.forward(0.2)
sleep(2)
motor.backward(0.5)
sleep(3)
motor.stop()
