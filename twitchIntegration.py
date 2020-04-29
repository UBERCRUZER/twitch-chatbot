import requests, json, sys
import os


class twitchAPI: 

    def __init__(self):

        secretFile = open("secret.txt")
        self.secret = secretFile.read()
        secretFile.close()

        IDFile = open("clientID.txt")
        clientID = IDFile.read()
        IDFile.close()

        self.BASE_URL = 'https://api.twitch.tv/helix/'
        self.CLIENT_ID = clientID
        self.INDENT = 4

        authPayload = self._getAuth(self.secret, 'client_credentials', clientID)
        self.bearerToken = authPayload.json()['access_token']
        timeoutDuration = authPayload.json()['expires_in']

        print('Authentication Success. Expires in', timeoutDuration, 'seconds.')

        self.HEADERS = {'Authorization': 'Bearer {0}'.format(self.bearerToken)}


    def _getAuth(self, secret, grant_type, client_ID):
        try: 
            URL = 'https://id.twitch.tv/oauth2/'
            authHeaders = {'Client-ID': client_ID}
            request = 'token?client_secret={0}&grant_type={1}'.format(secret, grant_type)
            payload = URL + request
            response = requests.post(payload, headers=authHeaders)

            token = response.json()['access_token']

            return response
        except:
            print ('Authentication Failed.')

            fileName = 'busted.json'
            filePath = os.path.join(os.getcwd(), fileName)

            with open(filePath, "w") as outfile: 
                json.dump(response.json(), outfile) 


    # get response from twitch API call
    def get_response(self, query):
        url  = self.BASE_URL + query
        response = requests.get(url, headers=self.HEADERS)
        return response

    # used for debugging the result
    def print_response(self, response):
        response_json = response.json()
        print_response = json.dumps(response_json, indent=self.INDENT)
        print(print_response)

    # # get the current live stream info, given a username
    # def get_user_streams_query(self, user_login):
    #     return 'streams?user_login={0}'.format(user_login)

    # def get_user_query(self, user_login):
    #     return 'users?login={0}'.format(user_login)

    # def get_user_videos_query(self, user_id):
    #     return 'videos?user_id={0}&first=50'.format(user_id)

    def get_followers_to(self, user_id, first=0, after=None):
        if ((after == None) & (first > 0)):
            return 'users/follows?to_id={0}&first={1}'.format(user_id, first)
        elif ((after != None) & (first == 0)):
            return 'users/follows?to_id={0}&after={1}'.format(user_id, after)
        elif ((after != None) & (first > 0)):
            return 'users/follows?to_id={0}&after={1}&first={2}'.format(user_id, after, first)
        else:
            return 'users/follows?to_id={0}'.format(user_id)

    def get_followers_from(self, user_id, first=0, after=None):
        if ((after == None) & (first > 0)):
            return 'users/follows?from_id={0}&first={1}'.format(user_id, first)
        elif ((after != None) & (first == 0)):
            return 'users/follows?from_id={0}&after={1}'.format(user_id, after)
        elif ((after != None) & (first > 0)):
            return 'users/follows?from_id={0}&after={1}&first={2}'.format(user_id, after, first)
        else:
            return 'users/follows?from_id={0}'.format(user_id)

    def get_users(self, users, byName=False):
        query = 'users?'
        if (not byName):
            for i in range(0,int(len(users))):
                if i == 0:
                    query = query + 'id=' + users[i]
                else:
                    query = query + '&id=' + users[i]
        elif (byName):
            for i in range(0,int(len(users))):
                if i == 0:
                    query = query + 'login=' + users[i]
                else:
                    query = query + '&login=' + users[i]
        return query