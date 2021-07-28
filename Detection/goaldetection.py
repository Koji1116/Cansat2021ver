# -*- coding:utf-8 -*-
import cv2
import numpy as np


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


def GoalDetection(imgpath, H_min, H_max, S_thd, G_thd):
    try:
        imgname = imgpath
        img = cv2.imread(imgname)
        hig, wid, _ = img.shape

        img_HSV = cv2.cvtColor(cv2.GaussianBlur(img, (15, 15), 0), cv2.COLOR_BGR2HSV_FULL)
        h = img_HSV[:, :, 0]
        s = img_HSV[:, :, 1]
        mask = np.zeros(h.shape, dtype=np.uint8)
        mask[((h < H_max) | (h > H_min)) & (s > S_thd)] = 255
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        max_area_contour = -1

        for j in range(0, len(contours)):
            area = cv2.contourArea(contours[j])
            if max_area < area:
                max_area = area
                max_area_contour = j

        max_area /= hig * wid
        max_area *= 100

        centers = get_center(contours[max_area_contour])

        if max_area_contour == -1:
            return [1, 0, 1000, imgname]
        elif max_area <= 0.2:
            return [1, max_area, 1000000, imgname]
        elif max_area >= G_thd:
            GAP = (centers[0] - wid / 2) / (wid / 2) * 100
            return [0, max_area, GAP, imgname]
        else:
            GAP = (centers[0] - wid / 2) / (wid / 2) * 100
            return [1, max_area, GAP, imgname]
    except:
        return [1000, 1000, 1000, imgname]


# 輪郭の中心を取り出す。
# centers = [get_center(x) for x in contours]
# print("centers=="+str(centers))
anan = GoalDetection('img/red2.png')
print(anan)
