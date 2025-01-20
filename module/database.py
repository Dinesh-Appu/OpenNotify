# pip install package


# System package
import sqlite3
import os

# custom package
from .models import MessageModel
from .exceptions import DatabaseError


class Database:
	
	def __init__(self):
		self.PATH = os.getcwd() + "./src/data.db"
		self.FILE = sqlite3.connect(self.PATH, check_same_thread=False)
		self.db = self.FILE.cursor()
		#print(dir(self.db))

	def addData(self, text) -> str:
		try:
			self.db.execute(text)
			self.FILE.commit()
			return 'success'

		except Exception as e:
			return f"Add Error >> {e}"


	def getData(self, text) -> str|dict:
		try:
			self.db.execute(text)
			data = self.db.fetchall()
			self.FILE.commit()
			return data
		except Exception as e:
			return f"Get Error: {e}"

	def createTabel(self, messagemodel:MessageModel) -> str:
		data = messagemodel.getVariablesType(messagemodel)
		tabels = ""
		types = ""
		tabelname = messagemodel.id
		for item in data:

			if data[item] == str:
				types = "TEXT"
			elif data[item] == int:
				types = "INT"
			elif data[item] == float:
				types = "FLOAT"
			elif data[item] == bool:
				types = "BOOLEAN"
			#elif data[item] == :
			#	types = "INT"
			else:
				print(data[item])

			#print(item, types)
			if tabels == "":
				tabels = f"{item} {types}"
			else:
				tabels = f"{tabels},\n {item} {types}"


		#print(tabels)

		text = f"""CREATE TABLE IF NOT EXISTS {tabelname}(\n num INTEGER PRIMARY KEY AUTOINCREMENT,\n {tabels}) """
		#print(text)
		result = self.addData(text)
		self.FILE.commit()

		return "Create "+ result 

	def addMessage(self, messagemodel:MessageModel) -> str:
		data = messagemodel.getVariables()
		tabels = []
		values = []
		text = " INSERT INTO ("
		tabelname = messagemodel.id
		for item in data:
			tabels.append(item)
			values.append(data[item])
			text = text + item
		text = text + ") VALUES ("
		for v in values:
			text = text + v
		text = text + ")"

		result = self.createTabel(messagemodel)
		if result == 'Create success':
			#text = f""" INSERT INTO {tabelname} ({tabels}) VALUES({values}) """
			print(text)
			result = self.addData(text)
			self.FILE.commit()
			return result

		self.FILE.commit()
		return  result

	def addMessageDict(self, message:dict, messagemodel:MessageModel) -> str:
		tabels = []
		values = []
		text = ""
		tabelname = message['id']
		messagemodel.id = tabelname
		messagemodel.to_id = message['to_id']
		result = self.createTabel(messagemodel)
		for i in message:
			tabels.append(i)
			values.append(message[i])
			if text == "":
				text = f" INSERT INTO {tabelname} (" + i
			else:
				text = text + ","+ i

		text = text + ") VALUES ("
		com = False
		for v in values:
			if not com:
				if type(v) == str:
					text = text + """ "{}" """.format(v)
				else:
					text = text + v
				com = True
			else:
				if type(v) == str:
					text = text+ "," + """ "{}" """.format(v)
				else:
					text = text+ "," + v

			

		text = text + ")"

		#text = F""" INSERT INTO {tabelname} ({tabels}) VALUES({values}) """
		#print(text)
		if result == 'Create success':
			self.FILE.commit()
			return self.addData(text)

		self.FILE.commit()
		return result



	def getMessages(self, id) -> str|list:
		text = f""" SELECT * FROM {id} 		       """
		result = self.getData(text)
		self.FILE.commit()
		return result




if __name__ == '__main__':
	database = Database()

