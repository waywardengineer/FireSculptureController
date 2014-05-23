''' Builds collections of input objects based on defaults. Manages uses: Inputs 
can be used by multiple things, so this keeps track of who's using what and deletes unused inputs'''


class InputManager():
	def __init__ (self, dataChannelManager):
		self.dataChannelManager = dataChannelManager
		self.inputModules = __import__('ProgramModules.Inputs')
		self.nextInputInstanceId = 1
		self.inputInstances = {}
		self.inputInstanceUses = {}
		self.availableInputTypes = {}
		for inputType in self.inputModules.availableInputTypes:
			self.availableInputTypes[inputType] = {}
			for subType in self.inputModules.availableInputTypes[inputType]:
				if len(subType) > 1:
					className = subType[0].upper() + subType[1:] + inputType[0].upper() + inputType[1:] + 'Input'
				else:
					className = inputType[0].upper() + inputType[1:] + 'Input'
				if not ('unavailable' in self.inputModules.inputParams[className].keys()):
					self.availableInputTypes[inputType][subType] = self.inputModules.inputParams[className]

	def buildInputCollection(self, inputParams, patternId):
		inputDict = {}
		for inputChannelId in inputParams:
			newInputInstanceId = self.createNewInput(inputParams[inputChannelId].copy())
			if 'outputIndexOfInput' in inputParams[inputChannelId].keys():
				outputIndexOfInput = inputParams[inputChannelId][outputIndexOfInput]
			else:
				outputIndexOfInput = 0
			inputDict[inputChannelId] = {'inputObj' : self.inputInstances[newInputInstanceId], 'outputIndexOfInput' : outputIndexOfInput}
			self.registerAndGetInput(patternId, newInputInstanceId, inputChannelId)
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

	def registerAndGetInput(self, userId, inputInstanceId, inputChannelId = False):
		if inputChannelId:
			self.unRegisterInput(userId, inputChannelId = inputChannelId)
		if not inputInstanceId in self.inputInstanceUses.keys():
			self.inputInstanceUses[inputInstanceId] = []
		self.inputInstanceUses[inputInstanceId].append([userId, inputChannelId])
		return self.getInputObj(inputInstanceId)


	def unRegisterInput(self, userId, inputInstanceId = False, inputChannelId = False):
		def checkItem(l, userId, inputChannelId):
			return userId == l[0] and (not inputChannelId or inputChannelId == l[1])
		def unRegisterForInput(userId, inputInstanceId, inputChannelId):
			self.inputInstanceUses[inputInstanceId][:] = [l for l in self.inputInstanceUses[inputInstanceId] if not checkItem(l, userId, inputChannelId)]
			if len(self.inputInstanceUses[inputInstanceId]) == 0:
				if inputInstanceId in self.inputInstances.keys():
					self.inputInstances[inputInstanceId].stop()
					del self.inputInstances[inputInstanceId]

		if not inputInstanceId:
			for inputInstanceId in self.inputInstanceUses:
				unRegisterForInput(userId, inputInstanceId, inputChannelId)
		else:
			unRegisterForInput(userId, inputInstanceId, inputChannelId)

	def getCurrentStateData(self):
		currentInputData = {}
		for inputInstanceId in self.inputInstances:
			currentInputData[inputInstanceId] = self.inputInstances[inputInstanceId].getCurrentStateData()
		data = {'inputs' : currentInputData, 'availableInputTypes' : self.availableInputTypes}
		return data
		

	def getInputObj(self, inputInstanceId):
		return self.inputInstances[inputInstanceId]

