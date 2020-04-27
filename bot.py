import string
from Socket import openSocket, sendMessage
import time


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


def reconnect(interval=1):
    try:
        print('reconnecting... retry in ', interval, 's')
        time.sleep(interval)
        s = openSocket()
        s.settimeout(300)
        joinRoom(s)
        
        return s, True
    except:
        print('reconnect exception')

        return s, False


# def checkConnect(s):
#     try: 
#         print('checking connection...')
#         data = s.recv(1024)

#         if len(data) == 0:
#             return False
#         return True
#     except:
#         print('connection dead')
#         return False




s = openSocket()
s.settimeout(300)
connected = False

connected = joinRoom(s)
readbuffer = ""

while connected:


    try:
        readbuffer = readbuffer + s.recv(2048).decode()
    except:
        print('socket recv error')
        s, connected = reconnect()


    temp = readbuffer.split("\n")
    readbuffer = temp.pop()
    
    for line in temp:
        print(line)
        if "PING" in line:
            pong = line.replace("PING", "PONG")
            s.send(pong.encode())
            # s.send(bytes("PONG :pingisn", "UTF-8"))
            # s.send('PONG :tmi.twitch.tv'.encode())
            # print(line.replace("PING", "PONG").encode())
            print(pong)
            s.settimeout(300)
            break
        user = getUser(line)
        message = getMessage(line)
        # print (user + ": " + message)

        
        if ("hey bot, you there?" in message) and (user=='ubercruzer'):
            sendMessage(s, 'yeah man, im here @ubercruzer')
            break

        if "you suck" in message:
            if user=='ubercruzer':
                sendMessage(s, 'yeah :(')
            else:
                sendMessage(s, "no u @" + user)
            break

        if "hey bot, quit!" in message:
            if user=='ubercruzer':
                sendMessage(s, 'seppuku, confirmed. i have brought shame to this channel.')
                connected = False
            else:
                sendMessage(s, "no u @" + user)
            break

print('dead connection')

