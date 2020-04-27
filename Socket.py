
import socket
from Params import HOST, PORT, PASS, IDENT, CHANNEL
import time


def openSocket():
	
	s = socket.socket()
	s.connect((HOST, PORT))
	s.send(("PASS " + PASS + "\r\n").encode())
	s.send(("NICK " + IDENT + "\r\n").encode())
	s.send(("JOIN #" +  CHANNEL + "\r\n").encode())
	return s
	
def sendMessage(s, message):
	messageTemp = "PRIVMSG #" + CHANNEL + " :" + message
	s.send((messageTemp + "\r\n").encode())
	print("Sent: " + messageTemp)
	time.sleep(1/100)