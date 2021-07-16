import io
from PIL import Image
import serial


port = serial.Serial(
    port="/dev/ttyAMA0",
    baudrate=57600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=20
)

# 画像をバイト変換


def ImageToByte(img1):
    img = Image.open(img1)
    with io.BytesIO() as output:
        img.save(output, format="JPEG")
        ImgTobyte = output.getvalue()
        return ImgTobyte

# 画像をｐｃに送信


def img_trans(string):
    port = serial.Serial(
        port="/dev/ttyAMA0",
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=20
    )
    port.write(string)
    port.close()

# 文字列送信


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


str_trans('hello')
# img1 = "/home/pi/Desktop/transfer-test/003.jpg"
# # img_string = convert_string(img1)
# img_string = ImageToByte(img1)

# img_trans(img_string)
