import io
from PIL import Image
import serial
import pigpio

pi = pigpio.pi()

#port = serial.Serial(
#    port="/dev/ttyAMA0",
#    baudrate=57600,
#    parity=serial.PARITY_NONE,
#    stopbits=serial.STOPBITS_ONE,
#    bytesize=serial.EIGHTBITS,
#    timeout=5
#)

def ImageToByte(img1):
    img = Image.open(img1)
    with io.BytesIO() as output:
        img.save(output, format="JPEG")
        ImgTobyte = output.getvalue()
        return ImgTobyte
def img_trans(string):
    port = serial.Serial(
        port="/dev/ttyAMA0",
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=10
    )
    port.write(string)
    port.close()

def str_trans(string):
    ser = serial. Serial(
        port="/dev/ttyAMA0",
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=20
    )
    string = string + '\n'
    moji = string.encode()
    commands = [moji]
    for cmd in commands:
        ser.write(cmd)
    ser.flush()
    ser.close()


def str_receive():
    ser = serial.Serial(
        port="/dev/ttyAMA0",
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=10
    )
    received = ser.read()
    received_str = received.decode()
    return received_str

def on():
    pi.write(12, 1)

def off():
    pi.write(12, 0)

#str_trans('!')
str_trans('aaaaaaaaa')
# img1 = "/home/pi/Desktop/transfer-test/003.jpg"
# img_string = convert_string(img1)
# img_string = ImageToByte(img1)

# img_trans(img_string)
