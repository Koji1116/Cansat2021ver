# -*- coding:utf-8 -*-
import cv2 
import numpy as np

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
    i = 100

    mask, _ = detect_red_color(img)
    
    

    # contour
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_contour = cv2.drawContours(img, contours, 6, (0, 255, 0), 5)
    cv2.imshow("img_edge",img_contour)
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
        return [0, max_area, 0, imgname]
    else:
        # rectangle
        centers = [get_center(x) for x in contours]
        GAP = centers[0]-wid/2
        return [1, max_area, GAP, imgname]
    


#輪郭の中心を取り出す。
#centers = [get_center(x) for x in contours]
#print("centers=="+str(centers))
anan = GoalDetection('img/red2.png')
print(anan)


