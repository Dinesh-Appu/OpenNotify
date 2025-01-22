import inspect



class MessageModel():

	id: str = None
	to_id: str = None

	def __init__(self):
		#print("message model")
		pass

	# Get All Custom Variables Name
	def getVariablesName(self) -> list:
		items = []
		for var in self.__annotations__:
			items.append(var)

		return items

	# Get All Custom Variables name and value
	def getVariables(self) -> dict:
		items = {}
		for var in inspect.getmembers(self):
			if not var[0].startswith('_'):
				if not inspect.ismethod(var[1]):
					items[var[0]] = var[1]


		return items

	def setVariables(self, items:list) -> None:
		no = 0
		#print(items)
		#var = self.getVariablesName()
		for v in self.__annotations__:
			#print("Vars", v)
			try:
				self.__dict__[v] = items[no]
				#print("Value", items[no])
			except IndexError:
				self.__dict__[v] = None
			#print(f"{v} = {self.__dict__[v]}")
			no+=1

		
		#print(self.__dict__)


	def getVariablesType(self) -> dict:
		value = self.__annotations__
		return value



if __name__ == "__main__":
	class TextMsg(MessageModel):
		id:str = None
		to_id:str = None
		text:str
		view:bool


	msg = TextMsg()
	#msg.text = None
	i = ["dinesh", 'appu', 'hi da', False]
	msg.setVariables(i)

	print(msg.text)
	print(msg.getVariables())

