import sys
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/Camera')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/TSL2561')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/GPS')
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
import GPS
import gps_navigate
import Capture
import ParaDetection
import pwm_control
import TSL2561
import Other

ParaAvoidanceLog = '/home/pi/log/ParaAvoidanceLog.txt'

def land_point_save():
	try:
		while True:
			GPS_value = GPS.readGPS()
			latitude_land = GPS_value[1]
			longitude_land = GPS_value[2]
			#time.sleep(0.5)
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
			#print(value)
			#print('longitude = '+str(longitude_new))
			#print('latitude = '+str(latitude_new))
			time.sleep(1)
			if latitude_new != -1.0 and longitude_new != 0.0 :
				break
	except KeyboardInterrupt:
		GPS.closeGPS()
		print("\r\nKeyboard Intruppted, Serial Closed")

	except:
		GPS.closeGPS()
		print (traceback.format_exc())
	direction = gps_navigate.vincenty_inverse(latitude_land,longitude_land,latitude_new,longitude_new)
	distance = direction["distance"]        
	return distance

def Parachute_Avoidance(flug,t_start):
	#--- There is Parachute arround rover ---#
	if flug == 1:
		print('Parachute Avoidance : There is a Parachute')
		#--- Avoid parachute by back control ---#
		try:
			#--- run back ---#
			run = pwm_control.Run()
			run.back()
			time.sleep(0.5)

		except KeyboardInterrupt:
			run = pwm_control.Run()
			run.stop()
			time.sleep(1)

		finally:
			run = pwm_control.Run()
			run.stop()
			time.sleep(1)
			#print("back")

		#--- Avoid parachute by rotate control ---#
		while flug == 1 or flug == -1:
			try:
				#--- rotate ---#
				run = pwm_control.Run()
				run.turn_right_l()
				time.sleep(0.5)

			except KeyboardInterrupt:
				run = pwm_control.Run()
				run.stop()
				time.sleep(1)

			finally:
				run = pwm_control.Run()
				run.stop()
				time.sleep(1)
			#--- Parachute detect repeatedly and avoid it ---#
			flug, area, photoname = ParaDetection.ParaDetection("/home/pi/photo/photo",320,240,200,10,120)
			print("flug = "+str(flug))
			Other.saveLog(ParaAvoidanceLog, 'ParaAvoidance', time.time() - t_start, flug, area, photoname, GPS.readGPS())

	#--- There is not Parachute arround rover ---#
	if flug == 0:
		print('Parachute Avoidance : There is not a Parachute')
		try:
			#--- rotate ---#
			run = pwm_control.Run()
			run.straight_h()
			time.sleep(2)

		except KeyboardInterrupt:
			run = pwm_control.Run()
			run.stop()
			time.sleep(1)

		finally:
			run = pwm_control.Run()
			run.stop()
			time.sleep(1)
		#--- finish ---#

if __name__ == '__main__':
	GPS.openGPS()
	TSL2561.tsl2561_setup()
	t_start = time.time()
	print("START: Judge covered by Parachute")
	#--- note GPS data at land point ---#
	longitude_land,latitude_land = land_point_save()
	#--- initialize distance ---#
	global distance
	distance = 0
	t2 = time.time()
	t1 = t2
	#--- Parachute judge ---#
	#--- timeout is 60s ---#
	while t2 - t1 < 60:
		Luxflug = ParaDetection.ParaJudge(100)
		if Luxflug[0] == 1:
			break
		t1 =time.time()
		time.sleep(1)
		print("rover is covered with parachute!")
	print("START: Parachute avoidance")
	while distance <= 5:
		try:
			#--- first parachute detection ---#
			flug, area, photoname = ParaDetection.ParaDetection("/home/pi/photo/photo",320,240,200,10,120)
			Parachute_Avoidance(flug,t_start)
			distance = Parachute_area_judge(longitude_land,latitude_land)

		except KeyboardInterrupt:
			print("Emergency!")
			run = pwm_control.Run()
			run.stop()

		except:
			run = pwm_control.Run()
			run.stop()
			print(traceback.format_exc())
	print('finish')
