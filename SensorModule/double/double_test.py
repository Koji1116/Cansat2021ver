import sys
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
sys.path.append('/home/pi/Desktop/Cansat2021ver/Other')
import math
import time
import datetime
import difflib
import pigpio
import numpy as np
import traceback
import Other
import glob


import Other
import datetime
import time
from smbus import SMBus
import glob

path_log = '/home/pi/Desktop/Cansat2021ver/SensorModule/double/BME'
filecount = len(glob.glob1(path_log, '*' + '.txt'))

bus_number = 1
i2c_address = 0x76 # 16進数77番でi2c通信

bus = SMBus(bus_number)

digT = []  # Temperature[℃]
digP = []  # Pressure[hPa]
digH = []  # Humidity[%]
t_fine = 0.0
RX = 18
pi = pigpio.pi()

#-------for test --------# takayama
log_static_path = '/home/pi/Desktop/Cansat2021ver/SensorModule/double/GPS'
filecount = len(glob.glob1(log_static_path, '*' + '.txt'))

ELLIPSOID_GRS80 = 1  # GRS80
ELLIPSOID_WGS84 = 2  # WGS84

# Long Axis Radius and Flat Rate
GEODETIC_DATUM = {
    ELLIPSOID_GRS80: [
        6378137.0,         # [GRS80] Long Axis Radius
        1 / 298.257222101,  # [GRS80] Flat Rate
    ],
    ELLIPSOID_WGS84: [
        6378137.0,         # [WGS84] Long Axis Radius
        1 / 298.257223563,  # [WGS84] Flat Rate
    ],
}

# Limited times of Itereation
ITERATION_LIMIT = 1000


def openGPS():
    try:
        pi.set_mode(RX, pigpio.INPUT)
        pi.bb_serial_read_open(RX, 9600, 8)
    except pigpio.error as e:
        #print("Open GPS Error")
        pi.set_mode(RX, pigpio.INPUT)
        pi.bb_serial_read_close(RX)
        pi.bb_serial_read_open(RX, 9600, 8)


def readGPS():
    utc = -1.0
    Lat = -1.0
    Lon = 0.0
    sHeight = 0.0
    gHeight = 0.0
    value = [0.0, 0.0, 0.0, 0.0, 0.0]

    (count, data) = pi.bb_serial_read(RX)
    if count:
        # print(data)
        # print(type(data))
        if isinstance(data, bytearray):
            gpsData = data.decode('utf-8', 'replace')

        # print(gpsData)
        # print()
        # print()
        gga = gpsData.find('$GPGGA,')
        rmc = gpsData.find('$GPRMC,')
        gll = gpsData.find('$GPGLL,')

        # print(gpsData[rmc:rmc+20])
        # print(gpsData[gll:gll+40])
        if gpsData[gga:gga+20].find(",0,") != -1 or gpsData[rmc:rmc+20].find("V") != -1 or gpsData[gll:gll+60].find("V") != -1:
            utc = -1.0
            Lat = 0.0
            Lon = 0.0
        else:
            utc = -2.0
            if gpsData[gga:gga+60].find(",N,") != -1 or gpsData[gga:gga+60].find(",S,") != -1:
                gpgga = gpsData[gga:gga+72].split(",")
                # print(gpgga)
                if len(gpgga) >= 6:
                    utc = gpgga[1]
                    lat = gpgga[2]
                    lon = gpgga[4]
                    try:
                        utc = float(utc)
                        Lat = round(float(lat[:2]) + float(lat[2:]) / 60.0, 6)
                        Lon = round(float(lon[:3]) + float(lon[3:]) / 60.0, 6)
                    except:
                        utc = -2.0
                        Lat = 0.0
                        Lon = 0.0
                    if gpgga[3] == "S":
                        Lat = Lat * -1
                    if gpgga[5] == "W":
                        Lon = Lon * -1
                else:
                    utc = -2.0
                if len(gpgga) >= 12:
                    try:
                        sHeight = float(gpgga[9])
                        gHeight = float(gpgga[11])
                    except:
                        pass
                    #print(sHeight, gHeight)
            # print(gpsData[gll:gll+60].find("A"))
            if gpsData[gll:gll+40].find("N") != -1 and utc == -2.0:
                gpgll = gpsData[gll:gll+72].split(",")
                # print(gpgll)
                # print("a")
                if len(gpgll) >= 6:
                    utc = gpgll[5]
                    lat = gpgll[1]
                    lon = gpgll[3]
                    try:
                        utc = float(utc)
                        Lat = round(float(lat[:2]) + float(lat[2:]) / 60.0, 6)
                        Lon = round(float(lon[:3]) + float(lon[3:]) / 60.0, 6)
                    except:
                        utc = -2.0
                    if gpgll[2] == "S":
                        Lat = Lat * -1
                    if gpgll[4] == "W":
                        Lon = Lon * -1
                else:
                    utc = -2.0
            if gpsData[rmc:rmc+20].find("A") != -1 and utc == -2.0:
                gprmc = gpsData[rmc:rmc+72].split(",")
                # print(gprmc)
                # print("b")
                if len(gprmc) >= 7:
                    utc = gprmc[1]
                    lat = gprmc[3]
                    lon = gprmc[5]
                    try:
                        utc = float(utc)
                        Lat = round(float(lat[:2]) + float(lat[2:]) / 60.0, 6)
                        Lon = round(float(lon[:3]) + float(lon[3:]) / 60.0, 6)
                    except:
                        utc = -1.0
                        Lat = 0.0
                        Lon = 0.0
                    if(gprmc[4] == "S"):
                        Lat = Lat * -1
                    if(gprmc[6] == "W"):
                        Lon = Lon * -1
                else:
                    utc = -1.0
                    Lat = -1.0
                    Lon = 0.0
            if utc == -2.0:
                utc = -1.0
                Lat = -1.0
                Lon = 0.0

    value = [utc, Lat, Lon, sHeight, gHeight]
    for i in range(len(value)):
        if not (isinstance(value[i], int) or isinstance(value[i], float)):
            value[i] = 0
    return value


