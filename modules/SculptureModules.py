'''Runs and overlays patterns, binds inputs to patterns, communicates pattern data to DataChannelManager. 
Each pattern will have some number of inputs which can be assigned to either gui things or input devices, and are of either an on/off type 
or a variable type(probably from 0 to 100) 
'''


class SculptureModuleBase():
	def __init__ (self, dataChannelManager, inputManager, moduleConfig):
		self.dataChannelManager = dataChannelManager
		self.inputManager = inputManager
		self.moduleConfig = moduleConfig
		self.nextPatternInstanceId = 0
		patternModuleName = 'Patterns_' + moduleConfig['patternType']
		patternClasses = __import__(patternModuleName)
		self.availablePatternClasses = {} 
		self.availablePatternNames = []
		self.patterns = {}
		self.gridSize = [len(moduleConfig['protocol']['mapping']), len(moduleConfig['protocol']['mapping'][0])]
		for patternTypeId in moduleConfig['patterns']:
			try:
				self.availablePatternClasses[patternTypeId] = getattr(patternClasses, patternTypeId)
				self.availablePatternNames.append(patternTypeId)
			except:
				pass


	def getModuleData(self, module): # gui will call this to render all the controls and stuff
		pass

	def addPattern(self, patternTypeId): # make a pattern live and select all rows by default
		self.patterns[self.nextPatternInstanceId] = {
						'patternTypeId' : patternTypeId, 
						'pattern' : self.availablePatternClasses[patternTypeId](self.inputManager, self.gridSize),
						'rows' : [True for i in range(self.gridSize[0])],
						}
		self.patterns[self.nextPatternInstanceId]['pattern'].bindUpdateTrigger(getattr(self, "doUpdates"))
		self.nextPatternInstanceId += 1

	def removePattern(self, patternInstanceId): #remove a pattern instance from the stack
		self.patterns[patternInstanceId]['pattern'].unBind()
		del self.patterns[patternInstanceId]


	def bindInput(self, patternInstanceId, patternInputId, inputInstanceId): #connect data from an input to a pattern parameter
		patternInputSpec = self.patterns[patternInstanceId]['pattern'].getInputSpecs(patternInputId)
		if inputManager.checkType(patternInputSpec['type'], inputInstanceId):
			self.patterns[patternInstanceId]['pattern'].bindInput(patternInputId, inputInstanceId)
			return True
		return False

class DiscreteActionModule(SculptureModuleBase):
	def doUpdates(self): #Check the pattern state and send data out
		data = []
		for row in range(len(self.moduleConfig['protocol']['mapping'])):
			for col in range(len(self.moduleConfig['protocol']['mapping'][row])):
				trigger = False
				for patternId in self.patterns:
					if self.patterns[patternId]['rows'][row] and self.patterns[patternId]['pattern'].getState(row, col):
						trigger = True
				data.append([[row, col], [trigger]])
		self.dataChannelManager.send(self.moduleConfig['id'], data)

	def toggleRowSelection(self, moduleId, patternInstanceId, row): #toggle row selection for pattern
		self.patterns[patternInstanceId]['rows'][row] = not self.patterns[patternInstanceId]['rows'][row]

