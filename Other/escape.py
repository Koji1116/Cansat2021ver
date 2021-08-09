from Detection.stuck import ue_jug
import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
import melt
import motor
import stuck

def escape(t_melt=3):
    melt.down(t_melt)
    stuck.ue_jug()

if __name__ == '__main__':
    motor.setup()
    escape()