def closeGPS():
    pi.bb_serial_read_close(RX)
    pi.stop()


def Cal_RhoAng(lat_a, lon_a, lat_b, lon_b):
    if(lat_a == lat_b and lon_a == lon_b):
        return 0.0, 0.0
    ra = 6378.140  # equatorial radius (km)
    rb = 6356.755  # polar radius (km)
    F = (ra-rb)/ra  # flattening of the earth
    rad_lat_a = np.radians(lat_a)
    rad_lon_a = np.radians(lon_a)
    rad_lat_b = np.radians(lat_b)
    rad_lon_b = np.radians(lon_b)
    pa = np.arctan(rb/ra*np.tan(rad_lat_a))
    pb = np.arctan(rb/ra*np.tan(rad_lat_b))
    xx = np.arccos(np.sin(pa)*np.sin(pb) + np.cos(pa) *
                   np.cos(pb)*np.cos(rad_lon_a-rad_lon_b))
    c1 = (np.sin(xx)-xx)*(np.sin(pa) + np.sin(pb))**2 / np.cos(xx/2)**2
    c2 = (np.sin(xx)+xx)*(np.sin(pa) - np.sin(pb))**2 / np.sin(xx/2)**2
    dr = F/8*(c1-c2)
    rho = ra*(xx + dr) * 1000  # Convert To [m]
    angle = math.atan2(lon_a-lon_b,  lat_b-lat_a) * 180 / math.pi  # [deg]
    return rho, angle


