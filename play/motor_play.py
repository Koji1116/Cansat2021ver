#---↓設定（何もいじらなくて大丈夫）----
import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/Motor')
from gpiozero import Motor
import time
Rpin1, Rpin2 = 6, 5
Lpin1, Lpin2 = 9, 10


#---↓motorを動かすための設定（右側のローバ）
motor_r = Motor(Rpin1, Rpin2)
#---↓motorを動かすための設定（左側のローバ）
motor_l = Motor(Lpin1, Lpin2)

#例えば、ローバーを１秒間、出力(0~1で指定)0.6で前進させたいときは次のようにコードを書く。
motor_r.forward(0.6)  #右のモータ動かす指令
motor_l.forward(0.6)  #左のモータ動かす指令
time.sleep(1)         #1秒間待つ
motor_r.stop()        #右のモータ止める指令
motor_l.stop()        #左のモータ止める指令


#--------課題----------#
#問題：'w'が入力されたら１秒間前進、'a'が入力されたら１秒間斜め左方向に前進、'd'が入力されたら1秒間斜め右方向前進
#      というコードを下に書いてください

#ヒント1：入力に関してはinput関数を使う(参考url:https://qiita.com/naoya_ok/items/f33a6ab2ff77154a7121)
#ヒント2：場合分けはif文使う(参考url:https://note.nkmk.me/python-if-elif-else/) 