import time
import socket

def getUser(line):
    separate = line.split(":")
    user = separate[1].split("!", 1)[0]
    return user
def getMessage(line):
    separate = line.split(":")
    message = separate[2]
    return message


def joinRoom(s):
    try:
        readbuffer = ""
        Loading = True
        while Loading:
            readbuffer = readbuffer + s.recv(2048).decode()
            print(readbuffer)
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()

            for line in temp:
                print(line)
                Loading = loadingComplete(line)
        # sendMessage(s, "MrDestructoid reporting for duty!")
        return True
    except:
        return False

def loadingComplete(line):
    if("End of /NAMES list" in line):
        return False
    else:
        return True


def reconnect(interval=1, timeout=300):
    try:
        print('reconnecting... retry in ', interval, 's')
        time.sleep(interval)
        s = openSocket()
        s.settimeout(timeout)
        joinRoom(s)
        
        return s, True
    except:
        print('reconnect exception')

        return s, False

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')