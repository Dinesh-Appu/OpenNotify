import threading
import socket
import json
import sys

from pydantic import BaseModel

from module.module import check_length, load_file, save_file 


MAX_SIZE:int = (1024*100)
MINIMUM_SIZE:int = 4
ENCODING:str = 'ascii'
server = ""



class Message(BaseModel):
	id:str
	msg:str
	type:str

def setmessage(message:dict):
	if message['id'] == None:
		raise TypeError("Id Is None!")

	if message['from'] == None:
		raise TypeError("Fron is None!")

	return message


def send_message(message):
	global server
	message = setmessage(message)
	if message == None:
		raise NoneType("Message Not Send")
	message_bytes = json.dumps(message).encode(ENCODING)
	try:
		length = check_length(message_bytes)
		server.send(length.encode(ENCODING))
		server.send(message_bytes)
		return "Ok"

	except ConnectionResetError:
		print('Server Sender Connection is Closed!')
		return "Closed"


def receive_message():
	global server
	while True:
		try:
			print('Waiting For Receive.....')
			length = int(server.recv(MINIMUM_SIZE).decode(ENCODING))
			message = server.recv(length)
			#print("Received Bytes >>",message)

			message_dict = json.loads(message.decode(ENCODING))

			print(f"Message >> {message_dict}")

		except ConnectionResetError:
			print("Server Receiver Connection is Closed!")
			break

def SetClient( ip, port):
	main(ip, port)

def main(ip, port):
	global server
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		server.connect((ip, port))
	except ConnectionRefusedError:
		print(" Server is Not Found")
		return
	receive_thread = threading.Thread(target=lambda:receive_message(), daemon= True)

	while True:
		name = '@'+input("Enter Id :")
		if not name == "":
			break


	server.send(name.encode(ENCODING))
	respond = server.recv(MAX_SIZE).decode(ENCODING)

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


if __name__ == '__main__':
	main('127.0.0.1', 200)






