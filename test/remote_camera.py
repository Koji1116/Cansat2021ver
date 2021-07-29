import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')

import Xbee
import Capture
import Other


try:
    Xbee.on()
    while 1:
        received_str = Xbee.receive_str()

        # received_str = ''
        # while received_str == '':
        #     received_str = Xbee.receive_str()

        if received_str == 'a':
            path = Other.fileName('photostorage/remote_camera')
            Capture.Capture('path')

except KeyboardInterrupt:
    print('interruppted')
    Xbee.off()