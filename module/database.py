# pip install package


# System package
import sqlite3
import os

# custom package
import MessageModel
from exception import DatabaseError


class Database:
	
	def __init__(self):
		self.PATH = os.getcwd() + "./src/tada.db"
		self.FILE = sqlite3.connect(self.PATH)
		self.db = self.FILE.cursor()
		#print(dir(self.db))

	def addData(self, text) -> str:
		try:
			self.db.execute(text)
			return 'success'

		except Exception as e:
			return e


	def getData(self) -> str|dict:
		try:
			self.db.execute(text)
			data = self.db.fetchall()
			return data
		except Exception as e:
			return "Error: "+e

	def createTabel(self) -> str:
		try:
			self.db.execute(text)



if __name__ == '__main__':
	database = Database()