def vincentyInverse(lat1, lon1, lat2, lon2, ellipsoid=None):
    if lat1 == lat2 and lon1 == lon2:
        return 0.0, 0.0

    # Calculate Short Axis Radius
    # if Ellipsoid is not specified, it uses GRS80
    a, f = GEODETIC_DATUM.get(ellipsoid, GEODETIC_DATUM.get(ELLIPSOID_GRS80))
    b = (1 - f) * a

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    lambda1 = math.radians(lon1)
    lambda2 = math.radians(lon2)

    # Corrected Latitude
    U1 = math.atan((1 - f) * math.tan(phi1))
    U2 = math.atan((1 - f) * math.tan(phi2))

    sinU1 = math.sin(U1)
    sinU2 = math.sin(U2)
    cosU1 = math.cos(U1)
    cosU2 = math.cos(U2)

    # Diffrence of Longtitude between 2 points
    L = lambda2 - lambda1

    # Reset lamb to L
    lamb = L

    # Calculate lambda untill it converges
    # if it doesn't converge, returns None
    for i in range(ITERATION_LIMIT):
        sinLambda = math.sin(lamb)
        cosLambda = math.cos(lamb)
        sinSigma = math.sqrt((cosU2 * sinLambda) ** 2 +
                             (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) ** 2)
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
        sigma = math.atan2(sinSigma, cosSigma)
        sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
        cos2Alpha = 1 - sinAlpha ** 2
        cos2Sigmam = cosSigma - 2 * sinU1 * sinU2 / cos2Alpha
        C = f / 16 * cos2Alpha * (4 + f * (4 - 3 * cos2Alpha))
        lambdaʹ = lamb
        lamb = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma *
                                             (cos2Sigmam + C * cosSigma * (-1 + 2 * cos2Sigmam ** 2)))

        # Deviation is udner 1e-12, break
        if abs(lamb - lambdaʹ) <= 1e-12:
            break
    else:
        return None

    # if it converges, calculates distance and angle
    u2 = cos2Alpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    dSigma = B * sinSigma * (cos2Sigmam + B / 4 * (cosSigma * (-1 + 2 * cos2Sigmam ** 2) -
                                                   B / 6 * cos2Sigmam * (-3 + 4 * sinSigma ** 2) * (-3 + 4 * cos2Sigmam ** 2)))

    s = b * A * (sigma - dSigma)  # Distance between 2 points
    alpha = -1 * math.atan2(cosU2 * sinLambda, cosU1 * sinU2 -
                            sinU1 * cosU2 * cosLambda)  # Angle between 2 points

    # return s(distance), and alpha(angle)
    return s, math.degrees(alpha)



#--　ポインタ/レジスタへの書き込み　--#


def writeReg(reg_address, data):
    bus.write_byte_data(i2c_address, reg_address, data)

#--　キャリブレーションパラメータの取得　--#


def bme280_calib_param():
    '''
    '''
    calib = []

    for i in range(0x88, 0x88+24):
        calib.append(bus.read_byte_data(i2c_address, i))
    calib.append(bus.read_byte_data(i2c_address, 0xA1))
    for i in range(0xE1, 0xE1+7):
        calib.append(bus.read_byte_data(i2c_address, i))

    digT.append((calib[1] << 8) | calib[0])
    digT.append((calib[3] << 8) | calib[2])
    digT.append((calib[5] << 8) | calib[4])
    digP.append((calib[7] << 8) | calib[6])
    digP.append((calib[9] << 8) | calib[8])
    digP.append((calib[11] << 8) | calib[10])
    digP.append((calib[13] << 8) | calib[12])
    digP.append((calib[15] << 8) | calib[14])
    digP.append((calib[17] << 8) | calib[16])
    digP.append((calib[19] << 8) | calib[18])
    digP.append((calib[21] << 8) | calib[20])
    digP.append((calib[23] << 8) | calib[22])
    digH.append(calib[24])
    digH.append((calib[26] << 8) | calib[25])
    digH.append(calib[27])
    digH.append((calib[28] << 4) | (0x0F & calib[29]))
    digH.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
    digH.append(calib[31])

    for i in range(1, 2):
        if digT[i] & 0x8000:
            digT[i] = (-digT[i] ^ 0xFFFF) + 1

    for i in range(1, 8):
        if digP[i] & 0x8000:
            digP[i] = (-digP[i] ^ 0xFFFF) + 1

    for i in range(0, 6):
        if digH[i] & 0x8000:
            digH[i] = (-digH[i] ^ 0xFFFF) + 1

#--　気圧データ読み込み　--#


