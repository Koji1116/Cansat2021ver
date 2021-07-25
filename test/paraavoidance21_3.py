#着地判定後にキャリブレーション前にパラシュート回避を行う
#パラシュート回避エリアは設定せずに、パラシュートが検出されない場合が3回以上(下のプログラムのzで設定)
#のときパラシュート回避を行ったと判定
#そこでキャリブレーションを行い、ローバーをゴール方向に向かせる。
#そのあとにもう一度パラシュート回避を同じ判定方法で行ってGPS走行に移行する。


import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
#sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/TSL2561')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Illuminance')
#sys.path.append('/home/pi/git/kimuralab/Detection/Run_phase')
sys.path.append('/home/pi/Desktop/Cansat2021ver/test')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')

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
#import ParaDetection
#import TSL2561
import Other
#import goaldetection
import motor
import GPS
import GPS_Navigate
import paradetection21_2

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
	z = 0
	while z < 3:
		if flug == 1:
		#--- Avoid parachute by back control ---#
		    try:
			    goalflug, goalarea, goalGAP, photoname = goaldetection.GoalDetection("/home/pi/photo/photo", 200, 20, 80, 7000)
			    if (goalGAP >= -100) and (goalGAP <= -50):
				    motor.move(50,-50,0.1)
				    motor.move(70,70,1)

			    if (goalGAP >= -50) and (goalGAP <= 0):
				    motor.move(80,-80,1)
				    motor.move(70,70,1)

			    if (goalGAP >= 0) and (goalGAP <= 50):
				    motor.move(-50,50,0.1)
				    motor.move(70,70,1)

			    if (goalGAP >= 50) and (goalGAP <= 100):
				    motor.move(-80,80,1)
				    motor.move(70,70,1)
		
		    except KeyboardInterrupt:
			    print("stop")
		if flug == 0:
			motor.move(50, 50, 0.5)
			z = z + 1
		print(z)
			

if __name__ == '__main__':
	try:
		#print("START: Judge covered by Parachute")
		#TSL2561.tsl2561_setup()
		#t2 = time.time()
		#t1 = t2
		#--- Paracute judge ---#
		#--- timeout is 60s ---#
		#while t2 - t1 < 60:
			#Luxflug = ParaDetection.ParaJudge(10000)
			#print(Luxflug)
			#if Luxflug[0] == 1:
			#	break
			#t1 =time.time()
			#time.sleep(1)
			#print("rover is covered with parachute!")

		print("START: Parachute avoidance")

		flug, area, GAP, photoname = paradetection21_2.ParaDetection("photostorage/photostorage_paradete",320,240,200,10,120)
		Parachute_Avoidance(flug)
		print("success")

	except KeyboardInterrupt:
		print("emergency!")

	except:
		print(traceback.format_exc())
	print("finish!")