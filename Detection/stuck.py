
import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
from time import sleep
import time
#from SensorModule.GPS.GPS_Navigate import vincenty_inverse
from math import*
from gpiozero import Motor
import BMC050
import Xbee
import stuck
import motor
import GPS_Navigate
import GPS
import acc

def ue_jug():
    ue_count = 0
    """
    ローバーの状態を確認する関数
    通常状態：True
    逆さになってる：False
    加速度センサZ軸の正負で判定するよ
    """
    while 1:
        accdata = acc.acc_dataRead()
        z = accdata[2]
        if z >= 0 :
            break
        else:
            if ue_count > 2:
                motor.move(30, 30, 0.008)
            else:
                motor.move(12, 12, 0.2)
            time.sleep(2)
            ue_count = +1


def stuck_jug(lat1, lon1, lat2, lon2, thd = 1.0 ):
    data_stuck =GPS_Navigate.vincenty_inverse(lat1, lon1, lat2, lon2)
    if data_stuck['distance'] <= thd:
        print(str(data_stuck['distance']) + '----スタックした')
        return False
    else:
        print(str(data_stuck['distance']) + '----スタックしてないよ')
        return True



def stuck_avoid_move(x):
    if x == 0:
        print('sutck_avoid_move():0')
        motor.move(100, 100, 5)
        motor.move(60, 60, 3)
    elif x == 1:
        print('sutck_avoid_move():1')
        motor.move(-100, -100, 5)
        motor.move(-60, -60, 3)
    elif x == 2:
        print('sutck_avoid_move():2')
        motor.move(80, 100, 5)
        motor.move(60, 60, 3)

    elif x == 3:
        print('sutck_avoid_move():3')
        motor.move(100, 80, 5)
        motor.move(60, 60, 3)

    elif x == 4:
        print('sutck_avoid_move():4')
        motor.move(-80, -100, 5)
        motor.move(-60, -60, 3)

    elif x == 5:
        print('sutck_avoid_move():5')
        motor.move(-100, -80, 5)
        motor.move(-60, -60, 3)

    elif x == 6:
        print('sutck_avoid_move():6')
        motor.move(100, -100, 5)
        motor.move(100, 100, 3)



def stuck_avoid():
    print('スタック回避開始')
    flag = False
    while 1:
        # 0~6
        for i in range(7):
            utc1, lat1, lon1, sHeight1, gHeight1 = GPS.GPSdeta_read()
            stuck.stuck_avoid_move(i)
            utc2, lat2, lon2, sHeight2, gHeight2 = GPS.GPSdeta_read()
            bool_stuck = stuck.stuck_jud(lat1, lon1, lat2, lon2, 1)
            if bool_stuck == True:
                if i == 1 or i == 4 or i == 5:
                    print('スタックもう一度引っかからないように避ける')
                    motor.move(-60, -60, 2)
                    motor.move(-60, 60, 0.5)
                    motor.move(80, 80, 3)
                flag = True
                break
        if flag:
            break
        # 3,2,1,0
        for i in range(7):
            utc1, lat1, lon1, sHeight1, gHeight1 = GPS.GPSdeta_read()
            stuck.stuck_avoid_move(7-i)
            utc2, lat2, lon2, sHeight2, gHeight2 = GPS.GPSdeta_read()
            bool_stuck = stuck.stuck_jud(lat1, lon1 ,lat2 , lon2,1)
            if bool_stuck == False:
                if i == 1 or i == 4 or i == 5:
                    print('スタックもう一度引っかからないように避ける')
                    motor.move(-60, -60, 2)
                    motor.move(-60, 60, 0.5)
                    motor.move(80, 80, 3)
                flag = True
                break
        if flag:
            break
    print('スタック回避完了')


if __name__ == '__main__':
    motor.setup()
    while 1:
        
        a = int(input('出力入力しろ'))
        b = float(input('時間入力しろ'))
        motor.move(a,a,b)
    
