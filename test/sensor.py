import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')

import BME280.py
import mag
import GPS
import TSL2572
import acc


print('---mag---')
mag.bmc050_setup()
mag_data = mag.mag_dataRead()
print(mag_data)

print('---acc---')
acc.bmc050_setup()
acc_data = acc.acc_dataRead()
print(acc_data)

print('---Environment---')
BME280.bme280_setup()
bme_data = BME280.bme280_read()
print(bme_data)

print('---Illuminance---')
ill_data = TSL2572.main()
print(ill_data)


print('---GPS---')
GPS.openGPS()
utc, lat, lon, sHeight, gHeight = GPS.readGPS()
if utc == -1.0:
    if lat == -1.0:
        print("Reading GPS Error")
        
    else:
        print("Status V")
else:
    print(utc, lat, lon, sHeight, gHeight)



