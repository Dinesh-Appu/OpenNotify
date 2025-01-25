import json
import sys
import os

from .system import getSystemInfo




def load_file(filename:str):
	try:
		check_path(filename)
		with open(filename, 'r') as file: 
			data = json.load(file)
			return data
	except FileNotFoundError:
		print(f"File {filename} Not Found")
		return "Not Found" 
	


def save_file(filename:str, data):
	try:
		check_path(filename)
		file = open(filename, 'w')
		json.dump( data, file, indent= 4)
		file.close()
		return f"File in {filename}"

	except Exception as e:
		print(e)
		return f"ERROR >>> {e}"


def check_path(filename):
	i= 0
	path = ""
	for folder in filename.split('/'):
		i = i+1
		if len(filename.split('/')) == i:
			pass
		elif folder.find(":") == 1:
			if path == "":
				path = folder + "/"
		else:
			path = path + folder+ "/" 
			if not os.path.exists(path):
				os.makedirs(path)

	return path

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


def data_load(data):
	for d in data['@appu']:
		print(d)

def unique_token(appname) -> str:
	#print(dir(system))
	info = json.loads(getSystemInfo())
	text = f"{info['ip-address']}-{appname}-{info['mac-address']}"
	#print(f'{len(text)} -> {text}')
	text = text.replace('.','')
	text = text.replace(':','')
	text = text.replace('-','')
	text = text.lower()
	#print(f'{len(text)} -> {text}')
	newText = ""
	oldText = text
	for t in oldText:

		match t:
			case 'a':
				t = 'k'
			case 'b':
				t = '3'
			case 'c':
				t = 'g'
			case 'd':
				t = '4'
			case 'e':
				t = 'q'
			case 'f':
				t = 'i'
			case 'g':
				t = '1'
			case 'h':
				t = 's'
			case 'i':
				t = 'z'
			case 'j':
				t = '0'
			case 'k':
				t = 'c'
			case 'l':
				t = 'e'
			case 'm':
				t = 'd'
			case 'n':
				t = 'x'
			case 'o':
				t = '5'
			case 'p':
				t = '2'
			case 'q':
				t = 'w'
			case 'r':
				t = 'y'
			case 's':
				t = 'u'
			case 't':
				t = 'p'
			case 'u':
				t = 'v'
			case 'v':
				t = 'b'
			case 'w':
				t = 'n'
			case 'x':
				t = '6'
			case 'y':
				t = 'r'
			case 'z':
				t = 'o'
			case '1':
				t = '7'
			case '2':
				t = 'l'
			case '3':
				t = 'h'
			case '4':
				t = 'm'
			case '5':
				t = 'a'
			case '6':
				t = 'f'
			case '7':
				t = '8'
			case '8':
				t = '9'
			case '9':
				t = 't'
			case '0':
				t = 'j'

		newText = newText + t

	#print(f'{len(oldText)} -> {oldText}')
	#print(f'{len(newText)} -> {newText}')
	return newText
	nos = 0
	num = []
	for x in oldText:
		num.append(x)
		no = newText.count(x)
		if no < 1:
			#print(f"{x} -> {no}")
			... 

	#print('-----------------------------------------------------------------------------')
	#for n in newText:
		#times = newText.count(n)
		#if times > 1:
			#print(f"{num[nos]} -> {n} = {times}")

		#nos += 1


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





if __name__ == '__main__':
	data = {"name": "dinesh", 'pw': "12345678"}
	data = {
    "@appu": [
        {
            "id": "@appu",
            "from": "@dinesh",
            "type": "text",
            "msg": "enna panra"
        },
        {
            "id": "@appu",
            "from": "@dinesh",
            "type": "text",
            "msg": "dfgrde"
        },
        {
            "id": "@appu",
            "from": "@dinesh",
            "type": "text",
            "msg": "edrtgyedy"
        },
        {
            "id": "@appu",
            "from": "@dinesh",
            "type": "text",
            "msg": "erdedyuy"
        },
        {
            "id": "@appu",
            "from": "@dinesh",
            "type": "text",
            "msg": "ryeayerytea"
        },
        {
            "id": "@appu",
            "from": "@dinesh",
            "type": "text",
            "msg": "y5rey"
        }
    ]
}

	filename = "../src/test.json"
	value = data_load(data)
	print(value)

	unique_token('ChatBox')

	#print(check_path('G:/Github/projects/src/.data.json'))



