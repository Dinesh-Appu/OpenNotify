
# system packages 
import socket
import threading
import sys
import os
import json
import uuid

# custom models
from .module.module import check_length, load_file, save_file
from .module.exceptions import ServerAuthenticationError
from .module.models import MessageModel
from .module.database import Database

class Server():
	
	def __init__( self, ip:str, port:int):
		self.IP = ip
		self.PORT = port
		self.client_ids: list[str] = []
		self.client_list : list[socket] = []
		self.message_list:dict = {}
		self.app_list:dict = {}
		self.APPNAME:str = None
		self.APPID:str = None
		self.MINIMUM_SIZE:int = 4
		self.MAX_SIZE:int = (1024*100)
		self.ENCODING:str = 'ascii'
		self.DATAFILE:str = os.getcwd()+"/src/data.json"
		self.APPFILE:str = os.getcwd()+"/src/app.json"

		self.model : MessageModel = None
		self.database = Database()


		self.getInfo()

		


	def start(self):
	    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    self.server.bind((self.IP, self.PORT))
	    self.server.listen()

	    if self.model == None:
	    	raise AttributeError("messageModel is 'NoneType'. Set using 'objectName.setModel()'")

	    if self.APPNAME == None:
	    	raise AttributeError("APP Name is 'NoneType'. Set Using 'objectName.generateID()'")

	    if self.APPID == None:
	    	raise AttributeError("APP Id is 'NoneType'. Set Using 'objectName.generateID()'")

	    self.show_info()

	    listen_thread = threading.Thread(target=lambda:self.listener(), daemon =True)
	    listen_thread.start()

	    self.commands(self.server)

	def generateID(self, app_name: str) -> str:
		# Remove Space 
		app_name = app_name.replace(" ","")
		if app_name == "":
			raise AttributeError("App Name is 'NoneType'")
		if app_name in self.app_list.keys():
			raise KeyError("App Name {app_name} Already Exits!")

		id = str(uuid.uuid4())
		self.APPNAME = app_name
		self.APPID = id

		data = { 'app_name': self.APPNAME, 'app_id' : self.APPID }
		save_file(self.DATAFILE, data)

		#self.app_list[app_name] = id
		#save_file(self.APPFILE, self.app_list)
		return id

	def setModel(self, messagemodel:MessageModel) -> None:
		self.model = messagemodel
		#text = f""" CREATE TABEL IF NOT EXITS {tabel_name} VALUES ({}, {})"""
	
	def  show_info(self):
		print(f" Server Ip >> {self.IP} \n Server Port >> {self.PORT} \n App Name >> {self.APPNAME} \n APP ID >> {self.APPID}")

	def getInfo(self) -> dict:
		result = load_file(self.DATAFILE)
		if type(result) == str:
			return result

		self.APPID =  result['app_id']
		self.APPNAME =  result['app_name']

		return result

	def send_msg(self, id:str, message):
	    client = None
	    try:
	        if id in self.client_ids:
	            client_index = self.client_ids.index(id)

	            client = self.client_list[client_index]
	    except IndexError or KeyError:
	        print("Index-Error! ? Key-Error!")
	        return
	    if client == None:
	        print(f"User {id} Not Found") 
	        return

	    try:    
	        message_bytes = json.dumps(message).encode(self.ENCODING)
	        #print(f"Send Message to {id} -> {message_bytes}")
	        length =check_length(message_bytes)
	        client.send(length.encode(self.ENCODING))
	        client.send(message_bytes)

	    except ConnectionResetError:
	        self.client_ids.remove(id)
	        self.client_list.remove(client)
	        print(client, "Removed !")

	def receive_message(self, client):
	    id = ""
	    while True:
	        try:
	            length = int(client.recv(self.MINIMUM_SIZE).decode(self.ENCODING))
	            message = client.recv(length)
	            message_dict = json.loads(message.decode(self.ENCODING))

	            id = message_dict['id']
	            print(message)
	            result = self.database.addMessageDict(message_dict, self.model)
	            if result == "success":
	            	print("added")
	            else:
	            	print(result)
	            
	        except ConnectionResetError:
	            client.close()
	            break
	        except Exception as e:
	            print(f"Error >>> {e} ")  
	        self.check_message(id)  

	def check_message(self, id:str):
	    msg = []
	    if not id:
	    	return
	    print(f"_{id}_")
	    print(f"Checking any Message received for {id}")
	    message_list = self.database.getMessages(id)
	    if type(message_list) == str:
	    	print(message_list)
	    	print(f"No Message for {id}")
	    	return
	    print(f"Message Found for {id} \n message -> {message_list}")
	    for message in message_list:
	    	message = list(message)
	    	m = (message[0], message[2])
	    	message.pop(0)
	    	print(message)
	    	print(f"  ")
	    	try:
	    		self.send_msg(id, message)
	    		msg.append(m)
	    		print(f"Message >>> {message}")
	    	except Exception as e:
	    		print(e)
	    try:
	    	for i in msg:
	    		print(i)
	    		print(self.database.removeMessage(i[1], i[0]))
	    		print(f"Message {i} Removed! ")
	    except KeyError:
	        print(f"User {id} Not Online")

	def listener(self):

	    while True:
	        print("\n Waiting For New Connection.....")
	        client, addrs = self.server.accept()
	        print(f"\n New Client ({addrs}) is Connected ")
	        self.manage(client, addrs)

	def manage(self, client, addrs):
	    try:
	    	auth = client.recv(self.MAX_SIZE).decode(self.ENCODING)

	    	if auth:
	    		auth = auth.split(':')
	    		if not auth[0] == self.APPNAME or not auth[1] == self.APPID:
	    			client.send("NotAuth".encode(self.ENCODING))
	    			client.close()
	    			return
	    		else:
	    			client.send("OK".encode(self.ENCODING))



	    	id = client.recv(self.MAX_SIZE).decode(self.ENCODING)
	    	if not id in self.client_ids:
	    		print(f"USer {id} is Newly Added")
	    		self.client_ids.append(id)
	    		self.client_list.insert(self.client_ids.index(id), client)
	    	else:
	    		print(f"USer {id} is Already Exits")
	    		index = self.client_ids.index(id)
	    		self.client_list[index] = client 
	    		#client.send("Already".encode(ENCODING))
	    	client.send("OK".encode(self.ENCODING))

	    	chaeck_thread = threading.Thread(target=lambda:self.check_message(id), daemon = True)
	    	receive_thread = threading.Thread(target= lambda:self.receive_message(client), daemon = True)

	    	chaeck_thread.start()
	    	receive_thread.start()
	    except ConnectionResetError:
	    	print(f"{client} is Connection Closed!")
	    	return
	    print(f"{client} is DisConnected")

	def commands(self, server):
	    while True:
	        text = input("\n /Server:")
	        text = text.lower()
	        match text:
	            case "":
	                pass
	            case "close" :
	                print("Closing Server...")
	                server.close()
	                server = None
	                break
	                sys.exit()
	                print("Closed !!")
	            case "list id":
	                for id in self.client_ids:
	                    print(id)

	            case "list client":
	                for client in self.client_list:
	                    print(client)
	            case "list":
	                print("list client | list id")

	            case "view":
	                print(self.message_list)
	            case "view data":
	                for id in self.message_list:
	                    print(self.message_list[id])
	            case "view message":
	                for id in self.message_list:
	                    print(id)
	                    for message in self.message_list[id]:
	                        print(message)
	            case "view keys":
	                for key in self.message_list.keys():
	                    print(key)
	            case default:
	                print(f" Invalid Command {text}")



