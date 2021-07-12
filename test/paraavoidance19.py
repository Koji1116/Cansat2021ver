import sys
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/Camera')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/Motor')
sys.path.append('/home/pi/git/kimuralab/Detection/ParachuteDetection')
sys.path.append('/home/pi/git/kimuralab/Other')
import time
import cv2
import numpy as np
import Capture
import ParaDetection
import Motor
import Other

if __name__ == '__main__':
	print("START: Judge covered by Parachute")
	t2 = time.time()
	t1 = t2
	while t2 - t1 < 60:
		Luxflug = ParaJudge(100)
		if Luxflug[0] == 1:
			break
		t1 =time.time()
	print("START: Parachute avoidance")
	try:
		for i in range(2):
			Motor.motor(30, 30, 0.5)
			Motor.motor(0, 0, 0.2)
			flug, area, photoname = ParaDetection.ParaDetection(photo)

			if flug == 1:
				Motor.motor(-60, -60, 5)
				Motor.motor(0, 0, 2)

			if flug == 0:
				Motor.motor(60, 60, 5)
				Motor.motor(0 ,0, 2)

	except KeyboardInterrupt:
		print("Emergency!")
		Motor.motor_stop()

	except:
		Motor.motor_stop()
		print(traceback.format_exc())
