import sys
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Motor')
from time import sleep

import motor

while 1:
    print('入力しろ')
    a =input()
    if a =='a':
        motor.motor(0.5,0.8,2)
    elif a =='w':
        motor.motor(0.8,0.8,2)
    elif a =='d':
        motor.motor(0.5,0.8,2)
    elif a =='s':
        motor.motor(-0.5,-0.5,2)
    else:
        pass

    
