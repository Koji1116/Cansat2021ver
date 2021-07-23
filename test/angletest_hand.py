import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
sys.path.append('/home/pi/Desktop/Cansat2021ver/SensorModule/6-axis')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Calibration')
import math
import BMC050
import time
import Calibration


def angle(magx, magy, magx_off=0, magy_off=0):
    θ = math.degrees(math.atan((magy - magy_off) / (magx - magx_off)))

    if magx - magx_off > 0 and magy - magy_off > 0:  # First quadrant
        pass  # 0 <= θ <= 90
    elif magx - magx_off < 0 and magy - magy_off > 0:  # Second quadrant
        θ = 180 + θ  # 90 <= θ <= 180
    elif magx - magx_off < 0 and magy - magy_off < 0:  # Third quadrant
        θ = θ + 180  # 180 <= θ <= 270
    elif magx - magx_off > 0 and magy - magy_off < 0:  # Fourth quadrant
        θ = 360 + θ  # 270 <= θ <= 360

    θ += 90

    if 360 <= θ <= 450:
        θ -= 360

    return θ


if __name__ == '__main__':
    BMC050.bmc050_setup()
    try:
        magdata_offset = Calibration.magdata_matrix_hand()
        magx_array_Old, magy_array_Old, magz_array_Old, magx_off, magy_off, magz_off = Calibration.calculate_offset(magdata_offset)
        time.sleep(0.1)
        while True:
            magdata = BMC050.mag_dataRead()
            mag_x = magdata[0]
            mag_y = magdata[1]
            θ = angle(mag_x, mag_y, magx_off, magy_off)
            # print(mag_x,mag_y)
            print(θ)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print('end')

