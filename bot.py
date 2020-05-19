import string
import TwitchChat
import time

import mysql.connector
from Params import hostSQL, userSQL, passwdSQL, databaseSQL
import os
import json
import twitchIntegration
# from ChatFunctions import joinRoom, loadingComplete, reconnect
import pandas as pd

from streamerList import streamerList


twitchAPI = twitchIntegration.twitchAPI()
timeout = 300

chatRoom = TwitchChat.JoinChat(timeout=timeout)

mydb = mysql.connector.connect(
    host=hostSQL,
    user=userSQL,
    passwd=passwdSQL,
    auth_plugin='mysql_native_password',
    database=databaseSQL
)

mycursor = mydb.cursor()


connected = False

query = twitchAPI.get_live_streamers(streamerList)
response = twitchAPI.get_response(query)

onlineList = []
for i in response.json()['data']:
    onlineList.append(i['user_name'].lower())

for i in onlineList:
    connected = chatRoom.joinRoom(i)

connected = chatRoom.joinRoom('ubercruzer')

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
        user = chatRoom.getUser(line)
        message = chatRoom.getMessage(line)
        channel = chatRoom.getChannel(line)

        response = None

# # # --------------------------------------- INSERT INTO PERSONS TABLE -----------------------------

        sql = 'SELECT * FROM persons WHERE display_name = "{0}"'.format(user)
        mycursor.execute(sql)
        result = mycursor.fetchall()
        if len(result) == 0:
            query = twitchAPI.get_users([user], byName=True)
            response = twitchAPI.get_response(query)

            # check for name change

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

                sql = 'UPDATE persons SET display_name = %s WHERE user_id = %s'
                val = (response.json()['data'][0]['display_name'], int(response.json()['data'][0]['id']))
                mycursor.execute(sql, val)
                mydb.commit()

# # # --------------------------------------- INSERT FOLLOWER TABLE ---------------------------------

        # get user ID
        sql = 'SELECT * FROM persons WHERE display_name = "{0}"'.format(user)
        mycursor.execute(sql)
        result = mycursor.fetchall()
        
        from_id = result[0][0]

        if not (user == channel):

            # get channel ID
            sql = 'SELECT user_id FROM persons WHERE display_name = "{0}"'.format(channel)
            mycursor.execute(sql)
            result = mycursor.fetchall()

            if len(result) == 0:
                query = twitchAPI.get_users([channel], byName=True)
                response = twitchAPI.get_response(query)

                print('adding broadcaster ' + response.json()['data'][0]['display_name'] + ' to database')

                sql = 'INSERT INTO persons (user_id, display_name, view_count, broadcaster_type) VALUES (%s, %s, %s, %s)'
                val = (response.json()['data'][0]['id'], response.json()['data'][0]['display_name'], 
                        response.json()['data'][0]['view_count'], response.json()['data'][0]['broadcaster_type'])
                mycursor.execute(sql, val)
                mydb.commit()

                to_id = response.json()['data'][0]['id']
            else:
                to_id = result[0][0]

            following = True

            query = twitchAPI.get_follow_date(from_id, to_id)
            response = twitchAPI.get_response(query)
            try:
                followdate = response.json()['data'][0]['followed_at']
                followdate = followdate.replace('T', ' ').replace('Z','')
            
            except:
                # print('user not following')
                following = False

            # check if already in table
            sql = 'SELECT * FROM followers WHERE from_ID = "{0}" AND to_ID = "{1}"'.format(from_id, to_id)
            mycursor.execute(sql)
            result = mycursor.fetchall()

            if (len(result) == 0) and (following):

                sql = 'INSERT INTO followers (from_ID, to_ID, followed_at) VALUES (%s, %s, %s)'
                val = (from_id, to_id, followdate)
                mycursor.execute(sql, val)
                mydb.commit()
            # else:
            #     if following:
            #         print('already in database')
        else:
            print('broadcaster. skipping.')





# # # --------------------------------------- INSERT CHATROOM TABLE ---------------------------------


        # try:
        # insert into chat table
        sql = 'INSERT INTO chatroom (from_ID, display_name, chat_line, chatchannel) VALUES (%s, %s, %s, %s)'
        val = (from_id, user, chatRoom.deEmojify(message), channel)
        mycursor.execute(sql, val)
        mydb.commit()
        # except:
        #     connected = False
        #     errorFile = pd.DataFrame(result)
        #     errorFile.to_csv('dump.csv')




# # # --------------------------------------- REPLIES -----------------------------------------------

        if ('bot' in message.lower()) and ('you there' in message.lower()):
            if (user=='ubercruzer'):
                chatRoom.sendMessage('yeah man, im here @ubercruzer', channel)
            else:
                chatRoom.sendMessage('leave me alone. im busy @' + user, channel)
            break

        if 'you suck' in message.lower():
            if user=='ubercruzer':
                chatRoom.sendMessage('yeah :(', channel)
            else:
                chatRoom.sendMessage('no u @' + user, channel)
            break

        if ('bot' in message.lower()) and ('kys' in message.lower()):
            if user=='ubercruzer':
                chatRoom.sendMessage('seppuku, confirmed. i have brought shame to this channel.', channel)
                connected = False
            else:
                chatRoom.sendMessage('thats not nice @' + user, channel)
            break

        if ('go away' in message.lower()) and ('bot' in message.lower()):
            if user=='ubercruzer':
                chatRoom.sendMessage('i see how it is. i thought we were friends.', channel)
                connected = False
            else:
                chatRoom.sendMessage('no u @' + user, channel)
            break

chatRoom.disconnect()
print('disconnected success')

