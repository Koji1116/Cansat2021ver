import sys
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
from SensorModule.Motor.stuck import stuck_jud
from time import sleep
from gpiozero import Motor
import motor
import BMC050
import time
import GPS_Navigate
import GPS


def stuck(thd=1):
    BMC050.bmc050_setup()
    motor = Motor(Rpin1, Rpin2)
    while 1:
        motor.forward(0.2)
        sleep(0.3)
        accdata = BMC050.acc_data()
        acc_x = accdata[0]
        acc_y = accdata[1]
        acc_z = accdata[2]
        acc = (acc_x**2 + acc_y**2 + acc_z**2)**0.5
        if acc < thd:
            print('スタックした　：acc = '+str(acc))
            Xbee.str_trans('スタックした　：acc = '+str(acc))
            motor.stop()
            return False
            break
        else:
            print('まだしてない　:acc = '+str(acc))
            Xbee.str_trans('まだしてない　:acc = '+str(acc))
            motor.forward(0.2)
            sleep(2)
            return True


if __name__ == '__main__':
    
    
    motor.motor(0.8, 0.8, 0.2)
    if stuck_jud_test():
        motor.stop()
        print('fuck    acc_max ='+str(acc_max))
        break
    else:
        print('not stucked   +acc_max='+str(acc_max))
        time.sleep(5)
        motor.stop()
        time.sleep(2)
