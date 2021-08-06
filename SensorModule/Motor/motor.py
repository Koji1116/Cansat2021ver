import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
from gpiozero import Motor
from time import sleep
import time
import acc

def motor_stop(x=1):
    '''motor_move()とセットで使用'''
    Rpin1 = 5
    Rpin2 = 6
    Lpin1 = 10
    Lpin2 = 9
    motor_r = Motor(Rpin1, Rpin2)
    motor_l = Motor(Lpin1, Lpin2)
    motor_r.stop()
    motor_l.stop()
    time.sleep(x)


def motor_move_acc(strength_l, strength_r, t_moving):
    '''
    引数は左のmotorの強さ、右のmotorの強さ、走る時間。
    strength_l、strength_rは-1~1で表す。負の値だったら後ろ走行。
    必ずmotor_stop()セットで用いる。めんどくさかったら下にあるmotor()を使用
    
    '''
    acc.bmc050_setup()
    Rpin1 = 5
    Rpin2 = 6
    Lpin1 = 10
    Lpin2 = 9
    # 前進するときのみスタック判定
    if strength_r >= 0 and strength_l >= 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.forward(strength_r)
        motor_l.forward(strength_l)
        print(acc.acc_dataRead())
    # 後進
    elif strength_r < 0 and strength_l < 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.backward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        print(acc.acc_dataRead())

    # 右回転
    elif strength_r >= 0 and strength_l < 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.forward(abs(strength_r))
        motor_l.backward(abs(strength_l))
        print(acc.acc_dataRead())

    # 左回転
    elif strength_r < 0 and strength_l >= 0:
        motor_r = Motor(Rpin1, Rpin2)
        motor_l = Motor(Lpin1, Lpin2)
        motor_r.backward(abs(strength_r))
        motor_l.forward(abs(strength_l))
        print(acc.acc_dataRead())



def motor_move(strength_l, strength_r, t_moving):
    '''
    引数は左のmotorの強さ、右のmotorの強さ、走る時間。
    strength_l、strength_rは-1~1で表す。負の値だったら後ろ走行。
    必ずmotor_stop()セットで用いる。めんどくさかったら下にあるmotor()を使用
    '''
    Rpin1 = 5
    Rpin2 = 6
    Lpin1 = 10
    Lpin2 = 9
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

def move_acc(strength_l, strength_r, t_moving, x=0.1):
    """
    急停止回避を組み込み 7/23 takayama
    """
    strength_r /= 100
    strength_l /= 100
    motor_move_acc(strength_l, strength_r, t_moving)
    t_stop = time.time()
    if abs(strength_l) == abs(strength_r) and strength_l * strength_r < 0:
        motor_stop(x)
    else:
        #before
        # while time.time() - t_stop <= 1:
        #     coefficient_power = abs(1 - (time.time() - t_stop))
        #     motor_move(strength_l*coefficient_power, strength_r*coefficient_power, 0.1)


        #更新(2021-07-24)
        for i in range(10):
            coefficient_power = 10 - i
            coefficient_power /= 10
            motor_move(strength_l * coefficient_power, strength_r * coefficient_power, 0.1)
            if i == 9:
                motor_stop(x)


def move(strength_l, strength_r, t_moving, x=0.1):
    """
    急停止回避を組み込み 7/23 takayama
    """
    strength_r /= 100
    strength_l /= 100
    motor_move(strength_l, strength_r, t_moving)
    t_stop = time.time()
    if abs(strength_l) == abs(strength_r) and strength_l * strength_r < 0:
        motor_stop(x)
    else:
        #before
        # while time.time() - t_stop <= 1:
        #     coefficient_power = abs(1 - (time.time() - t_stop))
        #     motor_move(strength_l*coefficient_power, strength_r*coefficient_power, 0.1)


        #更新(2021-07-24)
        for i in range(10):
            coefficient_power = 10 - i
            coefficient_power /= 10
            motor_move(strength_l * coefficient_power, strength_r * coefficient_power, 0.1)
            if i == 9:
                motor_stop(x)



if __name__ == '__main__':
    # while 1:
    #     command = input('操作\t')
    #     if command == 'a':
    #         move(40, 80, 2)
    #     elif command == 'w':
    #         move(80, 80, 2)
    #     elif command == 'd':
    #         move(80, 40, 2)
    #     elif command == 's':
    #         move(-50, -50, 2)
    #     elif command == 'manual':
    #         l = float(input('左の出力は？'))
    #         r = float(input('右の出力は？'))
    #         t = float(input('移動時間は？'))
    #         time.sleep(0.8)
    #         move(l, r, t)
    #     else:
    #         print('もう一度入力してください')


    while 1:
        command = input('操作\t')
        if command == 'a':
            while 1:
                motor_move_acc(40, -40, 2)
        elif command == 'w':
            motor_move_acc(80, 80, 2)
        elif command == 'd':
            motor_move_acc(80, 40, 2)
        elif command == 's':
            motor_move_acc(-50, -50, 2)
        elif command == 'manual':
            l = float(input('左の出力は？'))
            r = float(input('右の出力は？'))
            t = float(input('移動時間は？'))
            time.sleep(0.8)
            motor_move_acc(l, r, t)
        else:
            print('もう一度入力してください')