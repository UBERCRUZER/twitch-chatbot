import string
import TwitchChat
import time

import mysql.connector
from Params import hostSQL, userSQL, passwdSQL, databaseSQL
import os
import json
import twitchIntegration
from ChatFunctions import getUser, getMessage, joinRoom, loadingComplete, reconnect, deEmojify

# chatChannel = 'ubercruzer'
# chatChannel = 'goofygains'
# chatChannel = 'emandliv'
# chatChannel = 'arrowfit'
# chatChannel = 'nikkiblackketter'
chatChannel = 'nicoflores74'

# chatChannel = 'tominationtime'
# chatChannel = 'martinimonsters'
# chatChannel = 'benrice_plgandalf'

twitchAPI = twitchIntegration.twitchAPI()

chatRoom = TwitchChat.JoinChat(chatChannel)

mydb = mysql.connector.connect(
    host=hostSQL,
    user=userSQL,
    passwd=passwdSQL,
    auth_plugin='mysql_native_password',
    database=databaseSQL
)

mycursor = mydb.cursor()

timeout = 300

connected = False

connected = chatRoom.joinRoom()
readbuffer = ""

while connected:

    try:
        readbuffer = readbuffer + chatRoom.getIncoming()
    except:
        print('socket recv error')
        # chatRoom = TwitchChat.JoinChat(chatChannel)
        # connected = chatRoom.joinRoom()
        connected = False


    temp = readbuffer.split("\n")
    readbuffer = temp.pop()
    
    for line in temp:
        # print(line)
        if "PING" in line:

            chatRoom.pong()
            break
        user = getUser(line)
        message = getMessage(line)


        response = None

# # # --------------------------------------- INSERT INTO PERSONS TABLE -----------------------------

        sql = 'SELECT * FROM persons WHERE display_name = "{0}"'.format(user)
        mycursor.execute(sql)
        result = mycursor.fetchall()
        if len(result) == 0:
            query = twitchAPI.get_users([user], byName=True)
            response = twitchAPI.get_response(query)
            print('adding ' + response.json()['data'][0]['display_name'] + ' to database')
            for i in response.json()['data']:
                # sql = 'SELECT * FROM persons WHERE user_id = {0}'.format(i['id'])
                # mycursor.execute(sql)
                # if len(mycursor.fetchall()) == 0:
                sql = 'INSERT INTO persons (user_id, display_name, view_count, broadcaster_type) VALUES (%s, %s, %s, %s)'
                val = (i['id'], i['display_name'], i['view_count'], i['broadcaster_type'])
                mycursor.execute(sql, val)
                # print('added ' + user + ' to database')
                mydb.commit()

# # # --------------------------------------- INSERT CHATROOM TABLE ---------------------------------

        
        # get user ID
        sql = 'SELECT user_id FROM persons WHERE display_name = "{0}"'.format(user)
        mycursor.execute(sql)
        result = mycursor.fetchall()

        # insert into chat table
        sql = 'INSERT INTO chatroom (from_ID, display_name, chat_line, chatchannel) VALUES (%s, %s, %s, %s)'
        val = (result[0][0], user, deEmojify(message), chatChannel)
        mycursor.execute(sql, val)
        mydb.commit()

# # # --------------------------------------- REPLIES -----------------------------------------------

        if ('bot' in message.lower()) and ('you there' in message.lower()) and (user=='ubercruzer'):
            chatRoom.sendMessage('yeah man, im here @ubercruzer')
            break

        if 'you suck' in message.lower():
            if user=='ubercruzer':
                chatRoom.sendMessage('yeah :(')
            else:
                chatRoom.sendMessage('no u @' + user)
            break

        if ('bot' in message.lower()) and ('kys' in message.lower()):
            if user=='ubercruzer':
                chatRoom.sendMessage('seppuku, confirmed. i have brought shame to this channel.')
                connected = False
            else:
                chatRoom.sendMessage('no u @' + user)
            break

        if ('go away' in message.lower()) and ('bot' in message.lower()):
            if user=='ubercruzer':
                chatRoom.sendMessage('i see how it is. i thought we were friends.')
                connected = False
            else:
                chatRoom.sendMessage('no u @' + user)
            break

print('disconnecting from', chatChannel)

