# -*- coding:utf-8 -*-
import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Camera')

import cv2
import numpy as np
import time

import Capture



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


def GoalDetection(imgpath, G_thd=7000):
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
    max_area = 0
    max_area_contour = -1

    for j in range(0, len(contours)):
        area = cv2.contourArea(contours[j])
        if max_area < area:
            max_area = area
            max_area_contour = j

    max_area = max_area / (hig * wid) * 100

    # no goal
    if max_area_contour == -1:
        return [-1, 0, -1, imgname]
    elif max_area <= 1:
        return [-1, 0, -1, imgname]

    # goal
    elif max_area >= G_thd:
        centers = get_center(contours[max_area_contour])
        print(centers)
        GAP = (centers[0] - wid / 2) / (wid / 2) * 100
        print((centers[1] - hig / 2) / (hig / 2))
        return [0, max_area, GAP, imgname]
    else:
        # rectangle
        centers = get_center(max_area_contour)
        GAP = (centers[0] - wid / 2) / (wid / 2) * 100
        return [1, max_area, GAP, imgname]


if __name__ == '__main__':
    try:
        while 1:
            G_thd = float(input('ゴールの閾値を入力(初期値:5%):\t'))
            time.sleep(2)
            photoName = Capture.Capture('photostorage/information', 320, 240)
            goalflug, goalarea, gap, _ = GoalDetection(photoName, G_thd)
            print(f'goalflug:{goalflug}\tgoalarea:{goalarea}%\tgap:{gap}%')
            time.sleep(1)
    except KeyboardInterrupt:
        print('Interrupted')
    except Exception as e:
        print(f'message:{e.message}')
