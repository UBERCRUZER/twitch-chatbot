import string
from Socket import openSocket, sendMessage
import time

import mysql.connector
from Params import hostSQL, userSQL, passwdSQL, databaseSQL, CHANNEL
import os
import json
import twitchIntegration

twitchAPI = twitchIntegration.twitchAPI()


mydb = mysql.connector.connect(
    host=hostSQL,
    user=userSQL,
    passwd=passwdSQL,
    auth_plugin='mysql_native_password',
    database=databaseSQL
)


mycursor = mydb.cursor()

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


# def checkConnect(s):
#     try: 
#         start = time.clock()
#         print('checking connection...')
#         data = s.recv(1024)
#         elapsed = time.clock() - start
#         if elapsed < .5:
#             return False
#         return True
#     except:
#         print('connection dead')
#         return False


timeout = 300

s = openSocket()
s.settimeout(timeout)
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
            s.send(bytes("PONG :tmi.twitch.tv\r\n", "UTF-8"))

            print(pong)
            s.settimeout(timeout)
            break
        user = getUser(line)
        message = getMessage(line)


        query = twitchAPI.get_users([user], byName=True)
        response = twitchAPI.get_response(query)

# # # --------------------------------------- INSERT INTO PERSONS TABLE -----------------------------

        for i in response.json()['data']:
            sql = 'SELECT * FROM persons WHERE user_id = {0}'.format(i['id'])
            mycursor.execute(sql)
            if len(mycursor.fetchall()) == 0:
                sql = 'INSERT INTO persons (user_id, display_name, view_count, broadcaster_type) VALUES (%s, %s, %s, %s)'
                val = (i['id'], i['display_name'], i['view_count'], i['broadcaster_type'])
                mycursor.execute(sql, val)
                print('added ' + user + ' to database')

        mydb.commit()

# # # --------------------------------------- INSERT CHATROOM TABLE ---------------------------------


        sql = 'INSERT INTO chatroom (display_name, chat_line, chatchannel) VALUES (%s, %s, %s)'
        val = (user, deEmojify(message), CHANNEL)
        mycursor.execute(sql, val)
        mydb.commit()

        if ("hey bot, you there?" in message) and (user=='ubercruzer'):
            sendMessage(s, 'yeah man, im here @ubercruzer')
            break

        if "you suck" in message:
            if user=='ubercruzer':
                sendMessage(s, 'yeah :(')
            else:
                sendMessage(s, "no u @" + user)
            break

        if "hey bot, quit" in message:
            if user=='ubercruzer':
                sendMessage(s, 'seppuku, confirmed. i have brought shame to this channel.')
                connected = False
            else:
                sendMessage(s, "no u @" + user)
            break

print('dead connection')

