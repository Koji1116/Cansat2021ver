import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
import picamera
import time
import traceback
import Other

def Capture(path, width = 320, height = 240):
	filepath = ""
	try:
		with picamera.PiCamera() as camera:
			camera.rotation = 270
			#取得した画像の回転
			camera.resolution = (width,height)
			#取得する画像の解像度を設定→どのような基準で設定するのか
			#使用するカメラの解像度は静止画解像度で3280×2464
			filepath = Other.fileName(path,"jpg")
			#指定したパスを持つファイルを作成
			#個々の関数がよくわからない
			camera.capture(filepath)
			#そのファイルに取得した画像を入れる
	except picamera.exc.PiCameraMMALError:
		filepath = "Null"
		#パスが切れているときはNULL
		time.sleep(0.8)
	except:
		print(traceback.format_exc())
		time.sleep(0.1)
		filepath = "Null"
		#そのほかのエラーの時はNULL
	return filepath

if __name__ == "__main__":
	try:
		for i in range(3):
			photoName = Capture("photo/photo", 160, 120)
			print(photoName)
	except KeyboardInterrupt:
		print('stop')
	except:
		print(traceback.format_exc())
