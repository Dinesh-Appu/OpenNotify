import inspect



class MessageModel():

	id: str = None
	to_id: str = None

	def __init__(self):
		print("message model")

	# Get All Custom Variables Name
	def getVariabelsName(self) -> list:
		for var in self.__annotations__:
			items.append(var)

		return items

	# Get All Custom Variables name and value
	def getVariabels(self) -> dict:
		for var in inspect.getmembers(self):
			if not var[0].startswith('_'):
				if not inspect.ismethod(var[1]):
					items[var] = var[1]


		return items

	def setVariables(self, items:list) -> None:
		no = 0
		for var in inspect.getmembers(self):
			if not var[0].startswith('_'):
				if not inspect.ismethod(var[1]):
					var[1] = items[no]
					no = no+1
		print(self.id)


	def getVariablesType(self) -> dict:
		value = self.__annotations__
		return value

