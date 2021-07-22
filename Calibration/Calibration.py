import sys
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/BMX055')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/GPS')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/Wireless')
sys.path.append('/home/pi/git/kimuralab/Detection/Run_phase')
sys.path.append('/home/pi/git/kimuralab/Other')

#--- must be installed module ---#
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
#--- default module ---#
import math
import time
import traceback
from threading import Thread
#--- original module ---#
import BMC050
import IM920
import Xbee
import pwm_control
import GPS
import gps_navigate
import Other

GPS_data = [0.0,0.0,0.0,0.0,0.0]
RX = 18

Calibration_rotate_controlLog = '/home/pi/log/Calibration_rotate_controlLog.txt'

def get_data():        
	"""
	MBC050からデータを得る
	"""
	try:
		bmcData = BMC050.bmc050_read()

	except KeyboardInterrupt:
		print()
	
	except Exception as e:
		print()
		print(e)
	
	#--- get acceralate sensor data ---#
	global accx,accy,accz
	accx = bmcData[0]
	accy = bmcData[1]
	accz = bmcData[2]

	#--- get magnet sensor data ---#
	global magx,magy,magz
	magx = bmcData[6]
	magy = bmcData[7]
	magz = bmcData[8]
	return magx , magy , magz , accx , accy , accz

def magdata_matrix():
	"""
	キャリブレーション用の磁気値を得るための関数
	forループ内(run)を変える必要がある2021/07/04
	"""
	try:
		get_data()
		#--- initialize GPS value ---#
		global magdata
		magdata = np.array([[magx,magy,magz]])
		#time.sleep(0.5)
		for i in range(60):
			run = pwm_control.Run()
			run.turn_right()
			get_data()
			#--- multi dimention matrix ---#
			magdata = np.append(magdata , np.array([[magx,magy,magz]]) , axis = 0)
			time.sleep(0.1)

	except KeyboardInterrupt:
		run = pwm_control.Run()
		run.stop()
		
	finally:
		run = pwm_control.Run()
		run.stop()
	
	return magdata

def calculate_offset(magdata):
	global magx_array , magy_array , magz_array
	#--- manage each element sepalately ---#
	magx_array = magdata[:,0] 
	magy_array = magdata[:,1]
	magz_array = magdata[:,2]

	#--- find maximam GPS value and minimam GPS value respectively ---#
	magx_max = magx_array[np.argmax(magx_array)]
	magy_max = magy_array[np.argmax(magy_array)]
	magz_max = magz_array[np.argmax(magz_array)]

	magx_min = magx_array[np.argmin(magx_array)]
	magy_min = magy_array[np.argmin(magy_array)]
	magz_min = magz_array[np.argmin(magz_array)]          
	
	#--- calucurate offset ---#
	global magx_off , magy_off , magz_off
	magx_off = (magx_max + magx_min)/2
	magy_off = (magy_max + magy_min)/2
	magz_off = (magz_max + magz_min)/2
	#print("magx_off = "+str(magx_off))
	#print("magy_off = "+str(magy_off))
	#print("magz_off = "+str(magz_off))
	return magx_array , magy_array , magz_array , magx_off , magy_off , magz_off

def plot_data_2D(magx_array,magy_array):
	plt.scatter(magx_array,magy_array,label ="Calibration")
	plt.legend()
	plt.show()

def plot_data_3D(magx_array,magy_array,magz_array):
	fig = plt.figure()
	ax = Axes3D(fig)
	#--- label name ---#
	ax.set_xlabel("X")
	ax.set_ylabel("Y")
	ax.set_zlabel("Z")
	ax.plot(magx_array , magy_array , magz_array , marker="o" , linestyle='None')
	plt.show()

def calculate_angle_2D(magx,magy,magx_off,magy_off):
	#--- recognize rover's direction ---#
	#--- North = 0 , θ = (direction of sensor) ---#
	#--- -90 <= θ <= 90 ---#
	global θ
	θ = math.degrees(math.atan((magy-magy_off)/(magx-magx_off)))
	if θ >= 0:
		if magx-magx_off < 0 and magy-magy_off < 0: #Third quadrant
			θ = θ + 180 #180 <= θ <= 270
		if magx-magx_off > 0 and magy-magy_off > 0: #First quadrant
			pass #0 <= θ <= 90
	else:
		if magx-magx_off < 0 and magy-magy_off > 0: #Second quadrant
			θ = 180 + θ #90 <= θ <= 180
		if magx-magx_off > 0 and magy-magy_off < 0: #Fourth quadrant
			θ = 360 + θ #270 <= θ <= 360
	
	#--- Half turn  ---#
	θ += 180
	if θ >= 360:
		θ -= 360
	#print('magx-magx_off = '+str(magx-magx_off))
	#print('magy-magy_off = '+str(magy-magy_off))
	print('calculate:θ = '+str(θ))
	#--- 0 <= θ <= 360 ---#
	return θ



