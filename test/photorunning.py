import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
import cv2
import numpy as np
import math
import Camera

def GoalDetection(imgpath, H_min=200, H_max=20, S_thd=80, G_thd=7000):
    """
    画像誘導用の関数
    引数
    imgpath:写真のパス、H_min:色相の最小値、H_max:色相の最大値、S_thd:彩度の閾値、G_thd、ゴール面積の閾値
    戻り値
    goalFlug:0はゴール検出、-1は未検出、1はゴールじゃない
    GAP:画像中心とゴールの中心の差(ピクセル)

    """

    try:
    	imgname = Capture.Capture(imgpath)
    	img = cv2.imread(imgname)
    	hig, wid, col = img.shape
    	i = 100

		#make mask
    	img_HSV = cv2.cvtColor(cv2.GaussianBlur(img,(15,15),0),cv2.COLOR_BGR2HSV_FULL)
    	h = img_HSV[:, :, 0]
    	s = img_HSV[:, :, 1]
    	mask = np.zeros(h.shape, dtype=np.uint8)
    	mask[((h < H_max) | (h > H_min)) & (s > S_thd)] = 255

		#contour
    	mask, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		#max area
    	max_area = 0
    	max_area_contour = -1

    	for j in range(0,len(contours)):
    		area = cv2.contourArea(contours[j])
    		if max_area < area:
    			max_area = area
    			max_area_contour = j

		#no goal
    	if max_area_contour == -1:
    		return [-1, 0, -1, imgname]

    	elif max_area <= 5:
    		return [-1, 0, -1, imgname]

		#goal
    	elif max_area >= G_thd:
    		return [0, max_area ,0, imgname]
    	else:
			#rectangle
    		cnt = contours[max_area_contour]
    		x,y,w,h = cv2.boundingRect(cnt)
    		GAP = x+w/2-160
    		return [1, max_area, GAP, imgname]
    except:
    	i = i + 1
    	return[i, -1, -1, imgname]

if __name__ == "__main__":
    try:
        path = '/home/pi/Desktop/Cansat2021ver/photostorage'
        while True:
            goalflug, goalarea, goalGAP, photoname = GoalDetection(path)
            print(f,'goalflug:{goalflug} goalarea:{goalarea} goalGAP:{goalGAP} photoname:{photoname}')
    except KeyboardInterrupt:
        print('stop')
    except:
        print('error')