class InputManager():
	def __init__ (self, dataChannelManager):
		self.dataChannelManager = dataChannelManager
		self.inputModules = __import__('ProgramModules.Inputs')
		self.nextInputInstanceId = 0
		self.inputInstances = {}


	def buildInputCollection(self, inputParams):
		inputDict = {}
		for patternInputId in inputParams:
			typeName = inputParams[patternInputId]['type']
			subTypeName = inputParams[patternInputId]['defaultSubType']
			inputClassName = subTypeName[0].upper() + subTypeName[1:] + typeName[0].upper() + typeName[1:] + 'Input'
			inputClass = getattr(self.inputModules, inputClassName)
			self.inputInstances[self.nextInputInstanceId] = inputClass(inputParams[patternInputId])
			self.inputInstances[self.nextInputInstanceId].setInstanceId(self.nextInputInstanceId)
			inputDict[patternInputId] = self.inputInstances[self.nextInputInstanceId]
			self.nextInputInstanceId += 1
		InputCollectionWrapper = getattr(self.inputModules, "InputCollectionWrapper")
		return InputCollectionWrapper(inputDict)


	def getInputObj(self, inputInstanceId):
		return self.inputInstances[inputInstanceId]

