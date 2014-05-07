'''
Messenger is an interface for all objects in the program to communicate with each other. It can have an arbitrary number of "channels".
Any object can put a message on any channel, and other objects can either check the channel for messages on their own, or bind a function that
will be called when a message appears on the channel.
'''


class Messenger():
	def __init__(self):
		self.messages = {}
		self.bindings = {}
	def putMessage(self, channel, message):
		if not channel in self.messages.keys():
			self.messages[channel] = []
			self.bindings[channel] = []
		self.messages[channel].append(message)
		for binding in self.bindings[channel]:
			binding()
	def getMessages(self, channel):
		messages = []
		if channel in self.messages.keys():
			messages = self.messages[channel]
			self.messages[channel] = []
		return messages
	def addBinding(self, channel, function):
		if not channel in self.messages.keys():
			self.messages[channel] = []
			self.bindings[channel] = []
		self.bindings[channel].append(function)
		
		
		