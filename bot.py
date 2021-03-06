import string
import TwitchChat
import time

import mysql.connector
from Params import hostSQL, userSQL, passwdSQL, databaseSQL
import os
import json
import twitchIntegration
import pandas as pd

from streamerList import streamerList
import datetime


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

# ------------------------------------------------------
 
query = twitchAPI.get_live_streamers(streamerList)
response = twitchAPI.get_response(query)

watchingStreamer = []
for i in response.json()['data']:
    connected = chatRoom.joinRoom(i['user_name'].lower())
    if connected:
        watchingStreamer.append(i['user_name'].lower())


connected = chatRoom.joinRoom('ubercruzer')
watchingStreamer.append('ubercruzer')

# connected = chatRoom.joinRoom('martinimonsters')

# ------------------------------------------------------

readbuffer = ''

nextUpdate = datetime.datetime.now() + datetime.timedelta(minutes = 1)

print('----- room join success! -----')

while connected:


    if datetime.datetime.now() > nextUpdate:
        # print('updating streamers')
        query = twitchAPI.get_live_streamers(streamerList)
        response = twitchAPI.get_response(query)

        for i in response.json()['data']:
            currentlyWatching = False

            for j in watchingStreamer:
                if i['user_name'].lower() == j.lower():
                    currentlyWatching = True
            
            if not currentlyWatching:
                connected = chatRoom.joinRoom(i['user_name'].lower())
                if connected:
                    watchingStreamer.append(i['user_name'].lower())
                    connected = True

                # chatRoom.joinRoom(i['user_name'].lower())
                # watchingStreamer.append(i['user_name'].lower())

        for i in watchingStreamer:
            stillStreaming = False

            for j in response.json()['data']:
                if i.lower() == j['user_name'].lower():
                    stillStreaming = True
                
            if not stillStreaming:
                chatRoom.leaveRoom(i.lower())
                watchingStreamer.remove(i.lower())

        nextUpdate = datetime.datetime.now() + datetime.timedelta(minutes = 3)
        print(datetime.datetime.now(), ':', watchingStreamer)
        print(datetime.datetime.now(), ': streamer update complete. next :', nextUpdate)


    try:
        readbuffer = readbuffer + chatRoom.getIncoming()
    except KeyboardInterrupt:
        print('kb interrupt. disconnecting.')
        # chatRoom = TwitchChat.JoinChat(chatChannel)
        # connected = chatRoom.joinRoom()
        connected = False
        break
    except UnicodeDecodeError: 
        print(datetime.datetime.now(), ': UnicodeDecodeError: \'utf-8\' codec can\'t decode bytes in position : unexpected end of data')
        
    # except:
    #     chatRoom = TwitchChat.JoinChat(chatChannel)
    #     connected = chatRoom.joinRoom()


    temp = readbuffer.split("\n")
    readbuffer = temp.pop()
    
    for line in temp:
        # print(line)
        if 'PING' in line:

            chatRoom.pong()
            break

        try:
            user = chatRoom.getUser(line)
            message = chatRoom.getMessage(line)
            channel = chatRoom.getChannel(line)
        except IndexError:
            print(line)
            break

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
                print(datetime.datetime.now(), ': adding ' + response.json()['data'][0]['display_name'] + ' to database')

                sql = 'INSERT INTO persons (user_id, display_name, view_count, broadcaster_type) VALUES (%s, %s, %s, %s)'
                val = (response.json()['data'][0]['id'], response.json()['data'][0]['display_name'], 
                       response.json()['data'][0]['view_count'], response.json()['data'][0]['broadcaster_type'])
                mycursor.execute(sql, val)
                mydb.commit()
            else:
                print(datetime.datetime.now(), ': name change. modifying ' + response.json()['data'][0]['display_name'])

                sql = 'UPDATE persons SET display_name = %s WHERE user_id = %s'
                val = (response.json()['data'][0]['display_name'], int(response.json()['data'][0]['id']))
                mycursor.execute(sql, val)
                mydb.commit()

# # # --------------------------------------- INSERT FOLLOWER TABLE ---------------------------------

        # get user ID
        sql = 'SELECT * FROM persons WHERE display_name = "{0}"'.format(user)
        mycursor.execute(sql)
        result = mycursor.fetchall()
        
        try:
            from_id = result[0][0]
        except IndexError:
            print('sql return indexer error. messed up character encoding?')
            break
    
        if not (user == channel):

            # get channel ID
            sql = 'SELECT user_id FROM persons WHERE display_name = "{0}"'.format(channel)
            mycursor.execute(sql)
            result = mycursor.fetchall()

            if len(result) == 0:
                query = twitchAPI.get_users([channel], byName=True)
                response = twitchAPI.get_response(query)

                print(datetime.datetime.now(), ': adding broadcaster ' + response.json()['data'][0]['display_name'] + ' to database')

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
                try: 
                    sql = 'INSERT INTO followers (from_ID, to_ID, followed_at) VALUES (%s, %s, %s)'
                    val = (from_id, to_id, followdate)
                    mycursor.execute(sql, val)
                    mydb.commit()
                except mysql.connector.errors.DataError: 
                    print(datetime.datetime.now(), ': Incorrect datetime value')
                    break


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


        if ('you suck' in message.lower()) and (channel == 'martinimonsters'):
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
        

        # if ('go away' in message.lower()) and ('bot' in message.lower()):
        #     if user=='ubercruzer':
        #         chatRoom.leaveRoom('ubercruzer')
        #         # connected = False
        #     else:
        #         chatRoom.sendMessage('no u @' + user, channel)
        #     break


chatRoom.disconnect()
print('disconnected success')

