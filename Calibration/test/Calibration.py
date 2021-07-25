import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
# sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection/Run_phase')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')


#--- must be installed module ---#
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
import numpy as np
#--- default module ---#
import math
import time
import traceback
from threading import Thread
#--- original module ---#
# import BMC050
import mag
import Xbee
# import pwm_control
import GPS
import GPS_Navigate

#import for log
import Other
import glob
from gpiozero import Motor
import motor
import datetime







GPS_data = [0.0,0.0,0.0,0.0,0.0]
RX = 18

# Calibration_rotate_controlLog = '/home/pi/log/Calibration_rotate_controlLog.txt'


def get_data():        
	"""
	MBC050からデータを得る
	"""
	try:
		magData = mag.mag_dataRead()
	except KeyboardInterrupt:
		print()
	except Exception as e:
		print()
		print(e)
	#--- get magnet sensor data ---#
	magx = magData[0]
	magy = magData[1]
	magz = magData[2]
	return magx, magy, magz

def get_data_offset(magx_off, magy_off, magz_off):
	"""
	MBC050からオフセットを考慮して磁気データをえる
	"""
	try:
		magData = mag.mag_dataRead()
	except KeyboardInterrupt:
		print()
	except Exception as e:
		print()
		print(e)
	#--- get magnet sensor data ---#
	magx = magData[0] - magx_off
	magy = magData[1] - magy_off
	magz = magData[2] - magz_off
	return magx, magy, magz
	
def magdata_matrix(l, r, t, n):
	"""
	キャリブレーション用の磁気値を得るための関数
	forループ内(run)を変える必要がある2021/07/04
	"""
	try:
		magx, magy, magz = get_data()
		magdata = np.array([[magx, magy, magz]])
		for _ in range(n):
			motor.move(l, r, t)
			magx, magy, magz = get_data()
			#--- multi dimention matrix ---#
			magdata = np.append(magdata , np.array([[magx,magy,magz]]) , axis = 0)
	except KeyboardInterrupt:
		print('Interrupt')
	except Exception as e:
		print(e.message())
	return magdata

def magdata_matrix_hand():
	"""
	キャリブレーション用の磁気値を手持ちで得るための関数
	"""
	try:
		magx, magy, magz = get_data()
		magdata = np.array([[magx, magy, magz]])
		for i in range():
			print('少し回転')
			time.sleep(1)
			print(f'{i+1}回目')
			magx, magy, magz = get_data()
			#--- multi dimention matrix ---#
			magdata = np.append(magdata, np.array([[magx, magy, magz]]), axis=0)
	except KeyboardInterrupt:
		print('Interrupt')
	except Exception as e:
		print(e.message())
	return magdata

def magdata_matrix_offset(l, r, t, n, magx_off, magy_off, magz_off):
	"""
	オフセットを考慮したデータセットを取得するための関数
	"""
	try:
		magx, magy, magz = get_data_offset(magx_off, magy_off, magz_off)
		magdata = np.array([[magx, magy, magz]])
		for _ in range(n):
			motor.move(l, r, t)
			magx, magy, magz = get_data_offset(magx_off, magy_off, magz_off)
			#--- multi dimention matrix ---#
			magdata = np.append(magdata, np.array([[magx, magy, magz]]), axis=0)
	except KeyboardInterrupt:
		print('Interrupt')
	except Exception as e:
		print(e.message())
	return magdata
	return magdata

def calculate_offset(magdata):
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
	magx_off = (magx_max + magx_min)/2
	magy_off = (magy_max + magy_min)/2
	magz_off = (magz_max + magz_min)/2
	return magx_array , magy_array , magz_array , magx_off , magy_off , magz_off


def angle(magx, magy, magx_off=0, magy_off=0):
    θ = math.degrees(math.atan((magy - magy_off) / (magx - magx_off)))

    if magx - magx_off > 0 and magy - magy_off > 0:  # First quadrant
        pass  # 0 <= θ <= 90
    elif magx - magx_off < 0 and magy - magy_off > 0:  # Second quadrant
        θ = 180 + θ  # 90 <= θ <= 180
    elif magx - magx_off < 0 and magy - magy_off < 0:  # Third quadrant
        θ = θ + 180  # 180 <= θ <= 270
    elif magx - magx_off > 0 and magy - magy_off < 0:  # Fourth quadrant
        θ = 360 + θ  # 270 <= θ <= 360

    θ += 90
    if 360 <= θ <= 450:
        θ -= 360
    return θ

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
	direction = GPS_Navigate.vincenty_inverse(lat1,lon1,lat2,lon2)
	return direction

def timer(t):
	global cond
	time.sleep(t)
	cond = False

if __name__ == "__main__":
	try:
		dateTime = datetime.datetime.now()
		path_log = f'Calibration-{dateTime.month}-{dateTime.day}-{dateTime.hour}:{dateTime.minute}:{dateTime.second}'
		# filecount = len(glob.glob1(path_log, '*' + '.txt'))
		r = float(input("右の出力は？\t"))
		l = float(input("左の出力は\t"))
		t = float(input("一回の回転時間は\t"))
		n = int(input('取得データ数は\t'))
		# number = int(input("取得するデータ数は？"))
		#--- setup ---#
		mag.bmc050_setup()
		t_start = time.time()
		#--- calibration ---#
		magdata_Old = magdata_matrix(l, r, t, n)
		#--- calculate offset ---#
		magx_array_Old, magy_array_Old, magz_array_Old, magx_off, magy_off, magz_off = calculate_offset(magdata_Old)
		time.sleep(0.1)
		#----Take magnetic data considering offset----#
		magdata_new = magdata_matrix_offset(r, l, t, n, magx_off, magy_off, magz_off)
		magx_array_new = magdata_new[:,0]
		magy_array_new = magdata_new[:,1]
		magz_array_new = magdata_new[:,2]

		for i in range(len(magx_array_new)):
			Other.saveLog(path_log, magx_array_Old[i], magy_array_Old[i], magx_array_new[i], magy_array_new[i])
		print("success")


	except KeyboardInterrupt:
		print("Interrupted")
	
	finally:
		print("End")