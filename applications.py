import socket
import threading
import sys
import os
import json
import uuid

from  PyQt5.QtCore import QObject, pyqtSignal
from .module.module import check_length, load_file, save_file


class Server():
	
	def __init__( self, ip:str, port:int):
		self.IP = ip
		self.PORT = port
		self.client_ids: list[str] = []
		self.client_list : list[socket] = []
		self.message_list:dict = {}
		self.app_list:dict = {}

		self.MINIMUM_SIZE:int = 4
		self.MAX_SIZE:int = (1024*100)
		self.ENCODING:str = 'ascii'
		self.DATAFILE:str = os.getcwd()+"./src/data.json"
		self.APPFILE:str = os.getcwd()+"./src/app.json"


	def start(self):
	    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    self.server.bind((self.IP, self.PORT))
	    self.server.listen()

	    value = load_file(self.DATAFILE)
	    if type(value) == dict:
	        self.message_list = value
	    if value == "Not Found":
	        save_file(self.DATAFILE, self.message_list)
	        self.message_list = load_file(self.DATAFILE)
	        print(self.DATAFILE)

	    apps = load_file(self.APPFILE)
	    if type(apps) == dict:
	        self.app_list = apps
	    if apps == "Not Found":
	    	self.app_list = {}
	    	save_file(self.APPFILE, self.app_list)


	    listen_thread = threading.Thread(target=lambda:self.listener(), daemon =True)
	    listen_thread.start()

	    self.commands(self.server)

	def getarateID(app_name: str) -> str:
		# Remove Space 
		app_name = app_name.replace(" ","")
		if app_name == "":
			raise AttributeError("App Name is 'NoneType'")
		if app_name in self.app_list.keys():
			raise KeyError("App Name {app_name} Already Exits!")

		id = uuid.uuid4()
		self.app_list[app_name] = id
		save_file(self.APPFILE, self.app_list)
		return id



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
	        print(f"Send Message to {id, client}")
	        message_bytes = json.dumps(message).encode(self.ENCODING)
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
	            try:
	                self.message_list[id].append(message_dict)

	            except KeyError:
	                self.message_list[id] = []
	                self.message_list[id].append(message_dict)

	            save_file(self.DATAFILE, self.message_list)
	        except ConnectionResetError:
	            client.close()
	            break
	        except Exception as e:
	            print(f"Error >>> {e} ")  
	        self.check_message(id)  

	def check_message(self, id:str):
	    msg = []
	    self.message_list = load_file(self.DATAFILE)
	    print(f"Checking any Message received for {id}")
	    if id in self.message_list.keys():
	        print(f"Message Found for {id} \n message -> {self.message_list[id]}")
	        print(f"  ")
	        try:
	            print("list >>> ", self.message_list[id])
	            for message in self.message_list[id]:
	            #for index in range(len(message_list[id])):
	                #message = message_list[id][index]
	                send_msg(id, message)
	                msg.append(message)
	                print(f"Message >>> {message}")
	                #message_list[id].remove(message)
	        except Exception as e:
	            print(e)
	    try:
	        for message in self.message_list[id]:
	            if message in msg:
	                self.message_list[id].remove(message) 
	                print(f"Removed Message {message} ")
	    except KeyError:
	        print(f"User {id} Not Online")
	    save_file(self.DATAFILE, self.message_list)

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
	    		if not auth[0] in self.app_list.keys() or not auth[1] in self.app_list.values():
	    			client.send("NotAuth".encode(self.ENCODING))
	    			client.close()
	    			return



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
	        text = input("/Server:")
	        text = text.lower()
	        match text:
	            case "":
	                pass
	            case "close" :
	                print("Closing Server...")
	                server.close()
	                server = None
	                save_file(self.DATAFILE, self.message_list)
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
		self.APP_ID:str
		self.APP_NAME:str

		# Objects
		self.server = ""
		self.receiver = CustomSignal()




	def start( self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.server.connect((self.IP, self.PORT))
		except ConnectionRefusedError:
			#print(f" Server {self.IP}:{self.PORT} is Not Found")
			raise ConnectionRefusedError(f" Server {self.IP}:{self.PORT} is Not Found")
		receive_thread = threading.Thread(target=lambda:self.receive_message(), daemon= True)

		if self.APP_ID == None:
			raise AttributeError("App Name is 'NoneType'. To set app id use Object(Client).setAppId")

		if self.APP_NAME == None:
			raise AttributeError("App Name is 'NoneType'. To set app id use Object(Client).setAppName")

		# client sending id+name for verification you can set id, name by ObjectName.setAppId, ObjectName.setAppName
		self.server.send((self.APP_ID+":"+self.APP_NAME).encode(self.ENCODING))
		respond = self.server.recv(self.MAX_SIZE).decode(self.ENCODING)

		if not respond == "OK":
			print(respond)
			match respond:
				case "NotAuth":
					raise ServerAuthenticationError("Authentication Failed!")
				case "Not":
					raise Exception("")
				#raise Exception("Error >>> ",respond)

		
		receive_thread.start()

	def sendMessage(self, message):
		reponse = self.send_message(message)
		if reponse == "Closed":
			raise ConnectionResetError(" Server {self.IP}:{self.PORT} is Closed! ")

	def setAppName(self, name:str) -> None:
		self.APP_NAME = name

	def setAppId(self, id):
		self.APP_ID = id


	def check_message(self, message:dict):
		if message['id'] == None:
			raise TypeError("Id Is None!")

		if message['from'] == None:
			raise TypeError("Fron is None!")

		return message

	def send_message(self, message):
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

	def receive_message(self):
		while True:
			try:
				print('Waiting For Receive.....')
				length = int(self.server.recv(self.MINIMUM_SIZE).decode(self.ENCODING))
				message = server.recv(length)
				#print("Received Bytes >>",message)

				message_dict = json.loads(message.decode(self.ENCODING))

				#print(f"Message >> {message_dict}")
				self.receiver.emit(message_dict)

			except ConnectionResetError:
				print("Server Receiver Connection is Closed!")
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






