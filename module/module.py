import json
import sys
import os



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

	#print(check_path('G:/Github/projects/src/.data.json'))



