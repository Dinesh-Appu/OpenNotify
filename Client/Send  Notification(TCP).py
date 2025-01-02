import threading
import socket
import json
import sys

from pydantic import BaseModel



MAX_SIZE:int = (1024*100)
MINIMUM_SIZE:int = 4
ENCODING:str = 'ascii'
ip = '127.0.0.1'
port = 200



class Message(BaseModel):
	id:str
	msg:str
	type:str



def check_length(value):
	length = str(len(value))
	match len(length):
		case 1:
			return f"000{length}"
		case 2:
			return f"00{length}"
		case 3:
			return f"0{length}"
		case 4:
			return f"{length}"


def send_message(server, message):
	try:
		length = check_length(message)
		server.send(length.encode(ENCODING))
		server.send(message)
		return "Ok"

	except ConnectionResetError:
		print('Server Sender Connection is Closed!')
		return "Closed"


def receive_message(server):
	while True:
		try:
			print('Waiting For Receive.....')
			length = int(server.recv(MINIMUM_SIZE).decode(ENCODING))
			message = server.recv(length)
			print("Received Bytes >>",message)

			message_dict = json.loads(message.decode(ENCODING))

			print(f"Message >> {message_dict}")

		except ConnectionResetError:
			print("Server Receiver Connection is Closed!")
			break


def main():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		server.connect((ip, port))
	except ConnectionRefusedError:
		print(" Server is Not Found")
		return
	receive_thread = threading.Thread(target=lambda:receive_message(server), daemon= True)

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
				'type' : 'text',
				'msg' : text
			}
			message_bytes = json.dumps(message).encode(ENCODING)

			reponse = send_message(server, message_bytes)
			if reponse == "Closed":
				break	


if __name__ == '__main__':
	main()






