# -*- coding: utf-8 -*-

import smbus
import time

class Illumi:
    def __init__(self, address, channel):
        self.address    = address
        self.channel    = channel
        self.bus        = smbus.SMBus(self.channel)
        self.gain       = 0x00          # 0x00=normal, 0x10=×16
        self.integrationTime    = 0x02  # 0x02=402ms, 0x01=101ms, 0x00=13.7ms
        self.scale      = 1.0

        # センサ設定の初期化
        self.setLowGain()
        self.setIntegrationTime('default')

    def powerOn(self):
        self.bus.write_i2c_block_data(self.address, 0x80, [0x03])
        time.sleep(0.1)

    def powerOff(self):
        self.bus.write_i2c_block_data(self.address, 0x80, [0x00])

    def setHighGain(self):
        # High Gainにセットする(16倍の感度？)
        # High Gainにするとうまくrawデータが取れないことがある。
        # 要原因調査 ( 5047固定値になる )
        self.gain   = 0x10
        data        = self.integrationTime | self.gain
        self.bus.write_i2c_block_data(self.address, 0x81, [data])
        self.calcScale()

    def setLowGain(self):
        # Low Gain(default) にセットする
        self.gain   = 0x00
        data        = self.integrationTime | self.gain
        self.bus.write_i2c_block_data(self.address, 0x81, [data])
        self.calcScale()

    def setIntegrationTime(self, val):
        # 積分する時間の設定（１回のセンシングにかける時間？）
        # val = shor, middle, logn(default)
        if val=='short':
            self.integrationTime    = 0x00  # 13.7ms scale=0.034
        elif val=='middle':
            self.integrationTime    = 0x01  # 101ms  scale=0.252
        else:
            self.integrationTime    = 0x02  # defaultVal 402ms  scale=1.0
        data = self.integrationTime | self.gain
        self.bus.write_i2c_block_data(self.address, 0x81, [data])
        self.calcScale()

    def getVisibleLightRawData(self):
        data    = self.bus.read_i2c_block_data(self.address, 0xAC ,2)
        raw     = data[1] << 8 | data[0]    # 16bitで下位バイトが先
        return raw

    def getInfraredRawData(self):
        data    = self.bus.read_i2c_block_data(self.address, 0xAE ,2)
        raw     = data[1] << 8 | data[0]    # 16bitで下位バイトが先
        return raw

    def getRawData(self):
        data    = self.bus.read_i2c_block_data(self.address, 0xAC ,4)
        VL      = data[1] << 8 | data[0]    # 可視光　16bitで下位バイトが先
        IR      = data[3] << 8 | data[2]    # 赤外線　16bitで下位バイトが先
        return (VL,IR)

    def calcScale(self):
        _scale = 1.0
        # integrationTimeによるスケール
        if self.integrationTime == 0x01:    # middle
            _scale = _scale / 0.252
        elif self.integrationTime == 0x00:  # short
            _scale = _scale / 0.034

        # gainによるスケール
        if self.gain == 0x00 :              # gain 1
            _scale = _scale * 16.0

        self.scale = _scale

    def getLux(self):
        # センサ生データの取得
        raw  = self.getRawData()

        # 65535の時はエラー出力にする実装
        if raw[0] == 65535 or raw[1] == 65535:
            return 10000

        # センサ設定により生データをスケールする
        VLRD = raw[0] * self.scale
        IRRD = raw[1] * self.scale

        # 0の除算にならないように
        if (float(VLRD) == 0):
            ratio = 9999
        else:
            ratio = (IRRD / float(VLRD))

        # Luxの算出
        if ((ratio >= 0) & (ratio <= 0.52)):
            lux = (0.0315 * VLRD) - (0.0593 * VLRD * (ratio**1.4))
        elif (ratio <= 0.65):
            lux = (0.0229 * VLRD) - (0.0291 * IRRD)
        elif (ratio <= 0.80):
            lux = (0.0157 * VLRD) - (0.018 * IRRD)
        elif (ratio <= 1.3):
            lux = (0.00338 * VLRD) - (0.0026 * IRRD)
        elif (ratio > 1.3):
            lux = 0

        return lux
sensor1 = ""
sensor2 = ""

def tsl2561_setup():
	global sensor1
	global sensor2
	try:
		sensor1 = Illumi(0x39, 1)
		sensor1.powerOn()
		sensor1.setIntegrationTime('default')
	except:
		try:
			sensor1 = Illumi(0x39, 1)
			sensor1.powerOn()
			sensor1.setIntegrationTime('default')
		except:
			pass

	try:
		sensor2 = Illumi(0x29, 1)
		sensor2.powerOn()
		sensor2.setIntegrationTime('default')
	except:
		try:
			sensor2 = Illumi(0x29, 1)
			sensor2.powerOn()
			sensor2.setIntegrationTime('default')
		except:
			pass

def readLux():
	global sensor1
	global sensor2
	#sensor1  = Illumi(0x39,1)
	#sensor1.powerOn()
    #sensor1.setHighGain()
	#sensor1.setIntegrationTime('default')

	#sensor2  = Illumi(0x29,1)
	#sensor2.powerOn()
    #sensor2.setHighGain()
	#sensor2.setIntegrationTime('default')

	try:
		lux1 = sensor1.getLux()
	except:
		lux1 = -1.0

	try:
		lux2 = sensor2.getLux()
	except:
		lux2 = -1.0

	value = [lux1, lux2]
	return value

if __name__ == "__main__":
	try:
		tsl2561_setup()
		while 1:
			lux = readLux()
			print(str(lux[0])+"	:	"+str(lux[1]))
			#print(type(lux[0]+lux[1]))
			time.sleep(0.5)
	except KeyboardInterrupt:
		print()
