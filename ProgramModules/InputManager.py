''' Builds collections of input objects based on defaults. Manages uses: Inputs 
can be used by multiple things, so this keeps track of who's using what and deletes unused inputs'''


class InputManager():
	def __init__ (self, dataChannelManager):
		self.dataChannelManager = dataChannelManager
		self.inputModules = __import__('ProgramModules.Inputs')
		self.nextInputInstanceId = 1
		self.inputInstances = {}
		self.inputInstanceUses = {}


	def buildInputCollection(self, inputParams, patternId):
		inputDict = {}
		for inputChannelId in inputParams:
			newInputInstanceId = self.createNewInput(inputParams[inputChannelId])
			inputDict[inputChannelId] = self.inputInstances[newInputInstanceId]
			self.registerUsage(patternId, newInputInstanceId, inputChannelId)
		InputCollectionWrapper = getattr(self.inputModules, "InputCollectionWrapper")
		return InputCollectionWrapper(inputDict)

	def createNewInput(self, params):
		typeName = params['type']
		subTypeName = params['subType']
		newInputInstanceId = self.nextInputInstanceId
		self.nextInputInstanceId += 1
		inputClassName = subTypeName[0].upper() + subTypeName[1:] + typeName[0].upper() + typeName[1:] + 'Input'
		inputClass = getattr(self.inputModules, inputClassName)
		self.inputInstances[newInputInstanceId] = inputClass(params, newInputInstanceId)
		return newInputInstanceId

	def registerUsage(self, userId, inputInstanceId, inputChannelId = False):
		if not inputInstanceId in self.inputInstanceUses.keys():
			self.inputInstanceUses[inputInstanceId] = []
		self.inputInstanceUses[inputInstanceId].append([userId, inputChannelId])
		return self.getInputObj(inputInstanceId)


	def unRegisterUsage(self, userId, inputInstanceId = False, inputChannelId = False):
		def checkItem(l, userId, inputChannelId):
			return userId == l[0] and (not inputChannelId or inputChannelId == l[1])
		def unRegisterForInput(userId, inputInstanceId, inputChannelId):
			self.inputInstanceUses[inputInstanceId][:] = [l for l in self.inputInstanceUses[inputInstanceId] if not checkItem(l, userId, inputChannelId)]
			if len(self.inputInstanceUses[inputInstanceId]) == 0 and not self.inputInstances[inputInstanceId].isPersistant():
				self.inputInstances[inputInstanceId].stop()
				del self.inputInstances[inputInstanceId]

		if not inputInstanceId:
			for inputInstanceId in self.inputInstanceUses:
				unRegisterForInput(userId, inputInstanceId, inputChannelId)
		else:
			unRegisterForInput(userId, inputInstanceId, inputChannelId)

	def getCurrentStateData(self):
		data = {}
		for inputInstanceId in self.inputInstances:
			data[inputInstanceId] = self.inputInstances[inputInstanceId].getCurrentStateData()
		data = {'inputs' : data}
		return data
		

	def getInputObj(self, inputInstanceId):
		return self.inputInstances[inputInstanceId]

