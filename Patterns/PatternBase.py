class PatternBase():
	def __init__ (self, inputManager, gridSize, instanceId):
		self.inputManager = inputManager
		self.gridSize = gridSize
		self.messengerBindingIds = {}
		self.updateTriggerFunction = False
		self.patternName = ''
		self.instanceId = instanceId

		try:
			self.inputParams
		except:
			self.inputs = False
		else:
			self.inputs = self.inputManager.buildInputCollection(self.inputParams, self.instanceId)
			for patternInputId in self.inputParams:
				if self.inputParams[patternInputId]['type'] == 'pulse':
					inputBinding = self.inputs.getBinding(patternInputId) 
					self.messengerBindingIds[patternInputId] = appMessenger.addBinding('output%s_%s' %(inputBinding[0], inputBinding[1]), getattr(self, patternInputId))


	def changeInputBinding(self, patternInputId, inputInstanceId, outputIndexOfInput = 0):
		self.inputs.replaceInput(patternInputId, self.inputManager.registerAndGetInput(self.instanceId, inputInstanceId, patternInputId), outputIndexOfInput)
		if self.inputParams[patternInputId]['type'] == 'pulse':
			if patternInputId in self.messengerBindingIds.keys():
				appMessenger.removeBinding(self.messengerBindingIds[patternInputId])
				del self.messengerBindingIds[patternInputId]
			newBindingId = appMessenger.addBinding('output%s_%s' %(inputInstanceId, outputIndexOfInput), getattr(self, patternInputId))
			self.messengerBindingIds[patternInputId] = newBindingId


	def stop(self):
		for bindingIdKey in self.messengerBindingIds:
			appMessenger.removeBinding(self.messengerBindingIds[bindingIdKey])
		self.messengerBindingIds = {}
		self.updateTriggerFunction = False
		inputs = False
		self.inputManager.unRegisterInput(self.instanceId)


	def getCurrentStateData(self):
		data = {'name' : self.patternName, 'inputs' : {}}
		for patternInputId in self.inputParams:
			inputBinding = self.inputs.getBinding(patternInputId) 
			data['inputs'][patternInputId] = {'type' : self.inputParams[patternInputId]['type'], 'inputInstanceId' : inputBinding[0], 'outputIndexOfInput' : inputBinding[1], 'description' : self.inputParams[patternInputId]['descriptionInPattern']}
		data['messengerBindingIds'] = self.messengerBindingIds
		return data
	

	def bindUpdateTrigger(self, function):
		self.updateTriggerFunction = function


	def getId(self):
		return self.instanceId
