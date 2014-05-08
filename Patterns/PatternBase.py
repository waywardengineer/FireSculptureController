class PatternBase():
	def __init__ (self, inputManager, gridSize):
		self.inputManager = inputManager
		self.gridSize = gridSize
		self.inputParamData = {}
		self.messengerBindingIds = {}
		self.updateTriggerFunction = False
		self.patternName = ''
		try:
			self.inputParams
		except:
			self.inputs = False
		else:
			self.inputs = self.inputManager.buildInputCollection(self.inputParams)
			for patternInputId in self.inputParams:
				if self.inputParams[patternInputId]['type'] == 'pulse':
					inputObj = getattr(self.inputs, patternInputId)
					self.messengerBindingIds[patternInputId] = appMessenger.addBinding('pulse%s' %(inputObj.getId()), getattr(self, patternInputId))


	def changeInputBinding(self, patternInputId, inputInstanceId):
		self.inputs.replaceInput(patternInputId, inputManager.getInputObj(inputInstanceId))
		if self.inputParamData[patternInputId]['patternInputSpecs']['type'] == 'pulse':
			if patternInputId in self.messengerBindingIds.keys():
				appMessenger.removeBinding(self.messengerBindingIds[patternInputId])
				del self.messengerBindingIds[patternInputId]
			newBindingId = appMessenger.addBinding('pulse%s' %(inputInstanceId), getattr(self, patternInputId))
			self.messengerBindingIds[inputInstanceId] = newBindingId


	def unBind(self):
		for bindingIdKey in self.messengerBindingIds:
			appMessenger.removeBinding(self.messengerBindingIds[bindingIdKey])
			del self.messengerBindingIds[bindingIdKey]
		self.updateTriggerFunction = False
	
	def getCurrentStateData(self):
		data = {'name' : self.patternName, 'inputBindings' : {}}
		for patternInputId in self.inputParams:
			inputObj = getattr(self.inputs, patternInputId)
			data['inputBindings'][patternInputId] = inputObj.getId()
		return data

	def bindUpdateTrigger(self, function):
		self.updateTriggerFunction = function
