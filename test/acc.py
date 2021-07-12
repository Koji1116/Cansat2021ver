from SensorModule.Motor.stuck import stuck_jud
from time import sleep
from gpiozero import Motor
import BMC050
import sys
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Communication')

if __name__ == '__main__':
    while 1:
        accdata = BMC050.acc_data()
        acc_x = accdata[0]
        acc_y = accdata[1]
        acc_z = accdata[2]
        acc = (acc_x**2 + acc_y**2 + acc_z**2)**0.5
