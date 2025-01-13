import socket
import threading
import sys
import os
import json

from module.module import check_length, load_file, save_file


class Server():
	
	def __init__( self, ip:str, port:int):
		self.IP = ip
		self.PORT = port
		self.client_ids: list[str] = []
		self.client_list : list[socket] = []
		self.message_list = {}

		self.MINIMUM_SIZE:int = 4
		self.MAX_SIZE:int = (1024*100)
		self.ENCODING:str = 'ascii'
		self.DATAFILE:str = os.getcwd()+"/src/data.json"


	def start(self):
	    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    self.server.bind((self.IP, self.PORT))
	    self.server.listen()

	    value = load_file(self.DATAFILE)
	    print(type(value), value)
	    if type(value) == dict:
	        self.message_list = value
	        print("DICT >>>>> ")
	    if value == "Not Found":
	        save_file(self.DATAFILE, self.message_list)
	        self.message_list = load_file(self.DATAFILE)

	    print(self.message_list)



	    listen_thread = threading.Thread(target=lambda:listener(self.server), daemon =True)
	    listen_thread.start()

	    commands(self.server)


	def send_msg(self, id:str, message:Message):
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
	        manage(client, addrs)



	def manage(self, client, addrs):
	    try:
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
		self.IP = ip
		self.PORT = port

		self.MAX_SIZE:int = (1024*100)
		self.MINIMUM_SIZE:int = 4
		self.ENCODING:str = 'ascii'
		self.server = ""





	def start( self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.server.connect((self.IP, self.PORT))
		except ConnectionRefusedError:
			print(f" Server {self.IP}:{self.PORT} is Not Found")
			return
		receive_thread = threading.Thread(target=lambda:self.receive_message(), daemon= True)

		while True:
			name = '@'+input("Enter Id :")
			if not name == "":
				break


		self.server.send(name.encode(self.ENCODING))
		respond = self.server.recv(MAX_SIZE).decode(self.ENCODING)

		if not respond == "OK":
			print(respond)
			return
		
		receive_thread.start()

		while True:
			to_name = "@"+input("Message to(id):")
			if not to_name == "":
				break

		while True:
			text = input(f"{name}:")
			if not text == "":
				message = {
					'id' : to_name,
					'from' : name,
					'type' : 'text',
					'msg' : text
				}
				reponse = send_message(message)
				print(reponse)
				if reponse == "Closed":
					break	



	def setmessage(message:dict):
		if message['id'] == None:
			raise TypeError("Id Is None!")

		if message['from'] == None:
			raise TypeError("Fron is None!")

		return message


	def send_message(message):
		message = self.setmessage(message)
		if message == None:
			raise NoneType("Message Not Send")
		message_bytes = json.dumps(message).encode(self.ENCODING)
		try:
			length = check_length(message_bytes)
			self.server.send(length.encode(self.ENCODING))
			self.server.send(message_bytes)
			return "Ok"

		except ConnectionResetError:
			print('Server Sender Connection is Closed!')
			return "Closed"


	def receive_message():
		while True:
			try:
				print('Waiting For Receive.....')
				length = int(self.server.recv(self.MINIMUM_SIZE).decode(self.ENCODING))
				message = server.recv(length)
				#print("Received Bytes >>",message)

				message_dict = json.loads(message.decode(self.ENCODING))

				print(f"Message >> {message_dict}")

			except ConnectionResetError:
				print("Server Receiver Connection is Closed!")
				break

