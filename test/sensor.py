import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Illuminance')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
import melt
import BME280
import Xbee
import mag
import GPS
import TSL2572
#import acc 
import Xbee
from gpiozero import Motor
import time
import motor
from smbus import SMBus
import pigpio

pi = pigpio.pi()

meltPin  = 17

##### for only acc
ACC_ADDRESS = 0x19
ACC_REGISTER_ADDRESS = 0x02
i2c = SMBus(1)

def bmc050_setup():
    # --- BMC050Setup --- #
    # Initialize ACC
    try:
        print('0')
        i2c.write_byte_data(ACC_ADDRESS, 0x0F, 0x03)
        print('1')
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x10, 0x0F)
        print('2')
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x11, 0x00)
        print('3')
        time.sleep(0.1)
    except:
        time.sleep(0.1)
        print("BMC050 Setup Error")
        i2c.write_byte_data(ACC_ADDRESS, 0x0F, 0x03)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x10, 0x0F)
        time.sleep(0.1)
        i2c.write_byte_data(ACC_ADDRESS, 0x11, 0x00)
        time.sleep(0.1)

def acc_dataRead():
    # --- Read Acc Data --- #
    accData = [0, 0, 0, 0, 0, 0]
    value = [0.0, 0.0, 0.0]
    for i in range(6):
        try:
            accData[i] = i2c.read_byte_data(
                ACC_ADDRESS, ACC_REGISTER_ADDRESS+i)
        except:
            pass
            # print("error")

    for i in range(3):
        value[i] = (accData[2*i+1] * 16) + (int(accData[2*i] & 0xF0) / 16)
        value[i] = value[i] if value[i] < 2048 else value[i] - 4096
        value[i] = value[i] * 0.0098 * 1

    return value

GPS.openGPS()

print('---melt----')
try:
	melt.down()
except:
	pi.write(meltPin, 0)



print('---motor---')
motor.move(20,20,2)




print('---mag---')
try:
    mag.bmc050_setup()
    for _ in range(5):
        mag_data = mag.mag_dataRead()
        print(mag_data)
except:
    print('error:mag')
 
print('---acc---')
try:
    bmc050_setup()
    for _ in range(5):
        acc_data = acc_dataRead()
        print(acc_data)
except:
    print('error : acc')



print('---Environment---')
try:
    BME280.bme280_setup()
    BME280.bme280_calib_param()
    for _ in range(5):
        bme_data = BME280.bme280_read()
        print(bme_data)
except:
    print('error : env')



print('---Illuminance---')
try:
    for _ in range(5):
        ill_data = TSL2572.main()
        print(ill_data)
except:
    print('error : TSL2572')

print('---Xbee---')
try:
    Xbee.on()
    for i in range(10):
        Xbee.str_trans(str(i)+'  : reseive?')
except:
    print('error : Xbee')

print('---GPS---')
try:
    GPS.openGPS()
    data = GPS.GPSdata_read()
    print(data)
except:
    print('error : GPS')



