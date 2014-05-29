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
				self.addMessengerBindingsIfNeeded(patternInputId)


	def addMessengerBindingsIfNeeded(self, patternInputId):
		if 'bindToFunction' in self.inputParams[patternInputId].keys() and self.inputParams[patternInputId]['bindToFunction']:
			inputBinding = self.inputs.getBinding(patternInputId)
			if isinstance(inputBinding[1], list):
				self.messengerBindingIds[patternInputId] = [appMessenger.addBinding('output%s_%s' %(inputBinding[0], i), getattr(self, patternInputId), i) for i in range(len(inputBinding[1]))]
			else:
				self.messengerBindingIds[patternInputId] = appMessenger.addBinding('output%s_%s' %(inputBinding[0], inputBinding[1]), getattr(self, patternInputId))

	def removeExistingMessengerBindings(self, patternInputId):
		if patternInputId in self.messengerBindingIds.keys():
			if isinstance(self.messengerBindingIds[patternInputId], list):
				for messengerBindingId in self.messengerBindingIds[patternInputId]:
					appMessenger.removeBinding(messengerBindingId)
			else:
				appMessenger.removeBinding(self.messengerBindingIds[patternInputId])
			del self.messengerBindingIds[patternInputId]
	
	
	def changeInputBinding(self, patternInputId, inputInstanceId, outputIndexOfInput = 0):
		self.inputs.replaceInput(patternInputId, self.inputManager.registerAndGetInput(self.instanceId, inputInstanceId, patternInputId), outputIndexOfInput)
		self.removeExistingMessengerBindings(patternInputId)
		self.addMessengerBindingsIfNeeded(patternInputId)


	def stop(self):
		for patternInputId in self.inputParams:
			self.removeExistingMessengerBindings(patternInputId)
		self.messengerBindingIds = {}
		self.updateTriggerFunction = False
		inputs = False
		self.inputManager.unRegisterInput(self.instanceId)


	def getCurrentStateData(self):
		data = {'name' : self.patternName, 'inputs' : {}}
		for patternInputId in self.inputParams:
			if not(self.inputParams[patternInputId]['type'] == 'multi'):
				inputBinding = self.inputs.getBinding(patternInputId) 
				data['inputs'][patternInputId] = {'type' : self.inputParams[patternInputId]['type'], 'inputInstanceId' : inputBinding[0], 'outputIndexOfInput' : inputBinding[1], 'description' : self.inputParams[patternInputId]['descriptionInPattern']}
		data['messengerBindingIds'] = self.messengerBindingIds
		return data
	

	def bindUpdateTrigger(self, function):
		self.updateTriggerFunction = function


	def getId(self):
		return self.instanceId
