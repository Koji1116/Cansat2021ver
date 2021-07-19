
import stuck
import motor
import Capture
import math
import numpy as np
import cv2
import sys
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/Camera')
sys.path.append('/home/pi/git/kimuralab/SensorModuleTest/Motor')
i = 100


def curvingSwitch(GAP, add):
    if abs(GAP) > 144:
        return add
    elif abs(GAP) > 128:
        return add*0.9
    elif abs(GAP) > 112:
        return add*0.8
    elif abs(GAP) > 96:
        return add*0.7
    elif abs(GAP) > 80:
        return add*0.6
    elif abs(GAP) > 64:
        return add*0.5
    elif abs(GAP) > 48:
        return add*0.4
    elif abs(GAP) > 32:
        return add*0.3
    elif abs(GAP) > 16:
        return add*0.2
    elif abs(GAP) >= 0:
        return 0


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
    try:
        imgname = Capture.Capture(imgpath)
        img = cv2.imread(imgname)
        hig, wid, col = img.shape
        i = 100

        # make mask
        img_HSV = cv2.cvtColor(cv2.GaussianBlur(
            img, (15, 15), 0), cv2.COLOR_BGR2HSV_FULL)
        h = img_HSV[:, :, 0]
        s = img_HSV[:, :, 1]
        mask = np.zeros(h.shape, dtype=np.uint8)
        mask[((h < H_max) | (h > H_min)) & (s > S_thd)] = 255

        # contour
        contours, hierarchy = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # max area
        max_area = 0
        max_area_contour = -1

        for j in range(0, len(contours)):
            area = cv2.contourArea(contours[j])
            if max_area < area:
                max_area = area
                max_area_contour = j

            # no goal

            elif max_area <= 5:
                return [-1, 0, -1, imgname]

            # goal
            elif max_area >= G_thd:
                return [0, max_area, 0, imgname]
            else:
                # rectangle
                cnt = contours[max_area_contour]
                x, y, w, h = cv2.boundingRect(cnt)
                GAP = x+w/2-160
                return [1, max_area, GAP, imgname]
    except:
        i = i + 1
        return[i, -1, -1, imgname]


def goal_duj():
    '''
    ゴール判定関数
    True;ゴール
    False:まだゴールじゃない
    '''
    if GoalDetection()[0] == 0:
        motor.motor(0.5, 0.5, 0.2)
        if stuck.stuck():
            return True
        else:
            return False
    else:
        return False


if __name__ == "__main__":
    try:
        while 1:
            goalflug, goalarea, goalGAP, photoname = GoalDetection(
                "/home/pi/photo/photo", 200, 20, 80, 7000)
            print("goalflug", goalflug, "goalarea", goalarea,
                  "goalGAP", goalGAP, "name", photoname)
    except KeyboardInterrupt:
        print('stop')
    except:
        print('error')
