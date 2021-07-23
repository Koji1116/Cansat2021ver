import sys
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/Camera')
sys.path.append('/home/pi/git/kimuralab//SensorModuleTest/TSL2561')
sys.path.append('/home/pi/git/kimuralab/Detection/Run_phase')
sys.path.append('/home/pi/git/kimuralab/Detection/ParachuteDetection')
sys.path.append('/home/pi/git/kimuralab/Other')

#--- default module ---#
import time
import traceback
#--- must be installed module ---#
import numpy as np
import cv2
#--- original module ---#
#import GPS
#import gps_navigate
import Capture
import ParaDetection
import pwm_control
import TSL2561
import Other
import goaldetection
import motor
import GPS
import GPS_Navigate

def land_point_save():
	try:
		while True:
			value = GPS.readGPS()
			latitude_land = value[1]
			longitude_land = value[2]
			time.sleep(1)
			if latitude_land != -1.0 and longitude_land != 0.0 :
				break
	except KeyboardInterrupt:
		GPS.closeGPS()
		print("\r\nKeyboard Intruppted, Serial Closed")
	except:
		GPS.closeGPS()
		print (traceback.format_exc())
	return longitude_land,latitude_land

def Parachute_area_judge(longitude_land,latitude_land):
	try:
		while True:
			value = GPS.readGPS()
			latitude_new = value[1]
			longitude_new = value[2]
			print(value)
			print('longitude = '+str(longitude_new))
			print('latitude = '+str(latitude_new))
			time.sleep(1)
			if latitude_new != -1.0 and longitude_new != 0.0 :
				break
	except KeyboardInterrupt:
		GPS.closeGPS()
		print("\r\nKeyboard Intruppted, Serial Closed")

	except:
		GPS.closeGPS()
		print (traceback.format_exc())
	direction = GPS_Navigate.vincenty_inverse(longitude_land,latitude_land,longitude_new,latitude_new)
	distance = direction["distance"]        
	return distance


def Parachute_Avoidance(flug):
	#--- There is Parachute around rover ---#
	if flug == 1:
		#--- Avoid parachute by back control ---#
		try:
			goalflug, goalarea, goalGAP, photoname = goaldetection.GoalDetection("/home/pi/photo/photo", 200, 20, 80, 7000)
			if (goalGAP >= -160) and (goalGAP <= -80):
				motor.motor(0.5,-0.5,0.1)
				motor.motor(0.7,0.7,1)

			if (goalGAP >= -80) and (goalGAP <= 0):
				motor.motor(0.8,-0.8,0.1)
				motor.motor(0.7,0.7,1)

			if (goalGAP >= 0) and (goalGAP <= 80):
				motor.motor(-0.5,0.5,0.1)
				motor.motor(0.7,0.7,1)

			if (goalGAP >= 80) and (goalGAP <= 160):
				motor.motor(-0.8,0.8,0.1)
				motor.motor(0.7,0.7,1)
		
		except KeyboardInterrupt:
			print("stop")
			
	#--- There is not Parachute arround rover ---#
	if flug == 0:
		try:
			#--- rotate ---#
			# run = pwm_control.Run()
			# run.straight_h()
			# time.sleep(0.5)
			motor.motor(1, 1, 0.5)

		except KeyboardInterrupt:
			# run = pwm_control.Run()
			# run.stop()		モータ関数変わってるからなくていい？takayama
			# time.sleep(1)
			pass

		finally:
			# run = pwm_control.Run()
			# run.stop()		モータ関数変わってるからなくていい？takayama
			# time.sleep(1)
			pass
		#--- finish ---#

if __name__ == '__main__':
	print("START: Judge covered by Parachute")
	TSL2561.tsl2561_setup()
	t2 = time.time()
	t1 = t2
	#--- Paracute judge ---#
	#--- timeout is 60s ---#
	while t2 - t1 < 60:
		Luxflug = ParaDetection.ParaJudge(10000)
		print(Luxflug)
		if Luxflug[0] == 1:
			break
		t1 =time.time()
		time.sleep(1)
		print("rover is covered with parachute!")

	print("START: Parachute avoidance")

	try:
		#--- first parachute detection ---#
		a,b = land_point_save()
		length = Parachute_area_judge(a,b)
		while length < 3:
		    flug, area, photoname = ParaDetection.ParaDetection("/home/pi/photo/photo",320,240,200,10,120)
		    Parachute_Avoidance(flug)

	except KeyboardInterrupt:
		print("Emergency!")
		

	except:
		print(traceback.format_exc())
	print('finish')
