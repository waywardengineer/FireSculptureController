class PatternBase():
	def __init__ (self, inputManager, gridSize, instanceId):
		self.gridSize = gridSize
		self.updateTriggerFunction = False
		self.patternName = ''
		self.instanceId = instanceId
		try:
			self.inputParams
		except:
			self.inputs = False
		else:
			self.inputs = inputManager.buildInputCollection(self, self.inputParams, self.instanceId)

	def changeInputBinding(self, *args):
		self.inputs.replaceInput(*args)


	def stop(self):
		self.inputs.stop()
		self.updateTriggerFunction = False
		self.inputs = False


	def getCurrentStateData(self):
		return({'name' : self.patternName, 'inputs' : self.inputs.getCurrentStateData()})
	

	def bindUpdateTrigger(self, function):
		self.updateTriggerFunction = function


	def getId(self):
		return self.instanceId
