
import sqlite3
import os
from typing import Optional



from .models import MessageModel
from .module import check_path


class Database:
	
	def __init__(self):
		self._PATH = os.getcwd()+"/src/database.db"

		check_path(self._PATH)

		self._FILE = sqlite3.connect(self._PATH, check_same_thread = False)
		self._DB = self._FILE.cursor()
		message = MessageModel()

		#
		text = """ CREATE TABLE IF NOT EXISTS Notifications ( No INTEGER PRIMARY KEY AUTOINCREMENT,
						id 	TEXT NOT NUll,
						title TEXT ,
						body TEXT NOT NULL,
						image TEXT DEFAULT NULL ,
						icon TEXT ,
						sound TEXT ,
						action TEXT ,
						token TEXT NOT NULL ,
						appid TEXT NOT Null
						) """
		print(self._add_data(text))
		text = """ CREATE TABLE IF NOT EXISTS Users ( No INTEGER PRIMARY KEY AUTOINCREMENT,
						id TEXT NOT Null UNIQUE,
						token TEXT NOT NuLL UNiQUE,
						expire_date TEXT(10) NOT NULL )"""
		print(self._add_data(text))
		#self._create_tabel("Notifications", message.getVariablesType())
		#self._create_tabel("Users", { 'id' : str, 'token' : str, 'expire_date' : str })



	def _add_data(self, text) -> str:
		try:
			self._DB.execute(text)
			self._FILE.commit()
			return "success"
		except Exception as e:
			return f"Error >> {e}"

	def _get_data(self, text) -> list|str:
		try:
			self._DB.execute(text)
			data = self._DB.fetchall()
			self._FILE.commit()
			return data
		except Exception as e:
			return f"Error >> {e}" 

	def _create_tabel(self, tabelname:str, columns:dict|list) -> str:
		text = f""" CREATE TABLE IF NOT EXISTS {tabelname} ( No INTEGER PRIMARY KEY AUTOINCREMENT"""
		t = ""
		if columns == dict:
			for item in columns:
				if columns[item] == str:
					t = "TEXT"
				elif columns[item] == str:
					t = "INTEGER"
				elif columns[item] == str:
					t = "FLOAT"
				elif columns[item] == str:
					t = "BOOLEAN"
				print(columns[item])
				text = text + f", {item} {t} "
		else:
			for item in columns:
				if type(item) == str:
					t = "TEXT"
				elif type(item) == str:
					t = "INTEGER"
				elif type(item) == str:
					t = "FLOAT"
				elif type(item) == str:
					t = "BOOLEAN"
				text = text + f", {item} {t} "

		text = text + ")"

		#print(text, "\n")
		self._add_data(text)


	def addMessage(self, message:MessageModel|dict) -> str:
		if type(message) == MessageModel:
			data = message.getVariables()
		else:
			data = message

		text = """  INSERT INTO Notifications ( """
		table = ""
		value = ""
		for t in data:
			if table == "":
				table = t
			else:
				table = table + f", {t}"

		text = text + table + ") VALUES ("
		for v in data:
			if value == "":
				if not data[v]:
					value = """ Null """
				elif type(data[v]) == str:
					value = f""" "{data[v]}" """
				else:
					value = data[v]

			else:
				if not data[v]:
					value = value + """, Null """
				elif type(data[v]) == str:
					value = value + f""", "{data[v]}" """
				else:
					value = value + f", {data[v]}"


		text = text + value + ")"
		#print(text)
		return self._add_data(text)

	def addUser(self, id:str, token:str, expire_date:str) -> str:

		text = f""" INSERT INTO Users (id, token, expire_date) VALUES ("{id}", "{token}", "{expire_date}" )"""

		return self._add_data(text)


	def getMessages(self, id:Optional[str] = None) -> list|str:
		text = ""
		if id:
			text = f""" SELECT * FROM Notifications WHERE id = "{id}" """
		else:
			text = """ SELECT * FROM Notifications """
		response = self._get_data(text)
		#print(type(respose))

		return response

	def getUser(self, id: Optional[str] = None) -> list|str :
		if id:
			text = f""" SELECT * FROM Users WHERE id = "{id}" """
		else:
			text = """ SELECT * FROM Users """

		response = self._get_data(text)

		return response

	def deleteMessage(self, no:int) -> str:
		text = F""" DELETE FROM Notifications WHERE No = {no} """
		return self._add_data(text)

	def deleteUser(self, id:str) -> str:
		text = f"""  DELETE FROM Users WHERE id = "{id}" """
		return self._add_data(text)


if __name__ == '__main__':
	data = Database()
	message = MessageModel()
	message.id = "@dinesh"
	message.body = "hi da"
	message.token = "42341rfgtregtgt"
	message.appid = "42341rfgtregtgt"

	print(data.addMessage(message))
	value = data.getMessages('@appu')
	#print(dir(value))
	if type(value) == str:
		print(value)
	elif len(value) == 0:
			print("No message")
	else:
		for v in value:
			print(value)


	print(data.addUser('@appu1', 'rf;lergerdgertyhiuh9gertgergg', '28/01/2025'))
	print(data.deleteUser('@appu'))

