# -*- coding: utf-8 -*-
import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/GPS')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Melting')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Environmental')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection/ParaDetection')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection/Release')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Detection/Land')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/test')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')

import time
import datetime
import difflib
import pigpio
import serial
import binascii
import Xbee
import GPS
import BMC050
import BME280
import Capture
import TSL2561
import Release
import Land
import GPS
import Melting
import Motor
import TSL2561
import ParaDetection
import ParaAvoidance
import Other
import panoramaShootingtest #名称変更の可能性あり
import Calibration

phaseChk = 0	#variable for phase Check
# bme280str = ["temp", "pres", "hum", "alt"]												#variable to show bme280 returned variables
# bmc050str = ["accx", "accy", "accz", "dirx", "diry", "dirz"]	#variable to show bmc050 returned variables
# gpsstr = ["utctime", "lat", "lon", "sHeight", "gHeight"]								#variable to show GPS returned variables

gpsData = [0.0, 0.0, 0.0, 0.0, 0.0]
bme280Data = [0.0, 0.0, 0.0, 0.0]
bmx055data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

t_setup = 60	#variable to set waiting time after setup
t = 1			#Unknown Variable
x = 300			#time for release(loopx)
y = 180			#time for land(loopy)

t_start = 0.0	#time when program started


#variable used for releasejudge
releasepress = 0.3
pressreleasecount = 0
pressreleasejudge = 0

releasealt = 2
GArepeasecount = 0
gpsreleasejudge = 0

pi = pigpio.pi()

#variable used for landjudgment
presslandjudge = 0
gpslandjudge = 0
acclandjudge = 0
Landjudgment = [presslandjudge, gpslandjudge, acclandjudge]

#variable used for ParaDetection
LuxThd = 100
imgpath = "/home/pi/photo/photo"
width = 320
height = 240
H_min = 200
H_max = 10
S_thd = 120



paraExsist = 0 	#variable used for Para Detection

phaseLog = "/home/pi/log/phaseLog.txt"
waitingLog = "/home/pi/log/waitingLog.txt"
releaseLog = "/home/pi/log/releaseLog.txt"
landingLog = "/home/pi/log/landingLog.txt"
meltingLog = "/home/pi/log/meltingLog.txt"
paraAvoidanceLog = "/home/pi/log/paraAvoidanceLog.txt"
panoramapath = '/home/pi/Desktop/Cansat2021ver/photosotorage/panorama'

def setup():
	global phaseChk

	pi.set_mode(22,pigpio.OUTPUT)
#	pi.write(22,1)	#Xbee Turn On  要議論
	pi.write(17,0)	#outcasing
	time.sleep(1)
	BME280.bme280_setup()
	BME280.bme280_calib_param()
	BMC050.bmc050_setup()
	GPS.openGPS()

	# with open(phaseLog, 'a') as f:
	# 	pass

	phaseChk = int(Other.phaseCheck(phaseLog))
	print(phaseChk)

def close():
	GPS.closeGPS()
	pi.write(22, 0)
	pi.write(17,0)
	Motor.motor(0, 0, 1)
	Motor.motor_stop()

if __name__ == "__main__":
	try:
		t_start = time.time()
		# ------------------- Setup Phase --------------------- #
		print("Program Start  {0}".format(time.time()))
		Xbee.str_trans('Program Start {0}'.format(time.time()))
		Xbee.str_trans('Program Start {0}'.format(datetime.datetime.now()))
		setup()
		print(phaseChk)
		Xbee.str_trans(phaseChk)

		# ------------------- Waiting Phase --------------------- #
		Other.saveLog(phaseLog, "2", "Waiting Phase Started", time.time() - t_start)
		if phaseChk <= 2:
			t_wait_start = time.time()
			while time.time() - t_wait_start <= t_setup:
				Other.saveLog(waitingLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read(), TSL2561.readLux(), BMC050.bmc050_read())
				print("Waiting")
				Xbee.str_trans("Sleep")
				time.sleep(1)
			Xbee.str_trans("Waiting Finished")
#			pi.write(22, 0)		#Xbee Turn Off (ACTSは任意だから今のところなし)

		# ------------------- Release Phase ------------------- #
		Other.saveLog(phaseLog, "3", "Release Phase Started", time.time() - t_start)
		if phaseChk <= 3:
			tx1 = time.time()
			tx2 = tx1
			print("Releasing Judgement Program Start  {0}".format(time.time() - t_start))
			#loopx
			bme280Data = BME280.bme280_read()
			while tx2 - tx1 <= x:
				_, gpsreleasejudge = Release.gpsdetect(releasealt)
				_, pressreleasejudge = Release.pressdetect(releasepress)

				if gpsreleasejudge == 1 or pressreleasejudge == 1:
					break
				else:
					print("Release not yet")
				Other.saveLog(releaseLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read(), BMC050.bmc050_read())
				time.sleep(0.5)

				# Other.saveLog(releaseLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read(), BMC050.bmc050_read())
				# time.sleep(0.5)
				tx2 = time.time()

			else:
				print("RELEASE TIMEOUT")
			print("THE ROVER HAS RELEASED")

			#通信機onにかかわる部分　ACTSは任意だから
