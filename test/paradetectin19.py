import sys
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/TSL2561')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/Camera')
import time
import cv2
import numpy as np
import Capture
import TSL2561


def ParaJudge(LuxThd):
	lux=TSL2561.readLux()
	#print("lux1: "+str(lux[0]))

	if lux[0] < LuxThd:
		time.sleep(1)
		return [0, lux[0]]

	else:
		return [1, lux[0]]


def ParaDetection(imgpath, H_min, H_max, S_thd):
	try:
		imgname = Capture.Capture(imgpath)
		img = cv2.imread(imgname)
		#make mask
        #RGBでは色合いの判定が難しい→HSV色空間というデータ構造を使う
        #https://qiita.com/odaman68000/items/ae28cf7bdaf4fa13a65b
		img_HSV = cv2.cvtColor(cv2.GaussianBlur(img,(15,15),0),cv2.COLOR_BGR2HSV_FULL)
        #ガウシアンフィルタ→ホワイトノイズに適する。注目が外の距離に応じて重みを変えることが出来る。
        #https://oliversi.com/2019/01/12/python-opencv-gaussianblur/
		h = img_HSV[:, :, 0]
		s = img_HSV[:, :, 1]
		mask = np.zeros(h.shape, dtype=np.uint8)
		mask[((h < H_max) | (h > H_min)) & (s > S_thd)] = 255
        #Hは色相(H<20|H>200)の範囲が赤色。紫っぽい範囲まで含めれば280～28
        #色相が赤でも色の濃さが薄ければ白や黒に近づく。よってS(彩度)も判定する必要あり。Sが大きければ大きいほど鮮やか。赤だとだいたいS＝128程度。

		#contour
		mask, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		#max area
		max_area = 0
		for j in range(0,len(contours)):
			area = cv2.contourArea(contours[j])
			if max_area < area:
				max_area = area
		#print('Max area is',max_area)

		#No Parachute 
		if max_area <= 100:
			#print( "There is not the Parachute" )
			return [0, max_area, imgname]

		#Prachute 
		else:
			#print( "There is the Parachute" )
			return [1, max_area, imgname]
	except:
		return[-1, 0, imgname]

if __name__ == "__main__":
	try:
		while 1:
			f, a, n = ParaDetection("/home/pi/photo/photo", 200, 10, 120)
			print("flug", f)
			print("area", a)
			print("name", n)
	except KeyboardInterrupt:
		print('KI')
	except:
		print('EO')