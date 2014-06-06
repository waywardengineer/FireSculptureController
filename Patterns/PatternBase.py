class PatternBase():
	def __init__ (self, inputManager, gridSize, instanceId):
		self.gridSize = gridSize
		self.requestUpdate = False
		self.patternName = ''
		self.instanceId = instanceId
		try:
			self.inputParams
		except:
			self.inputs = False
		else:
			self.inputs = inputManager.buildInputCollection(self, self.inputParams)

	def reassignInput(self, *args):
		self.inputs.reassignInput(*args)


	def stop(self):
		self.inputs.stop()
		self.requestUpdate = False
		self.inputs = False


	def getCurrentStateData(self):
		return({'name' : self.patternName, 'inputs' : self.inputs.getCurrentStateData()})
	

	def setUpdateFunction(self, function):
		self.requestUpdate = function


	def getId(self):
		return self.instanceId