def calculate_angle_3D(accx,accy,accz,magx,magy,magz,magx_off,magy_off,magz_off):
	#--- recognize rover's direction ---#
	#--- calculate roll angle ---#
	Φ = math.degrees(math.atan(accy/accx))
	#--- calculate pitch angle ---#
	ψ = math.degrees(math.atan((-accx)/(accy*math.sin(Φ) + accz*math.cos(Φ))))
	#-- North = 0 , θ = (direction of sensor) ---#
	global θ
	θ = math.degrees(math.atan((magz - magz_off)*math.sin(Φ) - (magy - magy_off)*math.cos(Φ))/((magx - magx_off)*math.cos(ψ) + (magy - magy_off)*math.sin(ψ)*math.sin(Φ) +(magz - magz_off)*math.sin(ψ)*math.cos(Φ)))
	if θ >= 0:
		if magx-magx_off < 0 and magy-magy_off < 0: #Third quadrant
			θ = θ + 180 #180 <= θ <= 270
	else:
		if magx-magx_off < 0 and magy-magy_off > 0: #Second quadrant
			θ = 180 + θ #90 <= θ <= 180
		if magx-magx_off > 0 and magy-magy_off < 0: #Fourth quadrant
			θ = 360 + θ #270 <= θ <= 360
	
	print('magx-magx_off = '+str(magx-magx_off))
	print('magy-magy_off = '+str(magy-magy_off))
	print('magz-magz_off = '+str(magz-magz_off))
	return θ

def calculate_direction(lon2,lat2):
	#--- read GPS data ---#
	try:
		while True:
			GPS_data = GPS.readGPS()
			lat1 = GPS_data[1]
			lon1 = GPS_data[2]
			if lat1 != -1.0 and lat1 != 0.0 :
				break
	except KeyboardInterrupt:
		GPS.closeGPS()
		print("\r\nKeyboard Intruppted, Serial Closed")
	except:
		GPS.closeGPS()
		print (traceback.format_exc())
	#--- calculate angle to goal ---#
	direction = gps_navigate.vincenty_inverse(lat1,lon1,lat2,lon2)
	return direction

def rotate_control(θ,lon2,lat2,t_start):
	direction = calculate_direction(lon2,lat2)
	azimuth = direction["azimuth1"]
	#--- 0 <= azimuth <= 360 ---#
	print('goal azimuth = '+str(azimuth))
	#print('θ = '+str(θ))

	try:
		t1 = time.time()
		while azimuth - 30 > θ  or θ > azimuth + 30:
			if 0 <= azimuth < 30:
				if azimuth - 30 + 360 <= θ <= 360:
					break
			if 330 <= azimuth <= 360:
				if 0 <= θ <= azimuth + 30 - 360:
					break
			#--- use Timer ---#
			global cond
			cond = True
			thread = Thread(target = timer,args=([1]))
			thread.start()
			while cond:
				run = pwm_control.Run()
				run.turn_right_l()
			get_data()
			θ = math.degrees(math.atan((magy-magy_off)/(magx-magx_off)))
			#--- -90 <= θ <= 90 ---#
			if θ >= 0:
				if magx-magx_off < 0 and magy-magy_off < 0: #Third quadrant
					θ = θ + 180 #180 <= θ <= 270
				if magx-magx_off > 0 and magy-magy_off > 0: #First quadrant
					pass #0 <= θ <= 90
			else:
				if magx-magx_off < 0 and magy-magy_off > 0: #Second quadrant
					θ = 180 + θ #90 <= θ <= 180
				if magx-magx_off > 0 and magy-magy_off < 0: #Fourth quadrant
					θ = 360 + θ #270 <= θ <= 360
			#--- Half turn  ---#
			θ += 180
			if θ >= 360:
				θ -= 360
			#--- 0 <= θ <= 360 ---#		
			print('θ = '+str(θ))
			Other.saveLog(Calibration_rotate_controlLog, 'Calibration_rotate_control', time.time() - t_start, θ, azimuth)
			run = pwm_control.Run()
			run.stop()
			time.sleep(0.5)
			if time.time() - t1 >= 60:
				#judge = False
				break
		judge = True
		print("rotate control finished")
		#print(θ)
			

	except KeyboardInterrupt:
		run = pwm_control.Run()
		run.stop()
		print("faulted to rotate control to goal direction")                
		
	finally:
		run = pwm_control.Run()
		run.stop()
	return judge

def timer(t):
	global cond
	time.sleep(t)
	cond = False

if __name__ == "__main__":
	try:
		#--- difine goal latitude and longitude ---#
		lon2 = 139.5430
		lat2 = 35.553
		#--- setup ---#
		BMC050.bmc050_setup()
		GPS.openGPS()
		t_start = time.time()
		#--- calibration ---#
		while True:
			#--- calculate offset ---#
			magdata_matrix()
			calculate_offset(magdata)
			time.sleep(0.1)
			#--- plot data ---#
			plot_data_2D(magx_array,magy_array)
			#plot_data_3D(magx_array,magy_array,magz_array)
			
			#--- calculate θ ---#
			get_data()
			calculate_angle_2D(magx,magy,magx_off,magy_off)
			#calculate_angle_3D(accx,accy,accz,magx,magy,magz,magx_off,magy_off,magz_off)

			#--- rotate contorol ---#
			judge = rotate_control(θ,lon2,lat2,t_start)
			if judge == False:
				try:
					run = pwm_control.Run()
					run.straight_h()
					time.sleep(1)
				finally:
					run = pwm_control.Run()
					run.stop()
					time.sleep(1)					
			else:
				run = pwm_control.Run()
				run.straight_h()
				time.sleep(1)
				break
	
	except KeyboardInterrupt:
		print("ERROR")
	
	finally:
		print("End")
		run = pwm_control.Run()
		run.stop()

#---8/16 17:00 に成功したときのキャリブレーションプログラム---#
