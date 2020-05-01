
import socket
from Params import HOST, PORT, PASS, IDENT
import time


class JoinChat:
	def __init__(self, CHANNEL, timeout=300):

		self.channel = CHANNEL
		self.s = socket.socket()
		self.s.connect((HOST, PORT))
		self.s.send(("PASS " + PASS + "\r\n").encode())
		self.s.send(("NICK " + IDENT + "\r\n").encode())
		self.s.send(("JOIN #" +  self.channel + "\r\n").encode())
		self.s.settimeout(timeout)
		
		
	def sendMessage(self, message):
		messageTemp = "PRIVMSG #" + self.channel + " :" + message
		self.s.send((messageTemp + "\r\n").encode())
		# print("Sent: " + messageTemp)
		time.sleep(1/70)

	def getIncoming(self):
		return self.s.recv(2048).decode()

	def pong(self):
		self.s.send(bytes("PONG :tmi.twitch.tv\r\n", "UTF-8"))


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
				# print(readbuffer)
				temp = readbuffer.split("\n")
				readbuffer = temp.pop()

				for line in temp:
					# print(line)
					Loading = self.loadingComplete(line)
			# self.sendMessage("MrDestructoid reporting for duty!")
			print('join room', self.channel, 'success')
			return True
		except:
			print('Join Room Failure')
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

	def disconnect(self):
		self.s.shutdown(socket.SHUT_RDWR)
		self.s.close()
		print('socket shutdown success')