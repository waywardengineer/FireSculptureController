class Messenger():
	def __init__(self):
		self.messages = {}
	def putMessage(self, unitId, message):
		if not unitId in self.messages.keys():
			self.messages[unitId] = []
		self.messages[unitId].append(message)
	def getMessages(self, unitId):
		messages = []
		if unitId in self.messages.keys():
			messages = self.messages[unitId]
			self.messages[unitId] = []
		return messages
