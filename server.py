
# system packages 
import socket
import threading
import sys
import os
import json
import uuid

# custom modules
from .module.module import check_length, check_path, load_file, save_file
from .module.exceptions import ServerAuthenticationError, ServerNotConnectedError
from .module.models import MessageModel
from .module.database import Database




class Server():
	
	def __init__( self, ip:str, port:int):
		self._IP = ip
		self._PORT = port
		self._client_ids: list[str] = []
		self._client_list : list[socket] = []
		self._message_list:dict = {}
		self._message_list:dict = {}
		self._APPNAME:str = None
		self._APPID:str = None
		self._MINIMUM_SIZE:int = 4
		self._MAXIMUM_SIZE:int = (1024*100)
		self._ENCODING:str = 'ascii'
		self._DATAFILE:str = os.getcwd()+"/src/data.json"
		self._APPFILE:str = os.getcwd()+"/src/app.json"

		self._getInfo()

		self._model : MessageModel = MessageModel()
		self._database = Database()



		


	def start(self):
	    self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    self._server.bind((self._IP, self._PORT))
	    self._server.listen()

	    if self._APPNAME == None:
	    	raise AttributeError("APP Name is 'NoneType'. Set Using 'objectName.generateID()'")

	    if self._APPID == None:
	    	raise AttributeError("APP Id is 'NoneType'. Set Using 'objectName.generateID()'")

	    self._show_info()

	    listen_thread = threading.Thread(target=lambda:self._listener(), daemon =True)
	    listen_thread.start()

	    self._commands(self._server)

	def generateID(self, app_name: str) -> str:
		# Remove Space 
		app_name = app_name.replace(" ","")
		if app_name == "":
			raise AttributeError("App Name is 'NoneType'")
		if app_name in self._message_list.keys():
			raise KeyError("App Name {app_name} Already Exits!")

		id = str(uuid.uuid4())
		self._APPNAME = app_name
		self._APPID = id

		data = { 'app_name': self._APPNAME, 'app_id' : self._APPID }
		save_file(self._DATAFILE, data)

		#self._message_list[app_name] = id
		#save_file(self._APPFILE, self._message_list)
		return id

	
	def _getInfo(self) -> dict:
		result = load_file(self._DATAFILE)
		if type(result) == str:
			return result

		if not os.path.exists(os.getcwd()+'./src/'):
			os.makedir(os.getcwd()+'./src/')

		self._APPID =  result['app_id']
		self._APPNAME =  result['app_name']

		return result


	def  _show_info(self):
		print(f" Server Ip >> {self._IP} \n Server Port >> {self._PORT} \n App Name >> {self._APPNAME} \n APP ID >> {self._APPID}")

	def _send_msg(self, id:str, message):
	    client = None
	    try:
	        if id in self._client_ids:
	            client_index = self._client_ids.index(id)

	            client = self._client_list[client_index]
	    except IndexError or KeyError:
	        print("Index-Error! ? Key-Error!")
	        return "KeyError"
	    if client == None:
	        print(f"User {id} Not Found") 
	        return "Not Found"

	    try:    
	        message_bytes = json.dumps(message).encode(self._ENCODING)
	        #print(f"Send Message to {id} -> {message_bytes}")
	        length =check_length(message_bytes)
	        client.send(length.encode(self._ENCODING))
	        client.send(message_bytes)
	        return "success"

	    except ConnectionResetError:
	        self._client_ids.remove(id)
	        self._client_list.remove(client)
	        print(client, "Removed !")
	        return "Not Online"

	def _receive_message(self, client, id):
	    while True:
	        try:
	            length = int(client.recv(self._MINIMUM_SIZE).decode(self._ENCODING))
	            message = client.recv(length)
	            message_dict = json.loads(message.decode(self._ENCODING))

	            #id = message_dict['id']
	            print(message_dict)
	            result = self._database.addMessage(message_dict)
	            if result == "success":
	            	print("added")
	            else:
	            	print(result)
	            
	        except ConnectionResetError:
	            client.close()
	            break
	        except Exception as e:
	            print(f"Error >>> {e} ")  
	        self._check_message(message_dict['id'])  

	def _check_message(self, id:str):
	    msg = []
	    if not id:
	    	return
	    print(f"_{id}_")
	    print(f"Checking any Message received for {id}")
	    message_list = self._database.getMessages(id)
	    if type(message_list) == str:
	    	if message_list.find("no such table") < 0:
	    		print(f"No Message for {id}")
	    	else:
	    		print(message_list)
	    	return
	    if len(message_list) == 0:
	    	return
	    print(f"Message Found for {id} \n message -> {message_list}")
	    for message in message_list:
	    	message = list(message)
	    	m = (message[0], message[1], message[3])
	    	message.pop(0)
	    	print(message)
	    	print(f"  ")
	    	try:
	    		response = self._send_msg(id, message)
	    		if response and response == "Not Found" or response == "Not Online":
	    			break
	    		else:
	    			msg.append(m)
	    			print(f"Message >>> {message}")
	    	except Exception as e:
	    		print(e)
	    try:
	    	for i in msg:
	    		print(self._database.deleteMessage(i[0]))
	    		print(f"Message {i[0]} Removed! ")
	    except KeyError:
	        print(f"User {id} Not Online")

	def _listener(self):

	    while True:
	        print("\n Waiting For New Connection.....")
	        client, addrs = self._server.accept()
	        print(f"\n New Client ({addrs}) is Connected ")
	        self._manage(client, addrs)

	def _manage(self, client, addrs):
	    try:
	    	auth = client.recv(self._MAXIMUM_SIZE).decode(self._ENCODING)

	    	if auth:
	    		#auth = auth.split(':')
	    		if not auth == self._APPID:
	    			client.send("NotAuth".encode(self._ENCODING))
	    			client.close()
	    			return
	    		else:
	    			client.send("OK".encode(self._ENCODING))



	    	id = client.recv(self._MAXIMUM_SIZE).decode(self._ENCODING)
	    	if not id in self._client_ids:
	    		print(f"USer {id} is Newly Added")
	    		self._client_ids.append(id)
	    		self._client_list.insert(self._client_ids.index(id), client)
	    	else:
	    		print(f"USer {id} is Already Exits")
	    		index = self._client_ids.index(id)
	    		self._client_list[index] = client 
	    		#client.send("Already".encode(ENCODING))
	    	client.send("OK".encode(self._ENCODING))

	    	chaeck_thread = threading.Thread(target=lambda:self._check_message(id), daemon = True)
	    	receive_thread = threading.Thread(target= lambda:self._receive_message(client, id), daemon = True)

	    	chaeck_thread.start()
	    	receive_thread.start()
	    except ConnectionResetError:
	    	print(f"{client} is Connection Closed!")
	    	return
	    print(f"{client} is DisConnected")

	def _commands(self, server):
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
	                for id in self._client_ids:
	                    print(id)

	            case "list client":
	                for client in self._client_list:
	                    print(client)
	            case "list":
	                print("list client | list id")

	            case "view":
	                print(self._message_list)
	            case "view data":
	                for id in self._message_list:
	                    print(self._message_list[id])
	            case "view message":
	                for id in self._message_list:
	                    print(id)
	                    for message in self._message_list[id]:
	                        print(message)
	            case "view keys":
	                for key in self._message_list.keys():
	                    print(key)
	            case default:
	                print(f" Invalid Command {text}")




