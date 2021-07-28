import time
import pigpio

pi = pigpio.pi()

meltPin = 17

def Melting(t_melt = 3):
	pi.write(meltPin, 0)
	time.sleep(1)
	pi.write(meltPin, 1)
	time.sleep(t_melt)
	pi.write(meltPin, 0)
	time.sleep(1)

if __name__ == "__main__":
	try:
		Melting()
	except:
		pi.write(meltPin, 0)

