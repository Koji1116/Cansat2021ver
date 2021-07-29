import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')

import GPS
import Xbee


if __name__ == '__main__':
    try:
        GPS.openGPS()
        Xbee.on()
        while 1:
            _, lat, lon, _, _, = GPS.readGPS()
            print(f'lat: {lat} \t lon:{lon}')
            Xbee.str_trans(f'lat: {lat} \t lon:{lon}')
    except KeyboardInterrupt:
        print('Interrupted')
        Xbee.str_trans('Interrupted')
        GPS.closeGPS()
        Xbee.off()


