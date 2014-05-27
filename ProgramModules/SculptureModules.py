'''Runs and overlays patterns, binds inputs to patterns, communicates pattern data to DataChannelManager. 
Each pattern will have some number of inputs which can be assigned to either gui things or input devices, and are of either an on/off type 
or a variable type(probably from 0 to 100) 
'''

from copy import deepcopy

class SculptureModuleBase():
	def __init__ (self, dataChannelManager, inputManager, moduleConfig):

		self.dataChannelManager = dataChannelManager
		self.inputManager = inputManager
		self.moduleConfig = deepcopy(moduleConfig)
		self.nextPatternInstanceId = 0
		patternModuleName = 'Patterns.' + moduleConfig['patternType']
		patternClasses = __import__(patternModuleName)
		self.availablePatternClasses = {} 
		self.availablePatternNames = []
		self.patterns = {}
		self.patternRowSettings = {}
		self.gridSize = [len(moduleConfig['protocol']['mapping']), len(moduleConfig['protocol']['mapping'][0])]
		for patternTypeId in moduleConfig['patterns']:
			try:
				self.availablePatternClasses[patternTypeId] = getattr(patternClasses, patternTypeId)
				self.availablePatternNames.append(patternTypeId)
			except:
				pass


	def getCurrentStateData(self, *args): # Dump all the state data for gui to render it
		data = {'availablePatternNames' : self.availablePatternNames, 'currentOutputState' : self.currentOutputState, 'patterns' : {}}
		for patternInstanceId in self.patterns:
			patternData = self.patterns[patternInstanceId].getCurrentStateData()
			patternData['instanceId'] = patternInstanceId
			patternData['rowSettings'] = self.patternRowSettings[patternInstanceId]
			data['patterns'][patternInstanceId] = patternData
		return data

	def addPattern(self, patternTypeId): # make a pattern live and select all rows by default
		newInstanceId = '%sPattern%s' %(self.moduleConfig['moduleId'], self.nextPatternInstanceId)
		self.patterns[newInstanceId] = self.availablePatternClasses[patternTypeId](self.inputManager, self.gridSize, newInstanceId)
		self.patternRowSettings[newInstanceId] = [True for i in range(self.gridSize[0])]
		self.patterns[newInstanceId].bindUpdateTrigger(getattr(self, "doUpdates"))
		self.nextPatternInstanceId += 1
		return newInstanceId

	def removePattern(self, patternInstanceId): #remove a pattern instance from the stack
		self.patterns[patternInstanceId].stop()
		del self.patterns[patternInstanceId]

	def bindPatternToNewInput(self, patternInstanceId, patternInputId, newPatternParams):
		return self.changePatternInputBinding(patternInstanceId, patternInputId, self.inputManager.createNewInput(newPatternParams))
	
	def stop(self):
		for patternInstanceId in self.patterns:
			self.patterns[patternInstanceId].stop()
		self.patterns = {}
	
	def doCommand(self, command):
		functionName = command.pop(0)
		function = getattr(self, functionName)
		return function(*command)

	def changePatternInputBinding(self, patternInstanceId, *args): #connect data from an input to a pattern parameter
		return self.patterns[patternInstanceId].changeInputBinding(*args)
	def getCurrentOutputState(self):
		return self.currentOutputState

class PooferModule(SculptureModuleBase):
	def __init__ (self, *args):
		SculptureModuleBase.__init__ (self, *args)
		self.currentOutputState = [[False for j in range(self.gridSize[1])] for i in range(self.gridSize[0])]
		self.enabledStatus = [[True for j in range(self.gridSize[1])] for i in range(self.gridSize[0])]
		safeMode.addBinding(self.doUpdates);

	def doUpdates(self): #Check the pattern state and send data out
		data = []
		for row in range(len(self.moduleConfig['protocol']['mapping'])):
			for col in range(len(self.moduleConfig['protocol']['mapping'][row])):
				state = False
				for patternId in self.patterns:
					state = ((not safeMode.isSet()) and self.enabledStatus[row][col]) and (state or (self.patternRowSettings[patternId][row] and self.patterns[patternId].getState(row, col)))
				if not state == self.currentOutputState[row][col]:
					data.append([[row, col], [state]])
					self.currentOutputState[row][col] = state
		self.dataChannelManager.send(self.moduleConfig['moduleId'], data)
		appMessenger.putMessage('outputChanged', {'moduleId' : self.moduleConfig['moduleId'], 'data' : data})

	def toggleEnable(self, address):
		self.enabledStatus[address[0]][address[1]] = not self.enabledStatus[address[0]][address[1]]
		return self.enabledStatus

	def toggleRowSelection(self, patternInstanceId, row): #toggle row selection for pattern
		self.patternRowSettings[patternInstanceId][row] = not self.patternRowSettings[patternInstanceId][row]
		
	def getCurrentStateData(self, *args): # Dump all the state data for gui to render it
		data = SculptureModuleBase.getCurrentStateData(self, *args)
		data['enabledStatus'] = self.enabledStatus
		return data


