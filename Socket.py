
import socket
from Params import HOST, PORT, PASS, IDENT
import time


class JoinChat:
	def __init__(self, CHANNEL):

		self.channel = CHANNEL
		self.s = socket.socket()
		self.s.connect((HOST, PORT))
		self.s.send(("PASS " + PASS + "\r\n").encode())
		self.s.send(("NICK " + IDENT + "\r\n").encode())
		self.s.send(("JOIN #" +  self.channel + "\r\n").encode())
		

	# def openSocket(self, CHANNEL):
		
	# 	s = socket.socket()
	# 	s.connect((HOST, PORT))
	# 	s.send(("PASS " + PASS + "\r\n").encode())
	# 	s.send(("NICK " + IDENT + "\r\n").encode())
	# 	s.send(("JOIN #" +  CHANNEL + "\r\n").encode())
	# 	return s
		
	def sendMessage(self, message):
		messageTemp = "PRIVMSG #" + self.channel + " :" + message
		self.s.send((messageTemp + "\r\n").encode())
		# print("Sent: " + messageTemp)
		time.sleep(1/70)





	def getUser(self, line):
		separate = line.split(":")
		user = separate[1].split("!", 1)[0]
		return user
	def getMessage(self, line):
		separate = line.split(":")
		message = separate[2]
		return message


	def joinRoom(self):
		try:
			readbuffer = ""
			Loading = True
			while Loading:
				readbuffer = readbuffer + self.s.recv(2048).decode()
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

	def loadingComplete(self, line):
		if("End of /NAMES list" in line):
			return False
		else:
			return True


	def reconnect(self, interval=1, timeout=300):
		try:
			print('reconnecting... retry in ', interval, 's')
			time.sleep(interval)
			self.s = __init__()
			self.s.settimeout(timeout)
			joinRoom(self.s)
			
			return self.s, True
		except:
			print('reconnect exception')
			return self.s, False

	def deEmojify(self, inputString):
		return inputString.encode('ascii', 'ignore').decode('ascii')