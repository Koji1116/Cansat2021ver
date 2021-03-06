import os
import linecache


def saveLog(path, *data):
    """
    制御ログのための関数
    前半はgit管理でログ作成用
    後半はgit管理外でログ作成用(git操作間違えてもログを残すため)
    """
    with open(path, "a") as f:
        for i in range(len(data)):
            if isinstance(data[i], list):
                for j in range(len(data[i])):
                    f.write(str(data[i][j]) + "\t")
            else:
                f.write(str(data[i]) + "\t")
        f.write("\n")

    # for log outside of git management
    rfd = path.rfind('/')
    path_backup = '/home/pi/Desktop/log' + path[rfd:]
    with open(path_backup, "a") as f:
        for i in range(len(data)):
            if isinstance(data[i], list):
                for j in range(len(data[i])):
                    f.write(str(data[i][j]) + "\t")
            else:
                f.write(str(data[i]) + "\t")
        f.write("\n")


def fileName(f, ext):
    i = 0
    num = ""
    while 1:
        num = ""
        if len(str(i)) <= 4:
            for j in range(4 - len(str(i))):
                num = num + "0"
            num = num + str(i)
        else:
            num = str(i)
        if not (os.path.exists(f + num + "." + ext)):
            break
        i = i + 1
    f = f + num + "." + ext
    return f


def phaseCheck(path):
    num_lines = sum(1 for line in open(path))
    lastLine = linecache.getline(path, num_lines)
    if not lastLine:
        return 0
    phase = lastLine[0]
    linecache.clearcache()
    return int(phase)


def positionCheck(path):
    num_lines = sum(1 for line in open(path))
    # print(num_lines)
    pos = [0.0, 0.0]
    for i in range(num_lines):
        line = linecache.getline(path, i + 1)
        posStr = line.split("\t")
        # print(line)
        if (posStr[0] == "Start"):
            pos = [posStr[1], posStr[2]]
            break
    return pos


if __name__ == "__main__":
    print(positionCheck("/home/pi/log/positionLog.txt"))
