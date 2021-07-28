import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
import melt
import motor

def escape(t_melt):
    # melt.down(t_melt)
    motor.move(50, 50, 1)
    # for i in range(5):
    #     strength_l = i * 10
    #     strength_r = i * 10
    #     motor.move(strength_l, strength_r, 0.1)
    # for i in range(5):
    #     strength_l = 50 - i * 10
    #     strength_l = 50 - i * 10
    #     motor.move(strength_l, strength_r, 0.1)

if __name__ == '__main__':
    escape(t_melt=3)