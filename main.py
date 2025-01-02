import threading
import json
import sys
import socket

from pydantic import BaseModel


client_ids: list[str] = []
client_list : list[socket] = []
message_list = {}

MINIMUM_SIZE:int = 4
MAX_SIZE:int = (1024*100)
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

def send_msg(id:str, message:Message):
	client = None
	try:
		if id in client_ids:
			client_index = client_ids.index(id)

			client = client_list[client_index]
	except IndexError or KeyError:
		print("IndexError! or KeyError!")
		return


	try:	
		print(f"Send Message to {id, client}")
		message_bytes = json.dumps(message).encode(ENCODING)
		length =check_length(message_bytes)
		client.send(length.encode(ENCODING))
		client.send(message_bytes)

	except ConnectionResetError:
		client_ids.remove(id)
		client_list.remove(client)
		print(client, "Removed !")

def receive_message(client):
	while True:
		try:
			length = int(client.recv(MINMUM_SIZE).decode(ENCODING))
			message = client.recv(length)
			message_dict = json.loads(message.decode(ENCODING))

			id = message_dict['id']
			try:
				message_list[id].append(message_dict)

			except KeyError:
				message_list[id] = []
				message_list[id].append(message_dict)
		except ConnectionResetError:
			client.close()
			break


def check_message(id:str):
	print(f"Checking any Message received for {id}")
	if id in message_list.keys():
		print(f"Message Found for {id}")
		try:
			for message in message_list[id]:
				send_msg(id, message)
				message_list[id].remove(message)
		except Exception as e:
			print(e)


def listener(server):

	while True:
		print("\n Waiting For New Connection.....")
		client, addrs = server.accept()
		print(f"\n New Client ({addrs}) is Connected ")
		manage(client, addrs)



def manage(client, addrs):

	try:
		id = client.recv(MAX_SIZE).decode(ENCODING)
		if not id in client_ids:

			print(f"USer {id} is Newly Added")
			client_ids.append(id)
			client_list.insert(client_ids.index(id), client)
		else:
			print(f"USer {id} is Already Exits")
			index = client_ids.index(id)
			client_list[index] = client 
			#client.send("Already".encode(ENCODING))
		client.send("OK".encode(ENCODING))
		
		chaeck_thread = threading.Thread(target=lambda:check_message(id), daemon = True)
		receive_thread = threading.Thread(target= lambda:receive_message(client), daemon = True)

		chaeck_thread.start()
		receive_thread.start()
	except ConnectionResetError:
		print(f"{client} is Connection Closed!")
		return
	except ConnectionAbortedError:
		print(f"{client} is DisConnected")

def commands(server):
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
				break
				sys.exit()
				print("Closed !!")
			case "list id":
				for id in client_ids:
					print(id)

			case "list client":
				for client in client_list:
					print(client)
			case "list":
				print("list client | list id")
			case "view":
				print(message_list)
			case "view message":
				for id in message_list:
					print(id)
					for message in message_list[id]:
						print(message)
			case "view keys":
				for key in message_list.keys():
					print(key)
			case default:
				print(f" Invalid Command {text}")

 
def main(host, port):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((host, port))
	server.listen()



	listen_thread = threading.Thread(target=lambda:listener(server), daemon =True)
	listen_thread.start()

	commands(server)


if __name__ == '__main__':
	main(ip, port)



