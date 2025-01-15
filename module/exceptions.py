

from typing import Optional





class ServerAuthenticationError(BaseException):

	def __init__(self, text : Optional[str] = None):
		self.text = text



class DatabaseError(BaseException):

	def __init__(self, text : Optional[str] = None):
		self.text = text
