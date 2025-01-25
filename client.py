
# system packages 
import socket
import threading
import sys
import os
import json
import uuid

# custom modules
from .module.module import check_length, check_path, load_file, save_file, unique_token
from .module.exceptions import ServerAuthenticationError, ServerNotConnectedError
from .module.models import MessageModel
from .module.database import Database
from .module.module import CustomSignal


class Client():

	def __init__( self, ip:str, port:int):
		# Variables
		self._IP:str = ip
		self._PORT:int = port
		self._MAXIMUM_SIZE:int = (1024*100)
		self._MINIMUM_SIZE:int = 4
		self._ENCODING:str = 'ascii'
		self._APPID:str = None
		self._TOKEN:str = None
		self.ID:str = None

		# Objects
		self.server = ""
		self.receiver = CustomSignal()
		self._model : MessageModel = MessageModel()


	# Public Function

	def start( self) -> None:

		if self._APPID == None:
			raise AttributeError("App Id is 'NoneType'. To set app id use Object(Client).setAppId()")

		if self.ID == None:
			raise AttributeError(" Id is 'NoneType'. To set app id use Object(Client).setId()")

		if self._TOKEN == None:
			self._TOKEN = unique_token("OpenNotify")
			#raise AttributeError("Token is 'NoneType'. To set app id use Object(Client).setToken")

		if self._model == None:
			raise AttributeError( "MessageModel is 'NoneType'. to set message model use objectName(Client).setModel()")
			
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.server.connect((self._IP, self._PORT))
		except ConnectionRefusedError:
			#print(f" Server {self._IP}:{self._PORT} is Not Found")
			raise ConnectionRefusedError(f"Server {self._IP}:{self._PORT} is Not Found")
		
		receive_thread = threading.Thread(target=lambda:self._receive_message(), daemon= True)

		# client sending id+name for verification you can set id, name by ObjectName.setAppId, ObjectName.setAppName
		self.server.send((self._APPID).encode(self._ENCODING))
		respond = self.server.recv(self._MAXIMUM_SIZE).decode(self._ENCODING)

		if not respond == "OK":
			print("Respond -> ",respond)
			match respond:
				case "NotAuth":
					raise ServerAuthenticationError("Authentication Failed!")
				case "Not":
					raise Exception("")
				#raise Exception("Error >>> ",respond)

		self.server.send(self.ID.encode(self._ENCODING))
		response = self.server.recv(self._MAXIMUM_SIZE).decode(self._ENCODING)
		if not response == 'OK':
			raise ConnectionRefusedError(f"Response is {response}!")

		
		receive_thread.start()
		
	def setAppId(self, id:str) -> None:
		if id == None:
			raise AttributeError("Enter Value App Id Id 'NoneType'")
		self._APPID = id

	def setToken(self, tokem:str) -> None:
		if tokem == None:
			raise AttributeError("Enter Value Token is 'NoneType'")
		self._TOKEN = tokem

	def setId(self, id) -> None:
		if id == None:
			raise AttributeError("Enter Value Id is 'NoneType'")

		#id.replace(" ", "")
		#if id == "":
			raise AttributeError("Id is Empty")
		self.ID = id

	def sendMessage(self, message:MessageModel) -> None:
		message.token = self._TOKEN
		message.appid = self._APPID
		msg = message.getVariables()
		response = self._send_message(msg)
		if response == "Closed":
			raise ConnectionResetError(f"Server {self._IP}:{self._PORT} is Closed! ")
		elif response == "NotConnected":
			raise ServerNotConnectedError(f"Not Connected to Server!")
		return True

	# Private Function

	def _check_message(self, message:dict) -> dict:
		if message['id'] == None:
			raise TypeError("'Id' Is None!")

		if message['body'] == None:
			raise TypeError("'Body' is None!")

		return message

	def _load_model(self, message:list) -> MessageModel:
		mod = self._model
		mod.setVariables( message)
		return mod

	def _send_message(self, message) -> str:
		message = self._check_message(message)
		if message == None:
			raise NoneType("Message Not Send")
		message_bytes = json.dumps(message).encode(self._ENCODING)
		try:
			length = check_length(message_bytes)
			if int(length) > self._MAXIMUM_SIZE:
				raise ValueError(f"message Size is To Large, Max Messsage Size is {self._MAXIMUM_SIZE} in bytes")
			self.server.send(length.encode(self._ENCODING))
			self.server.send(message_bytes)
			return "Ok"

		except ConnectionResetError:
			return "Closed"
		except OSError:
			return "NotConnected"

	def _receive_message(self) -> None:
		while True:
			try:
				print('Waiting For Receive.....')
				length = int(self.server.recv(self._MAXIMUM_SIZE).decode(self._ENCODING))
				message = self.server.recv(length)
				#print("Received Bytes >>",message)

				message_dict = json.loads(message.decode(self._ENCODING))
				
				#print(f"Message >> {message_dict}")
				self.receiver.emit(self._load_model(message_dict))

			except ConnectionResetError:
				print(f" Server {self._IP}:{self._PORT} Connection is Closed! ")
				break

