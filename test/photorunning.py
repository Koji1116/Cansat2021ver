import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
import cv2
import numpy as np
import time
import Capture
import Xbee
import motor
import Other
import datetime
from gpiozero import Motor
import time

import sys


#写真内の赤色面積で進時間を決める用　調整必要
area_short = 0
area_middle = 0
area_long = 0


sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Communication')



def motor_move(strength_r, strength_l, t_wait):
	# ピン番号は仮
	Rpin1 = 6
	Rpin2 = 5
	Lpin1 = 10
	Lpin2 = 9
	# 前進
	if strength_r >= 0 and strength_l >= 0:
		motor_r = Motor(Rpin1, Rpin2)
		motor_l = Motor(Lpin1, Lpin2)

		motor_r.forward(strength_r)
		motor_l.forward(strength_l)
		time.sleep(t_wait)
	# 後進
	elif strength_r < 0 and strength_l < 0:
		motor_r = Motor(Rpin1, Rpin2)
		motor_l = Motor(Lpin1, Lpin2)

		motor_r.backward(abs(strength_r))
		motor_l.backward(abs(strength_l))
		time.sleep(t_wait)
	# 右回転
	elif strength_r >= 0 and strength_l < 0:
		motor_r = Motor(Rpin1, Rpin2)
		motor_l = Motor(Lpin1, Lpin2)

		motor_r.forkward(abs(strength_r))
		motor_l.backward(abs(strength_l))
		time.sleep(t_wait)
	# 左回転
	elif strength_r < 0 and strength_l >= 0:
		motor_r = Motor(Rpin1, Rpin2)
		motor_l = Motor(Lpin1, Lpin2)
		motor_r.backward(abs(strength_r))
		motor_l.forkward(abs(strength_l))
		time.sleep(t_wait)


def motor_stop(x=1):
	'''motor_move()とセットで使用'''
	Rpin1 = 5
	Rpin2 = 6
	Lpin1 = 9
	Lpin2 = 10
	motor_r = Motor(Rpin1, Rpin2)
	motor_l = Motor(Lpin1, Lpin2)
	motor_r.stop()
	motor_l.stop()
	time.sleep(x)

# 赤色の検出
def detect_red_color(img):
	# HSV色空間に変換
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

	# 赤色のHSVの値域1
	hsv_min = np.array([0, 200, 50])
	hsv_max = np.array([30, 255, 255])
	mask1 = cv2.inRange(hsv, hsv_min, hsv_max)

	# 赤色のHSVの値域2
	hsv_min = np.array([150, 200, 50])
	hsv_max = np.array([179, 255, 255])
	mask2 = cv2.inRange(hsv, hsv_min, hsv_max)

	# 赤色領域のマスク（255：赤色、0：赤色以外）
	mask = cv2.bitwise_or(mask1, mask2)

	# マスキング処理
	masked_img = cv2.bitwise_and(img, img, mask=mask)

	return mask, masked_img


def get_center(contour):
	"""
    輪郭の中心を取得する。
    """
	# 輪郭のモーメントを計算する。
	M = cv2.moments(contour)
	# モーメントから重心を計算する。
	cx = M["m10"] / M["m00"]
	cy = M["m01"] / M["m00"]

	return cx, cy


def GoalDetection(imgpath, H_min=200, H_max=20, S_thd=80, G_thd=7000):
	'''
    引数
    imgpath：画像のpath
    H_min: 色相の最小値
    H_max: 色相の最大値
    S_thd: 彩度の閾値
    G_thd: ゴール面積の閾値

    戻り値：[goalglug, GAP, imgname]
    goalFlug    0: goal,   -1: not detect,   1: nogoal
    GAP: 画像の中心とゴールの中心の差（ピクセル）
    imgname: 処理した画像の名前
    '''
	global i

	img = cv2.imread(imgpath)
	imgname = imgpath
	hig, wid, col = img.shape
	print(img.shape)
	i = 100

	mask, _ = detect_red_color(img)

	# contour
	contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	img_contour = cv2.drawContours(img, contours, 6, (0, 255, 0), 5)
	cv2.imshow("img_edge", img_contour)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	# max area
	max_area = 0
	max_area_contour = -1

	for j in range(0, len(contours)):
		area = cv2.contourArea(contours[j])
		if max_area < area:
			max_area = area
			max_area_contour = j

	# no goal
	if max_area_contour == -1:
		return [-1, 0, -1, imgname]
	elif max_area <= 5:
		return [-1, 0, -1, imgname]

	# goal
	elif max_area >= G_thd:
		centers = get_center(contours[max_area_contour])
		print(centers)
		GAP = (centers[0] - wid / 2) / (wid / 2)
		print((centers[1] - hig / 2) / (hig / 2))
		return [0, max_area, GAP, imgname]
	else:
		# rectangle
		centers = get_center(max_area_contour)
		GAP = centers[0] - wid / 2
		return [1, max_area, GAP, imgname]

if __name__ == "__main__":
	try:
		path = '/home/pi/Desktop/Cansat2021ver/photostorage'
		goalflug = 1
		startTime = time.time()
		dateTime = datetime.datetime.now()
		path = f'ImageGuidance_{dateTime.month}-{dateTime.day}-{dateTime.hour}:{dateTime.minute}'
		while goalflug != 0:
			goalflug, goalarea, goalGAP, _ = GoalDetection(path)
			print(f'goalflug:{goalflug} goalarea:{goalarea}% goalGAP:{goalGAP}%')
			# Xbee.str_trans('goalflug', goalflug, ' goalarea', goalarea, ' goalGAP', goalGAP)
			Other.saveLog(path,startTime - time.time(), goalflug, goalarea, goalGAP)
			if goalarea <= 5:
				if goalGAP <= -30:
					print('Turn left')
					# Xbee.str_trans('Turn left')
					motor.motor(-0.2, 0.2, 0.2)
				# --- if the pixcel error is 30 or more, rotate right --- #
				elif 30 <= goalGAP:
					print('Turn right')
					# Xbee.str_trans('Turn right')
					motor.motor(0.2, -0.2, 0.2)
				# --- if the pixcel error is greater than -30 and less than 30, go straight --- #
				else:
					print('Go straight')
					if goalarea <= area_short:
						motor.motor(1, 1, 10)
					elif goalarea <= area_middle:
						motor.motor(1, 1, 5)
					elif goalarea <= area_long:
						motor.motor(1, 1, 2)

			time.sleep(1.0)

	except KeyboardInterrupt:
		print('stop')
	except:
		print('error')