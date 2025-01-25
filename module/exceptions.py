

from typing import Optional





class ServerAuthenticationError(Exception):

	def __init__(self, text : Optional[str] = None):
		self.text = text


class ServerNotConnectedError(Exception):

	def __init__(self, text : Optional[str] = None):
		self.text = text


class DatabaseError(Exception):

	def __init__(self, text : Optional[str] = None):
		self.text = text