def compensate_P(adc_P):
    global t_fine
    pressure = 0.0

    v1 = (t_fine / 2.0) - 64000.0
    v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * digP[5]
    v2 = v2 + ((v1 * digP[4]) * 2.0)
    v2 = (v2 / 4.0) + (digP[3] * 65536.0)
    v1 = (((digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8) +
          ((digP[1] * v1) / 2.0)) / 262144
    v1 = ((32768 + v1) * digP[0]) / 32768

    if v1 == 0:
        return 0
    pressure = ((1048576 - adc_P) - (v2 / 4096)) * 3125
    if pressure < 0x80000000:
        pressure = (pressure * 2.0) / v1
    else:
        pressure = (pressure / v1) * 2
    v1 = (digP[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
    v2 = ((pressure / 4.0) * digP[7]) / 8192.0
    pressure = pressure + ((v1 + v2 + digP[6]) / 16.0)

    return pressure/100


def compensate_T(adc_T):
    '''
    温度データ読み込み
    '''
    global t_fine
    v1 = (adc_T / 16384.0 - digT[0] / 1024.0) * digT[1]
    v2 = (adc_T / 131072.0 - digT[0] / 8192.0) * \
        (adc_T / 131072.0 - digT[0] / 8192.0) * digT[2]
    t_fine = v1 + v2
    temperature = t_fine / 5120.0
    return temperature


def compensate_H(adc_H):
    '''
    湿度データ読み込み
    '''
    global t_fine
    var_h = t_fine - 76800.0
    if var_h != 0:
        var_h = (adc_H - (digH[3] * 64.0 + digH[4]/16384.0 * var_h)) * (digH[1] / 65536.0 * (
            1.0 + digH[5] / 67108864.0 * var_h * (1.0 + digH[2] / 67108864.0 * var_h)))
    else:
        return 0
    var_h = var_h * (1.0 - digH[0] * var_h / 524288.0)
    if var_h > 100.0:
        var_h = 100.0
    elif var_h < 0.0:
        var_h = 0.0
    return var_h

#--　セットアップ　--#


def bme280_setup():
    osrs_t = 1  # Temperature oversampling x 1
    osrs_p = 1  # Pressure oversampling x 1
    osrs_h = 1  # Humidity oversampling x 1
    mode = 3  # Normal mode
    t_sb = 5  # Tstandby 1000ms
    filter = 0  # Filter off
    spi3w_en = 0  # 3-wire SPI Disable

    ctrl_meas_reg = (osrs_t << 5) | (osrs_p << 2) | mode
    config_reg = (t_sb << 5) | (filter << 2) | spi3w_en
    ctrl_hum_reg = osrs_h

    writeReg(0xF2, ctrl_hum_reg)
    writeReg(0xF4, ctrl_meas_reg)
    writeReg(0xF5, config_reg)
#--------------------------------------------------------------------------
#--　データ読み込み　--#


def bme280_read():
    try:
        data = []
        for i in range(0xF7, 0xF7+8):
            data.append(bus.read_byte_data(i2c_address, i))

        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        temp = compensate_T(temp_raw)
        pres = compensate_P(pres_raw)
        hum = compensate_H(hum_raw)

        SeaLevelPres = 1013
        alt = ((temp+273.15)/0.0065) * \
            (pow(SeaLevelPres / pres, (1/5.257)) - 1.0)
        value = [temp, pres, hum, alt]

        for i in range(len(value)):
            if value[i] is not None:
                value[i] = round(value[i], 4)
    except:
        value = [0.0, 0.0, 0.0, 0.0]

    return value



if __name__ == '__main__':
    try:
        openGPS()
        bme280_setup()
        bme280_calib_param()
        t_start = time.time()
        #filecount = len(glob.glob1(log_static_path + '*'))
        while True:
            utc, lat, lon, sHeight, gHeight = readGPS()
            if utc == -1.0:
                if lat == -1.0:
                    print("Reading GPS Error")
                    Other.saveLog(log_static_path + str(filecount) + ".txt",datetime.datetime.now(), time.time() - t_start, 0, 0)
                    # pass
                else:
                    # pass
                    print("Status V")
                    Other.saveLog(log_static_path + str(filecount) + ".txt",datetime.datetime.now(), time.time() - t_start, 0, 0)
            else:
                # pass
                print(utc, lat, lon, sHeight, gHeight)
                Other.saveLog(log_static_path + 'static_test-' + str(filecount) + ".txt", datetime.datetime.now(), time.time() - t_start, lat, lon)
            
            temp, pres, hum, alt = bme280_read()
            # print(str(pres) + "\t" + str(alt) + "\t" + str(temp) + "\t" + str(hum))
            print(f'Press:{str(pres)}	Alt:{str(alt)}	Temp:{str(temp)}	Hum:{str(hum)}')
            Other.saveLog(path_log + str(filecount), datetime.datetime.now(), time.time() - t_start, pres, alt, temp, hum)
            # with open("preslog.txt","w")as f:
            #	f.write(str(pres)+ "\t" + str(alt) + "\t"+str(temp) + "\t" + str(hum) + "\n")
            
            time.sleep(0.5)
    except KeyboardInterrupt:
        closeGPS()
        print("\r\nKeyboard Intruppted, Serial Closed", filecount)
    except:
        closeGPS()
        print(traceback.format_exc())
