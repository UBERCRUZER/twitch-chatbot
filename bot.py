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
# chatChannel = 'thestrengthathlete'
# chatChannel = 'frimia'
# chatChannel = 'nikkiblackketter'
# chatChannel = 'nicoflores74'
# chatChannel = 'calgarybarbell'
# chatChannel = 'silentmikke'
# chatChannel = 'gretchen'
# chatChannel = 'tominationtime'
# chatChannel = 'martinimonsters'
# chatChannel = 'benrice_plgandalf'
# chatChannel = 'sevenlionsmusic'
# chatChannel = 'pink_sparkles'
# chatChannel = 'hafthorjulius'
# chatChannel = 'joeyallmight'
# chatChannel = 'kneecoleslaw'
# chatChannel = 'emmdeefit'
chatChannel = 'davinityyy'



twitchAPI = twitchIntegration.twitchAPI()
timeout = 300

chatRoom = TwitchChat.JoinChat(chatChannel, timeout=timeout)

mydb = mysql.connector.connect(
    host=hostSQL,
    user=userSQL,
    passwd=passwdSQL,
    auth_plugin='mysql_native_password',
    database=databaseSQL
)

mycursor = mydb.cursor()



connected = False

connected = chatRoom.joinRoom()
readbuffer = ""

while connected:

    try:
        readbuffer = readbuffer + chatRoom.getIncoming()
    except KeyboardInterrupt:
        print('kb interrupt. disconnecting.')
        # chatRoom = TwitchChat.JoinChat(chatChannel)
        # connected = chatRoom.joinRoom()
        connected = False
    # except:
    #     chatRoom = TwitchChat.JoinChat(chatChannel)
    #     connected = chatRoom.joinRoom()


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

            # check for duplicates user ID

            userID = response.json()['data'][0]['id']
            sql = 'SELECT * FROM persons WHERE user_id = "{0}"'.format(userID)
            mycursor.execute(sql)
            result = mycursor.fetchall()

            if len(result) == 0:
                print('adding ' + response.json()['data'][0]['display_name'] + ' to database')

                sql = 'INSERT INTO persons (user_id, display_name, view_count, broadcaster_type) VALUES (%s, %s, %s, %s)'
                val = (response.json()['data'][0]['id'], response.json()['data'][0]['display_name'], 
                       response.json()['data'][0]['view_count'], response.json()['data'][0]['broadcaster_type'])
                mycursor.execute(sql, val)
                mydb.commit()
            else:
                print('name change. modifying ' + response.json()['data'][0]['display_name'])

                sql = 'UPDATE persons SET display_name = %s, WHERE user_id = %s'
                val = (response.json()['data'][0]['display_name'], response.json()['data'][0]['id'])
                mycursor.execute(sql, val)
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

        if ('bot' in message.lower()) and ('you there' in message.lower()):
            if (user=='ubercruzer'):
                chatRoom.sendMessage('yeah man, im here @ubercruzer')
            else:
                chatRoom.sendMessage('leave me alone. im busy @' + user)
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
                chatRoom.sendMessage('thats not nice @' + user)
            break

        if ('go away' in message.lower()) and ('bot' in message.lower()):
            if user=='ubercruzer':
                chatRoom.sendMessage('i see how it is. i thought we were friends.')
                connected = False
            else:
                chatRoom.sendMessage('no u @' + user)
            break

chatRoom.disconnect()
print('disconnected from', chatChannel)

