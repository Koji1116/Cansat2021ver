import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
from time import sleep
import acc
import time


if __name__ == '__main__':
    acc.bmc050_setup()

    s = input('a だったら確認テスト')
    
    while 1:
        if s =='a':
            accdata = acc.acc_dataRead()
            z = accdata[2]
            if z <8:
                print('逆になってる')
            else:
                print('通常')
        else:
            accdata = acc.acc_dataRead()
            # x = accdata[0]
            # y = accdata[1]
            z = accdata[2]
            print(z)
        time.sleep(1)
