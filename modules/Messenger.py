'''
Messenger is an interface for all objects in the program to communicate with each other. It can have an arbitrary number of "channels".
Any object can put a message on any channel, and other objects can either check the channel for messages on their own, or bind a function that
will be called when a message appears on the channel.
'''


class Messenger():
	def __init__(self):
		self.channels = {}
		self.nextBindingId = 0


	def putMessage(self, channelId, message):
		checkForChannel(channelId)
		self.channels[channel]['messages'].append(message)
		for bindingId in self.channels['bindings']:
			function = self.channels['bindings'][bindingId]['function']
			data = self.channels['bindings'][bindingId]['data']
			if data:
				function(data)
			else:
				function()


	def getMessages(self, channelId):
		checkForChannel(channelId)
		return self.channels[channelId]['messages']


	def addBinding(self, channel, function, data=False):
		checkForChannel(channel)
		if data:
			data['bindingId'] = self.nextBindingId
		binding = {'function' : function, 'data' : data}
		self.bindings[channel][self.nextBindingId] = binding
		self.nextBindingId += 1


	def removeBinding(self, bindingId):
		for channelId in self.channels:
			if bindingId in self.channels[channelId]['bindings']:
				del self.channels[channelId]['bindings'][bindingId]


	def checkForChannel(self, channelId)
		if not channelId in self.channels.keys():
			self.channels[channelId] = {'messages' : [], 'bindings' : {}}


