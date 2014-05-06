'''Runs and overlays patterns, controls inputs to patterns, communicates pattern data to DataChannelManager. One instance of this per module
Each pattern will have some number of inputs which can be assigned to either gui things or input devices, and are of either an on/off type 
or a variable type(probably from 0 to 100) 
'''

class PatternManager:
	def __init__ (self, dataChannelManager, inputManager, moduleConfig):
		self.dataChannelManager = dataChannelManager
		self.inputManager = inputManager
		self.moduleConfig = moduleConfig
		self.availablePatternClasses = {}
		self.availablePatternNames = []
		patternModuleName = 'Patterns_' + moduleConfig['patternType']
		patternClasses = __import__(patternModuleName)
		self.patternStack = {}
		self.patternInstanceIdCounter = 0
		for patternId in self.moduleConfig['patterns']:
			try:
				self.availablePatternClasses[patternId] = getattr(patternClasses, patternId)
				self.availablePatternNames.append(patternId)
			except:
				pass
	def getAvailablePatterns(self): #return list of patterns that apply for this module and sculpture
		return self.availablePatternNames
		
	def addPatternToStack(self, patternId): # make a pattern live and select all rows by default
		self.patternStack[self.patternInstanceIdCounter] = {'patternId' : patternId, 'pattern' : self.availablePatternClasses[patternId](), 'rows' : [True for i in range(len(self.moduleConfig['protocol']['mapping']))]}
		self.bindDefaultInputs(self.patternInstanceIdCounter)
		self.patternInstanceIdCounter += 1
	
	def toggleRowSelection(self, patternInstanceId, row): #toggle row selection for pattern
		self.patternStack[patternInstanceId]['rows'][row] = not self.patternStack[patternInstanceId]['rows'][row]
	
	#def getActivePatterns(self): #get active patterns, their rows, settings, and instance IDs
	
	def removePatternFromStack(self, patternInstanceId): #remove a pattern instance from the stack
		del self.patternStack[patternInstanceId]
		

	def bindDefaultInputs(self, patternInstanceId):
		pass
	
	#def bindInput(self, patternInstanceId, patternParameterIndex, inputId): #connect data from an input to a pattern parameter
	
	#def checkForUpdates(self): #will be called my a timer thread, sees if there are any messages from other timer threads or new inputs, sends new data out
	