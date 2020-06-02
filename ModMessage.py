import os
import pickle
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords


import mysql.connector
from Params import hostSQL, userSQL, passwdSQL, databaseSQL


class ModMessage: 

    def __init__(self):
        filename = 'model.sav'

        self.model = pickle.load(open('model.sav', 'rb'))
        self.porter=PorterStemmer()
        mydb = mysql.connector.connect(
            host=hostSQL,
            user=userSQL,
            passwd=passwdSQL,
            auth_plugin='mysql_native_password',
            database=databaseSQL
        )

        self.mycursor = mydb.cursor()

        self.porter = PorterStemmer()

        self.stop_words = pickle.load(open('stop_words.sav', 'rb'))



    def stemSentence(self, sentence):
        token_words=word_tokenize(sentence)
        token_words
        stem_sentence=[]
        for word in token_words:
            stem_sentence.append(porter.stem(word))
            stem_sentence.append(" ")
        return "".join(stem_sentence)


    def processMsg(self, msg):
        testMsg = [str(msg)]

        testMsg = [stemSentence(testMsg[0])]

        print('Prediction')
        X = vectorizer.transform(testMsg)
        predicted = model.predict(X)
        print(predicted)





