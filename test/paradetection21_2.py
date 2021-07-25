import sys
sys.path.append('')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Illuminance')
import time
import cv2
import numpy as np
import Capture
import TSL2572

def ParaJudge(LuxThd):
	'''
	パラシュート被っているかを照度センサを用いて判定する関数
	引数は照度の閾値
	'''
	lux = TSL2572.readLux()
	#print("lux1: "+str(lux[0]))

	#--- rover is covered with parachute ---#
	if lux[0] < LuxThd:  #LuxThd: 照度センサの閾値
		time.sleep(1)
		return [0, lux[0]]

	#--- rover is not covered with parachute ---#
	else:
		return [1, lux[0]] 


def get_center(contour):
    """
    輪郭の中心を取得する。
    """
    # 輪郭のモーメントを計算する。
    M = cv2.moments(contour)
    # モーメントから重心を計算する。
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
    else:
        # set values as what you need in the situation
        cx, cy = 0, 0

    return cx, cy
    


def ParaDetection(imgpath, width, height, H_min, H_max, S_thd):
	
	try:
		imgname = Capture.Capture(imgpath,width,height)
		img = cv2.imread(imgname)
		hig, wid, _ = img.shape

		img_HSV = cv2.cvtColor(cv2.GaussianBlur(img,(15,15),0),cv2.COLOR_BGR2HSV_FULL)
		h = img_HSV[:, :, 0]
		s = img_HSV[:, :, 1]
		mask = np.zeros(h.shape, dtype=np.uint8)
		mask[((h < H_max) | (h > H_min)) & (s > S_thd)] = 255

		contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


		max_area = 0
		max_area_contour = -1

		for j in range(0,len(contours)):
			area = cv2.contourArea(contours[j])
			if max_area < area:
				max_area = area
				max_area_contour = j

		max_area /= hig * wid
		max_area *= 100

		centers = get_center(contours[max_area_contour])

		if max_area_contour == -1:
			return [-1, 0, -1, imgname]
#		elif max_area >= G_thd:
			GAP = (centers[0] - wid / 2) / (wid / 2) * 100
			return [0, max_area, GAP, imgname]
		else:
			GAP = (centers[0] - wid / 2) / (wid / 2) * 100
			return [1, max_area, GAP, imgname]
	except:
		return[100, 100, 100, imgname]

if __name__ == "__main__":
	
	TSL2572.tsl2572_setup()
	#--- lux data test ---#
	try:
		while 1:
			ParaJudge(10000)
			time.sleep(1)

	except KeyboardInterrupt:
		print('Stop lux data test')

	#--- Parachute detection test ---#
	try:
		while 1:
			flug = -1
			while flug == -1:
				f, a, n = ParaDetection("/home/pi/photo/photo",320,240,200,10,120)
				print(f'flug:{f}	area:{a}	name:{n}')
			print('ParaDetected')
			print(f'flug:{f}	area:{a}	name:{n}')
			# print("flug", f)
			# print("area", a)
			# print("name", n)
	except KeyboardInterrupt:
		print('Stop')
	except:
		print('End:Parachute_Detection')
