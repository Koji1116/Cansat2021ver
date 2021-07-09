from time import sleep
from gpiozero import Motor
import BMC050
import Xbee
import stuck
import motor
import sys
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Motor')


def stuck_jud(thd=10):  # しきい値thd調整必要
    BMC050.bmc050_setup()
    accdata = BMC050.acc_data()
    acc_x = accdata[0]
    acc_y = accdata[1]
    acc_z = accdata[2]
    acc = (acc_x**2 + acc_y**2 + acc_z**2)**0.5
    if acc < thd:
        print('スタックした')
        Xbee.str_trans('スタックした')
        return True
    else:
        print('まだしてない')
        Xbee.str_trans('まだしてない')
        return False


def stuck_avoid_move(x):
    if x == 0:
        Xbee.str_trans('sutck_avoid_move():0')
        motor.motor_move(1, 1, 5)
        motor.stop()
        sleep(0.5)
        motor.motor_move(0.8, 0.8, 0.2)
    elif x == 1:
        Xbee.str_trans('sutck_avoid_move():1')
        motor.motor_move(-1, -1, 5)
        motor.stop()
        sleep(0.5)
        motor.motor_move(-0.8, -0.8, 0.2)
    elif x == 2:
        Xbee.str_trans('sutck_avoid_move():2')
        motor.motor_move(0, 1, 5)
        motor.stop()
        sleep(0.5)
        motor.motor_move(0.8, 0.8, 0.2)

    elif x == 3:
        Xbee.str_trans('sutck_avoid_move():3')
        motor.motor_move(1, 0, 5)
        motor.stop()
        sleep(0.5)
        motor.motor_move(0.8, 0.8, 0.2)

    elif x == 4:
        Xbee.str_trans('sutck_avoid_move():4')
        motor.motor_move(0, -1, 5)
        motor.stop()
        sleep(0.5)
        motor.motor_move(-0.8, -0.8, 0.2)

    elif x == 5:
        Xbee.str_trans('sutck_avoid_move():5')
        motor.motor_move(-1, 0, 5)
        motor.stop()
        sleep(0.5)
        motor.motor_move(-0.8, -0.8, 0.2)

    elif x == 6:
        Xbee.str_trans('sutck_avoid_move():6')
        motor.motor_move(1, -1, 5)
        motor.stop()
        sleep(0.5)
        motor.motor_move(0.8, -0.8, 0.2)
        sleep(0.2)


# ここ途中
def stuck_avoid():
    Xbee.str_trans('スタック回避開始')
    flag = False
    while 1:
        # 1,2,3,4
        for i in range(1, 5, 1):
            stuck.stuck_avoid_move(i)
            bool_stuck = stuck.stuck_jug()
            motor.motor_stop()
            if bool_stuck == False:
                if i == 3:
                    # 後進でスタックした場合は、それをよける関数
                flag = True
                break
        if flag:
            break
        # 4,3,2,1
        for i in 4:
            stuck.stuck_avoid_move(4-i)
            bool_stuck = stuck.stuck_jug()
            motor.motor_stop()
            if bool_stuck == False:
                if i == 3:
                    # 後進でスタックした場合は、それをよける関数
                flag = True
                break
        if flag:
            break
    Xbee.str_trans('スタック回避完了')


if __name__ == '__main__':
    Rpin1 = 17
    Rpin2 = 18

    Lpin1 = 19
    Lpin2 = 20
    stuck(12)
