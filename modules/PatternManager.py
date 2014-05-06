'''Runs and overlays patterns, controls inputs to patterns, communicates pattern data to DataChannelManager. One instance of this per module
Each pattern will have some number of inputs which can be assigned to either gui things or input devices, and are of either an on/off type 
or a variable type(probably from 0 to 100) 
'''

class PatternManager.py
	def __init__ (self, dataChannelManager, inputManager, sculptureConfig, moduleId):
		self.sculptureConfig = sculptureConfig
		self.moduleId = moduleId
	def getAvailablePatterns(self): #return list of patterns that apply for this module and sculpture
	
	def addPatternToStack(self, patternId): # make a pattern live and select all rows by default
	
	def toggleRowSelection(self, patternInstanceId, row): #toggle row selection for pattern
	
	def getActivePatterns(self): #get active patterns, their rows, settings, and instance IDs
	
	def removePatternFromStack(self, patternInstanceId): #remove a pattern instance from the stack
	
	def assignInputToPattern(self, patternInstanceId, patternParameterIndex, inputId): #connect data from an input to a pattern parameter
	
	def checkForUpdates(self): #will be called my a timer thread, sees if there are any messages from other timer threads or new inputs, sends new data out