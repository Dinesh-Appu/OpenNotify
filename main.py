import threading
import json
import sys
import os
import socket 
from PyQt5.QtCore import pyqtSignal as signal

from pydantic import BaseModel

from module.module import check_length, load_file, save_file

client_ids: list[str] = []
client_list : list[socket] = []
message_list = {}

MINIMUM_SIZE:int = 4
MAX_SIZE:int = (1024*100)
ENCODING:str = 'ascii'
DATAFILE:str = os.getcwd()+"/src/data.json"
ip = '127.0.0.1'
port = 200


class Message(BaseModel):
    id:str
    to:str
    msg:str
    type:str

def send_msg(id:str, message:Message):
    global message_list
    client = None
    try:
        if id in client_ids:
            client_index = client_ids.index(id)

            client = client_list[client_index]
    except IndexError or KeyError:
        print("Index-Error! ? Key-Error!")
        return
    if client == None:
        print(f"User {id} Not Found") 
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
    global message_list
    while True:
        try:
            length = int(client.recv(MINIMUM_SIZE).decode(ENCODING))
            message = client.recv(length)
            message_dict = json.loads(message.decode(ENCODING))

            id = message_dict['id']
            try:
                message_list[id].append(message_dict)

            except KeyError:
                message_list[id] = []
                message_list[id].append(message_dict)

            save_file(DATAFILE, message_list)
        except ConnectionResetError:
            client.close()
            break
        except Exception as e:
            print(f"Error >>> {e} ")  
        check_message(id)  

def check_message(id:str):
    global message_list
    msg = []
    message_list = load_file(DATAFILE)
    print(f"Checking any Message received for {id}")
    if id in message_list.keys():
        print(f"Message Found for {id} \n message -> {message_list[id]}")
        print(f"  ")
        try:
            print("list >>> ", message_list[id])
            for message in message_list[id]:
            #for index in range(len(message_list[id])):
                #message = message_list[id][index]
                send_msg(id, message)
                msg.append(message)
                print(f"Message >>> {message}")
                #message_list[id].remove(message)
        except Exception as e:
            print(e)
    try:
        for message in message_list[id]:
            if message in msg:
                message_list[id].remove(message) 
                print(f"Removed Message {message} ")
    except KeyError:
        print(f"User {id} Not Online")
    save_file(DATAFILE, message_list)


def listener(server):

    while True:
        print("\n Waiting For New Connection.....")
        client, addrs = server.accept()
        print(f"\n New Client ({addrs}) is Connected ")
        manage(client, addrs)



def manage(client, addrs):
    global message_list
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
    print(f"{client} is DisConnected")


def commands(server):

    global message_list
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
                save_file(DATAFILE, message_list)
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
            case "view data":
                for id in message_list:
                    print(message_list[id])
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
    global message_list
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    value = load_file(DATAFILE)
    print(type(value), value)
    if type(value) == dict:
        message_list = value
        print("DICT >>>>> ")
    if value == "Not Found":
        save_file(DATAFILE, message_list)
        message_list = load_file(DATAFILE)

    print(message_list)



    listen_thread = threading.Thread(target=lambda:listener(server), daemon =True)
    listen_thread.start()

    commands(server)


if __name__ == '__main__':
    main(ip, port)



