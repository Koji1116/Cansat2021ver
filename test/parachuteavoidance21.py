#着地判定後キャリブレーション前にパラシュート回避を行う
#パラシュート回避エリアは設定せずに、パラシュートが検出されない場合が3回以上(下のプログラムのzで設定)
#のときパラシュート回避を行ったと判定
#そこでキャリブレーションを行い、ローバーをゴール方向に向かせる。
#そのあとにもう一度パラシュート回避を同じ判定方法で行ってGPS走行に移行する。


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

def Parachute_Avoidance(flug):




	
	#--- There is Parachute around rover ---#
	z = 0
	while z < 3:
		if flug == 1:
		#--- Avoid parachute by back control ---#
		    try:
			    goalflug, goalarea, goalGAP, photoname = goaldetection.GoalDetection("/home/pi/photo/photo", 200, 20, 80, 7000)
			    if (goalGAP >= -160) and (goalGAP <= -80):
				    motor.motor_koji(0.5,-0.5,0.1)
				    motor.motor_koji(0.7,0.7,1)

			    if (goalGAP >= -80) and (goalGAP <= 0):
				    motor.motor_koji(0.8,-0.8,0.1)
				    motor.motor_koji(0.7,0.7,1)

			    if (goalGAP >= 0) and (goalGAP <= 80):
				    motor.motor_koji(-0.5,0.5,0.1)
				    motor.motor_koji(0.7,0.7,1)

			    if (goalGAP >= 80) and (goalGAP <= 160):
				    motor.motor_koji(-0.8,0.8,0.1)
				    motor.motor_koji(0.7,0.7,1)
		
		    except KeyboardInterrupt:
			    print("stop")
		if flug == 0:
			motor.motor_koji(1, 1, 0.5)
			z = z + 1
		print(z)
			

if __name__ == '__main__':
	try:
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

		flug, area, GAP, photoname = goaldetection.GoalDetection("/home/pi/photo/photo,320,240,200,10,120")
		Parachute_Avoidance(flug)
		

	except KeyboardInterrupt:
		print("emergency!")

	except:
		print(traceback.format_exc())
	print("finish!")