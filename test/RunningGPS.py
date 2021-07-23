import sys
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/BMX055')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/GPS')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/IM920')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/Motor')
sys.path.append('/home/pi/git/kimuralab/IntegratedProgram/Calibration')
sys.path.append('/home/pi/git/kimuralab/Other')

import math
import numpy as np
import time
import traceback
import pigpio
import serial
import os
import BMC050
import Calibration
import GPS
import Motor
import Other

fileCal = "" 						#file path for Calibration
ellipseScale = [0.0, 0.0, 0.0, 0.0] #Convert coefficient Ellipse to Circle
disGoal = 100.0						#Distance from Goal [m]
angGoal = 0.0						#Angle toword Goal [deg]
angOffset = -77.0					#Angle Offset towrd North [deg]
gLat, gLon = 35.918181, 139.907992	#Coordinates of That time
nLat, nLon = 0.0, 0.0		  		#Coordinates of That time
nAng = 0.0							#Direction of That time [deg]
relAng = [0.0, 0.0, 0.0]			#Relative Direction between Goal and Rober That time [deg]
rAng = 0.0
mP = 0								#Motor Power
kp = 0.7							#P Gain
gpsInterval = 0						#GPS Log Interval Time
maxMP = 60							#Maximum motor Power

gpsData = [0.0, -1.0, -1.0, 0.0, 0.0]						#variable to store GPS data
bmx055data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]	#variable to store BMX055data

runningLog = "log/runningLog.txt"
calibrationLog = "log/calibrationLog"

pi = pigpio.pi()	#object to set pigpio

def setup():
	pi.set_mode(22,pigpio.OUTPUT)
	pi.write(22,0)
	pi.write(17,0)
	time.sleep(1)
	BMC050.bmc050_setup()
	GPS.openGPS()

def close():
	GPS.closeGPS()
	Motor.motor_stop()

def checkGPSstatus(gpsData):
	if gpsData[1] != -1.0 and gpsData[2] != 0.0:
		return 1
	else:
		return 0

def calNAng(calibrationScale, angleOffset):
	bmc050Data = BMC050.bmc050_read()
	nowAng = Calibration.readDir(calibrationScale, bmc050Data) - angleOffset
	nowAng = nowAng if nowAng <= 180.0 else nowAng - 360.0
	nowAng = nowAng if nowAng >= -180.0 else nowAng + 360.0
	return nowAng

def calGoal(nowLat, nowLon, goalLat, goalLon, nowAng):
	#distanceGoal, angleGoal = GPS.Cal_RhoAng(nowLat, nowLon, goalLat, goalLon)
	distanceGoal, angleGoal = GPS.vincentyInverse(nowLat, nowLon, goalLat, goalLon)
	relativeAng = angleGoal - nowAng
	relativeAng = relativeAng if relativeAng <= 180 else relativeAng - 360
	relativeAng = relativeAng if relativeAng >= -180 else relativeAng + 360
	return [distanceGoal, angleGoal, relativeAng]

def runMotorSpeed(relativeAng, kP, motorPowerMax):
	"""
	#Set Left and Right Motor Power
	mPS = int(relativeAng * kP * (-0.6))
	mPLeft = int(motorPowerMax * (180-relativeAng)/180) + mPS
	mPRight = int(motorPowerMax * (180+relativeAng)/180) - mPS
	"""

	mPS = int(relativeAng * kP * (-1))
	mPLeft = motorPowerMax + mPS
	mPRight = motorPowerMax - mPS
	#mPLeft = mPLeft + mPS
	#mPRight = mPRight - mPS

	#Limited motor at motorPowerMax
	mPLeft = int(motorPowerMax if mPLeft > motorPowerMax else mPLeft)
	mPLeft = int(motorPowerMax / 2 if mPLeft < motorPowerMax / 2 else mPLeft)
	mPRight = int(motorPowerMax if mPRight > motorPowerMax else mPRight)
	mPRight = int(motorPowerMax / 2 if mPRight < motorPowerMax / 2 else mPRight)
	return [mPLeft, mPRight, mPS]

if __name__ == "__main__":
	try:
		setup()
		time.sleep(1)

		fileCal = Other.fileName(calibrationLog, "txt")

		Motor.motor(40, 0, 1)
		Calibration.readCalData(fileCal)
		Motor.motor(0, 0, 1)
		ellipseScale = Calibration.Calibration(fileCal)
		Other.saveLog(fileCal, ellipseScale)

		gpsInterval = 0

		#Get GPS data
		#print("Getting GPS Data")
		while not checkGPSstatus(gpsData):
			gpsData = GPS.readGPS()
			time.sleep(1)

		print("Running Start")
		while disGoal >= 5:
			if checkGPSstatus(gpsData):
				nLat = gpsData[1]
				nLon = gpsData[2]

			#Calculate angle
			nAng = calNAng(ellipseScale, angOffset)

			#Calculate disGoal and relAng
			relAng[2] = relAng[1]
			relAng[1] = relAng[0]
			disGoal, angGoal, relAng[0] = calGoal(nLat, nLon, gLat, gLon, nAng)
			rAng = np.median(relAng)

			#Calculate Motor Power
			mPL, mPR, mPS = runMotorSpeed(rAng, kp, maxMP)

			Motor.motor(mPL, mPR, 0.001, 1)

			#Save Log
			print(nLat, nLon, disGoal, angGoal, nAng, rAng, mPL, mPR, mPS)
			Other.saveLog(runningLog, time.time(), BMC050.bmx055_read(), nLat, nLon, disGoal, angGoal, nAng, rAng, mPL, mPR, mPS)
			gpsData = GPS.readGPS()
			time.sleep(0.1)

		Motor.motor(0, 0, 2)
		print("Switch to Goal Detection")
		close()
	except KeyboardInterrupt:
		close()
		print("Keyboard Interrupt")
	except:
		close()
		print(traceback.format_exc())
