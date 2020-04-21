import string
from Socket import openSocket, sendMessage


def getUser(line):
    separate = line.split(":")
    user = separate[1].split("!", 1)[0]
    return user
def getMessage(line):
    separate = line.split(":")
    message = separate[2]
    return message


def joinRoom(s):
    readbuffer = ""
    Loading = True
    while Loading:
        readbuffer = readbuffer + s.recv(1024).decode()
        print(readbuffer)
        temp = readbuffer.split("\n")
        readbuffer = temp.pop()

        for line in temp:
            print(line)
            Loading = loadingComplete(line)
    # sendMessage(s, "MrDestructoid reporting for duty!")

def loadingComplete(line):
    if("End of /NAMES list" in line):
        return False
    else:
        return True



s = openSocket()
joinRoom(s)
readbuffer = ""

while True:
    readbuffer = readbuffer + s.recv(1024).decode()

    temp = readbuffer.split("\n")
    readbuffer = temp.pop()

    for line in temp:
        print(line)
        if "PING" in line:
            s.send(line.replace("PING", "PONG").encode())
            break
        user = getUser(line)
        message = getMessage(line)
        print (user + ": " + message)

        
        if "you suck" in message:
            if user=='ubercruzer':
                sendMessage(s, 'yeah ok')
            else:
                sendMessage(s, "no u @" + user)
            break

# readbuffer = readbuffer + s.recv(1024).decode()

# print(readbuffer)