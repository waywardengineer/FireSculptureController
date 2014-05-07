'''Runs and overlays patterns, controls inputs to patterns, communicates pattern data to DataChannelManager. One instance of this per module
Each pattern will have some number of inputs which can be assigned to either gui things or input devices, and are of either an on/off type 
or a variable type(probably from 0 to 100) 
'''

class PatternManager:
	def __init__ (self, dataChannelManager, inputManager, sculptureConfig):
		self.dataChannelManager = dataChannelManager
		self.inputManager = inputManager
		self.sculptureConfig = sculptureConfig
		self.patterns = {}
		self.modulesData = {}
		self.patternInstanceIdCounter = 0
		for moduleConfig in sculptureConfig['modules']:
			patternModuleName = 'Patterns_' + moduleConfig['patternType']
			patternClasses = __import__(patternModuleName)
			moduleData = {'availablePatternClasses' : {}, 'availablePatternNames':[], 'currentPatternIds' : []}
			for patternId in moduleConfig['patterns']:
				try:
					moduleData['availablePatternClasses'][patternId] = getattr(patternClasses, patternId)
					moduleData['availablePatternNames'].append(patternId)
				except:
					pass
			modulesData.append(moduleData)
		appMessenger.addBinding('patternTimers', getattr(self, 'doUpdates'))

	def getPatternData(self, module): 
		return self.modulesData[module]

	def addPatternToStack(self, module, patternId): # make a pattern live and select all rows by default
		self.patterns[self.patternInstanceIdCounter] = {
						'patternId' : patternId, 
						'pattern' : self.availablePatternClasses[patternId](),
						'rows' : [True for i in range(len(self.moduleConfig['protocol']['mapping']))],
						'inputIds' : []
						}
		self.modulesData[module][
		self.bindDefaultInputs(self.patternInstanceIdCounter)
		self.patternInstanceIdCounter += 1
	
	def toggleRowSelection(self, patternInstanceId, row): #toggle row selection for pattern
		self.patterns[patternInstanceId]['rows'][row] = not self.patternStack[patternInstanceId]['rows'][row]
	
	#def getActivePatterns(self): #get active patterns, their rows, settings, and instance IDs
	
	def removePatternFromStack(self, patternInstanceId): #remove a pattern instance from the stack
		del self.patterns[patternInstanceId]
		

	def bindDefaultInputs(self, patternInstanceId):
		for input in self.patterns[patternInstanceId]['pattern'].getInputs():
			newId = inputManager.getInputId(input['subType'], self.patterns[patternInstanceId]['inputIds'])
			self.patterns[patternInstanceId]['inputIds'].append(newId)

			
	
	def bindInput(self, patternInstanceId, patternParameterIndex, inputId): #connect data from an input to a pattern parameter
	
	def doUpdates(self): #will be called my a timer thread, sees if there are any messages from other timer threads or new inputs, sends new data out
		self.dataChannelManager.send('poofers', [[[0, 15], [True]]])
	