class Client():

	def __init__( self, ip:str, port:int):
		# Variables
		self.IP:str = ip
		self.PORT:int = port
		self.MAX_SIZE:int = (1024*100)
		self.MINIMUM_SIZE:int = 4
		self.ENCODING:str = 'ascii'
		self.APPID:str = None
		self.APPNAME:str = None
		self.ID:str = None

		# Objects
		self.server = ""
		self.receiver = CustomSignal()
		self.model : MessageModel = None




	def start( self) -> None:

		if self.APPID == None:
			raise AttributeError("App Id is 'NoneType'. To set app id use Object(Client).setAppId()")

		if self.APPNAME == None:
			raise AttributeError("App Name is 'NoneType'. To set app id use Object(Client).setAppName()")

		if self.ID == None:
			raise AttributeError(" Id is 'NoneType'. To set app id use Object(Client).setId()")

		if self.model == None:
			raise AttributeError( "MessageModel is 'NoneType'. to set message model use objectName(Client).setModel()")
			
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.server.connect((self.IP, self.PORT))
		except ConnectionRefusedError:
			#print(f" Server {self.IP}:{self.PORT} is Not Found")
			raise ConnectionRefusedError(f" Server {self.IP}:{self.PORT} is Not Found")
		
		receive_thread = threading.Thread(target=lambda:self.receive_message(), daemon= True)

		# client sending id+name for verification you can set id, name by ObjectName.setAppId, ObjectName.setAppName
		self.server.send((self.APPNAME+":"+self.APPID).encode(self.ENCODING))
		respond = self.server.recv(self.MAX_SIZE).decode(self.ENCODING)

		if not respond == "OK":
			print("Respond -> ",respond)
			match respond:
				case "NotAuth":
					raise ServerAuthenticationError("Authentication Failed!")
				case "Not":
					raise Exception("")
				#raise Exception("Error >>> ",respond)

		self.server.send(self.ID.encode(self.ENCODING))
		response = self.server.recv(self.MAX_SIZE).decode(self.ENCODING)
		if not response == 'OK':
			raise ConnectionRefusedError(f"Response is {response}!")

		
		receive_thread.start()

	def sendMessage(self, message) -> None:
		reponse = self.send_message(message)
		if reponse == "Closed":
			raise ConnectionResetError(f" Server {self.IP}:{self.PORT} is Closed! ")

	def setAppName(self, name:str) -> None:
		self.APPNAME = name

	def setAppId(self, id) -> None:
		self.APPID = id

	def setId(self, id) -> None:
		id.replace(" ", "")
		if id == "":
			raise AttributeError("Id is Empty")
		self.ID = id

	def setModel(self, messagemodel:MessageModel) -> None:
		self.model = messagemodel

	def check_message(self, message:dict) -> dict:
		if message['id'] == None:
			raise TypeError("'Id' Is None!")

		if message['to_id'] == None:
			raise TypeError("'To' is None!")

		return message

	def load_model(self, message:list) -> MessageModel:
		self.model.setVariables(self.model, message)
		print(self.model.to_id)


	def send_message(self, message) -> str:
		message = self.check_message(message)
		if message == None:
			raise NoneType("Message Not Send")
		message_bytes = json.dumps(message).encode(self.ENCODING)
		try:
			length = check_length(message_bytes)
			if int(length) > self.MAX_SIZE:
				raise ValueError(f"message Size is To Large, Max Messsage Size is {self.MAX_SIZE} in bytes")
			self.server.send(length.encode(self.ENCODING))
			self.server.send(message_bytes)
			return "Ok"

		except ConnectionResetError:
			print('Server Connection is Closed!')
			return "Closed"

	def receive_message(self) -> None:
		while True:
			try:
				print('Waiting For Receive.....')
				length = int(self.server.recv(self.MINIMUM_SIZE).decode(self.ENCODING))
				message = self.server.recv(length)
				#print("Received Bytes >>",message)

				message_dict = json.loads(message.decode(self.ENCODING))

				#print(f"Message >> {message_dict}")
				self.receiver.emit(message_dict)

			except ConnectionResetError:
				print(f" Server {self.IP}:{self.PORT} Connection is Closed! ")
				break


class CustomSignal():

	def __init__(self):
		self.num : int
		self.trigger_function = None


	def emit(self, text):
		if self.trigger_function == None:
			return

		self.trigger_function(text)


	def connect(self, func):
		self.trigger_function = func