#			pi.write(22,1)
#			time.sleep(2)
			Xbee.str_trans("RELEASE")

		# ------------------- Landing Phase ------------------- #
		Other.saveLog(phaseLog, "4", "Landing Phase Started", time.time() - t_start)
		if phaseChk <= 4:
			print("Landing Judgement Program Start  {0}".format(time.time() - t_start))
			ty1 = time.time()
			ty2 = ty1
			#loopy
			gpsData = GPS.readGPS()
			bme280Data = BME280.bme280_read()
			while ty2 - ty1 <= y:
				Xbee.str_trans("loopY")

				# Initialize conditions
				presslandjudge = 0
				gpslandjudge = 0
				acclandjudge = 0

				# Judgment
				presslandjudge = Land.Pressdetect()
				gpslandjudge = Land.gpsdetect()
				acclanddetect = Land.accdetect()
				Landjudgment = [presslandjudge, gpslandjudge, acclandjudge]

				if Landjudgment.count(1) >= 2:
					print("THE ROVER HAS LANDED")
					break
				else:
					print("LAND NOT YET")

				gpsData = GPS.readGPS()
				bme280Data = BME280.bme280_read()
				bmc050data = BMC050.bmc050_read()

				Other.saveLog(landingLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read(), BMC050.bmc050_read())
				time.sleep(1)
				Other.saveLog(landingLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read(), BMC050.bmc050_read())
				time.sleep(1)
				Other.saveLog(landingLog, time.time() - t_start, GPS.readGPS(), BME280.bme280_read(), BMC050.bmc050_read())
				time.sleep(1)
				ty2 = time.time()
			else:
				print("LAND TIMEOUT")
			print("THE ROVER HAS LANDED")
			pi.write(22,1)
			Xbee.str_trans("LAND")

		# ------------------- Melting Phase ------------------- #
		Xbee.str_trans("Melt")
		Other.saveLog(phaseLog,"5", "Melting Phase Started", time.time() - t_start)
		if(phaseChk <= 5):
			print("Melting Phase Started")
			Other.saveLog(meltingLog, time.time() - t_start, GPS.readGPS(), "Melting Start")
			Melting.Melting()
			Other.saveLog(meltingLog, time.time() - t_start, GPS.readGPS(), "Melting Finished")

		# ------------------- ParaAvoidance Phase ------------------- #
		"""
		パラシュート回避行動を追加したい。
		"""
		Xbee.str_trans("ParaAvo")
		Other.saveLog(phaseLog, "6", "ParaAvoidance Phase Started", time.time() - t_start)
		if(phaseChk <= 6):
			Xbee.str_trans('P7S')
			Other.saveLog(phaseLog, '7', 'Parachute Avoidance Phase Started', time.time() - t_start)
			t_ParaAvoidance_start = time.time()
			print('Parachute Avoidance Phase Started {0}'.format(time.time() - t_start))

			# print("ParaAvoidance Phase Started")
			# Other.saveLog(paraAvoidanceLog, time.time() - t_start, GPS.readGPS(), "ParaAvoidance Start")
			# print("START: Judge covered by Parachute")
			# ParaAvoidance.ParaJudge()
			# print("START: Parachute avoidance")
			# paraExsist = ParaAvoidance.ParaAvoidance()
			# Other.saveLog(paraAvoidanceLog, time.time() - t_start, GPS.readGPS(), paraExsist)
			# Other.saveLog(paraAvoidanceLog, time.time() - t_start, GPS.readGPS(), "ParaAvoidance Finished")


		# ------------------- Panorama Shooting Phase ------------------- #
		Xbee.str_trans('Panorama')
		Other.saveLog(phaseLog, '7', 'Panorama Shooting phase', time.time() - t_start)
		if phaseChk <= 7:
			t_PanoramaShooting_start = time.time()
			print('Panorama Shooting Phase Started {0}'.format(time.time() - t_start))
			magdata = Calibration.magdata_matrix()
			magx_off, magy_off = Calibration.calculate_offset(magdata)
			panoramaShootingtest.shooting(magx_off, magy_off, panoramapath)
			Other.panorama(srcdir=panoramapath)


		Xbee.str_trans("Progam Finished")
		close()
	except KeyboardInterrupt:
		close()
		print("Keyboard Interrupt")
	except Exception as e:
		Xbee.str_trans("error")
		close()
		Other.saveLog("/home/pi/log/errorLog.txt", time.time() - t_start, "Error")
		print(e.message)
