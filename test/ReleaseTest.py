import sys  
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')
# sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')


import time
import serial
import pigpio
import BME280 #Environmental
# import GPS
import traceback


# anyalt = 2
# GAreleasecount = 0
# gpsreleasejudge = 0

anypress = 0.3
pressreleasecount = 0
pressreleasejudge = 0



def pressdetect(anypress):
	pressreleasecount = 0
	pressreleasejudge = 0
	try:
		pressdata = BME280.bme280_read()
		prevpress = pressdata[1]
		time.sleep(1)
		pressdata = BME280.bme280_read()
		latestpress = pressdata[1]
		#print(presscount)
		deltP = latestpress - prevpress
		if 0.0 in pressdata:
			print("BME280rror!")
			pressreleasejudge = 2
			pressreleasecount = 0
		elif deltP > anypress:
			pressreleasecount += 1
			if pressreleasecount > 2:
				pressreleasejudge = 1
				print("pressreleasejudge")
		else:
			pressreleasecount = 0
		#print(str(latestpress) + "	:	" + str(prevpress))
	except:
		print(traceback.format_exc())
		pressreleasecount = 0
		pressreleasejudge = 2
	return pressreleasecount, pressreleasejudge

def releasejudge(thd_p_release):



if __name__=="__main__":

	BME280.bme280_setup()
	BME280.bme280_calib_param()

	while True:
		pressreleasecount, pressreleasejudge = pressdetect(0.3)
		print(f'count:{pressreleasecount}\tjudge{pressreleasejudge})
		if pressreleasejudge == 1:
			print('Press')
		else:
			print('unfulfilled')

# def gpsdetect(anyalt):
#     global gpsdata
#     global GAreleasecount
#     gpsreleasejudge = 0
#     try:
#         gpsdata = GPS.readGPS()
#         Pregpsalt = gpsdata[3]
#         time.sleep(1)
#         gpsdata = GPS.readGPS()
#         Latestgpsalt = gpsdata[3]
#         daltGA = Latestgpsalt - Pregpsalt
#         #print(str(Latestgpsslt)+"   :   "+str(Pregpsalt))
#         if daltGA > anyalt:
#             GAreleasecount += 1
#             if GAreleasecount > 2:
#                 gpsreleasejudge = 1
#                 print("gpsreleasejudge")
#             else:
#                 gpsreleasejudge = 0
#     except:
#         print(traceback.format_exc())
#         GAreleasecount = 0
#         gpsreleasejudge = 2
#     return GAreleasecount, gpsreleasejudge

# if __name__=="__main__":
#
# 	BME280.bme280_setup()
# 	BME280.bme280_calib_param()
# 	GPS.openGPS()
#
# 	while True:
# 		_, gpsreleasejudge = gpsdetect(10)
# 		if gpsreleasejudge == 1:
# 			print('GPS')
# 		else:
# 			print('GPS unfulfilled')
#
# 		_, pressreleasejudge = pressdetect(0.3)
# 		if pressreleasecount == 1:
# 			print('Press')
# 		else:
# 			print('unfulfilled')
