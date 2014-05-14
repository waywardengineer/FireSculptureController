import json
class PatternBase():
	def __init__ (self, inputManager, gridSize):
		self.inputManager = inputManager
		self.gridSize = gridSize
		self.inputParamData = {}
		self.messengerBindingIds = {}
		self.updateTriggerFunction = False
		self.patternName = ''
		self.instanceId = False

		try:
			self.inputParams
		except:
			self.inputs = False
		else:
			self.inputs = self.inputManager.buildInputCollection(self.inputParams, self.instanceId)
			for patternInputId in self.inputParams:
				if self.inputParams[patternInputId]['type'] == 'pulse':
					inputObj = getattr(self.inputs, patternInputId)
					self.messengerBindingIds[patternInputId] = appMessenger.addBinding('pulse%s' %(inputObj.getId()), getattr(self, patternInputId))


	def changeInputBinding(self, inputInstanceId, patternInputId):
		self.inputs.replaceInput(patternInputId, inputManager.registerUsage(self.instanceId, inputInstanceId, patternInputId))
		if self.inputParamData[patternInputId]['patternInputSpecs']['type'] == 'pulse':
			if patternInputId in self.messengerBindingIds.keys():
				appMessenger.removeBinding(self.messengerBindingIds[patternInputId])
				del self.messengerBindingIds[patternInputId]
			self.messengerBindingIds[inputInstanceId] = newBindingId
			newBindingId = appMessenger.addBinding('pulse%s' %(inputInstanceId), getattr(self, patternInputId))


	def unBind(self):
		for bindingIdKey in self.messengerBindingIds:
			appMessenger.removeBinding(self.messengerBindingIds[bindingIdKey])
		self.messengerBindingIds = {}
		self.updateTriggerFunction = False
		inputs = False
		self.inputManager.unRegisterUsage(self.instanceId)


	def getCurrentStateData(self):
		data = {'name' : self.patternName, 'inputBindings' : {}}
		for patternInputId in self.inputParams:
			inputObj = getattr(self.inputs, patternInputId)
			print patternInputId
			
			data['inputBindings'][patternInputId] = {'inputInstanceId' : inputObj.getId(), 'description' : self.inputParams[patternInputId]['description']}
		return data
	

	def bindUpdateTrigger(self, function):
		self.updateTriggerFunction = function



	def setInstanceId(self, id):
		self.instanceId = id


	def getId(self):
		return self.instanceId
