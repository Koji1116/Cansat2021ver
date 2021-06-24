import sys  
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/BME280')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/GPS')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/TSL2561')

import time
import serial
import pigpio
import BME280
import GPS
import TSL2561
import traceback

anylux = 0
anypress = 0.3
luxdata = []
bme280data = []
luxcount = 0
presscount = 0

luxreleasejudge = 0
pressreleasejudge = 0

# def luxdetect(anylux):
# 	global luxdata
# 	global luxcount
# 	luxreleasejudge = 0
# 	try:
# 		luxdata = TSL2561.readLux()
# 		#print(luxdata)
# 		#print(luxcount)
# 		if luxdata[0] > anylux or luxdata[1] > anylux:
# 			luxcount += 1
# 			if luxcount > 4:
# 				luxreleasejudge = 1
# 				print("luxreleasejudge")
# 			else:
# 				luxreleasejudge = 0
# 	except:
# 		print(traceback.format_exc())
# 		luxcount = 0
# 		luxreleasejudge = 2
# 	return luxreleasejudge, luxcount


def gpsdetect(anyalt):
    global gpsdata
    global GAcount
    gpsreleasejudge = 0
    try:
        gpsdata = GPS.readGPS()
        Prevgpsalt = gpsdata[3]
        time.sleep(1)
        gpsdata = GPS.readGPS()
        Latestgpsalt = gpsdata[3]
        daltGA = abs(Latestgpsalt - Prevgpsalt)
        #print(str(Latestgpsslt)+"   :   "+str(Prevgpsalt))
        if daltGA > anyalt:
            GAcount += 1
            if GAcount > 4:
                gpsreleasejudge = 1
                print("gpsreleasejudge")
            else:
                gpsreleasejudge = 0
    except:
        print(traceback.format_exc())
        GAcount = 0
        gpsreleasejudge = 2
    return GAcount, gpsreleasejudge


def pressdetect(anypress):
	global bme280data
	global presscount
	pressreleasejudge = 0
	try:
		pressdata = BME280.bme280_read()
		prevpress = pressdata[1]
		time.sleep(1)
		pressdata = BME280.bme280_read()
		latestpress = pressdata[1]
		#print(presscount)
		deltP = latestpress - prevpress
		if 0.0 in bme280data:
			print("BME280rror!")
			pressreleasejudge = 2
			presscount = 0
		elif deltP > anypress:
			presscount += 1
			if presscount > 4:
				pressreleasejudge = 1
				print("pressreleasejudge")
		else:
			presscount = 0
		#print(str(latestpress) + "	:	" + str(prevpress))
	except:
		print(traceback.format_exc())
		presscount = 0
		pressreleasejudge = 2
	return presscount, pressreleasejudge

if __name__=="__main__":

	# TSL2561.tsl2561_setup()
	# while 1:
	# 	luxdetect(200)
	# 	time.sleep(1)

	GPS.openGPS()
	while 1:
		gpsdetect(10)
		time.sleep(1)

	# BME280.bme280_setup()
	# BME280.bme280_calib_param()
	# while 1:
	# 	pressdetect(0.3)
	# 	time.sleep(1)
