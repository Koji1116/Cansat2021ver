import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Casnat2021ver/Detection')
import numpy as np
import BMC050
import acc
import time
from threading import Thread
import stuck



BMC.BMC050_setup()
while 1:
    za = []
    for i in range(3):
        accdata = acc.acc_dataRead()
        za.append(accdata[2])
        time.sleep(0.2)
    z = max(za)
    print(z)