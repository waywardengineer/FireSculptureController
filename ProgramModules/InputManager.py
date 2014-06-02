''' Builds collections of input objects based on defaults. Manages uses: Inputs 
can be used by multiple things, so this keeps track of who's using what and deletes unused inputs'''
from ProgramModules import utils
class InputManager():
	def __init__ (self, dataChannelManager):
		self.dataChannelManager = dataChannelManager
		self.inputModules = __import__('ProgramModules.Inputs')
		self.nextInputInstanceId = 1
		self.inputInstances = {}
		self.inputInstanceUses = {}
		self.availableInputTypes = {}
		self.inputCollections = {}
		for inputType in self.inputModules.availableInputTypes:
			self.availableInputTypes[inputType] = {}
			for subType in self.inputModules.availableInputTypes[inputType]:
				className = utils.makeCamelCase([subType, inputType, 'input'], True)
				if not ('unavailable' in self.inputModules.inputParams[className].keys()):
					self.availableInputTypes[inputType][subType] = self.inputModules.inputParams[className]

	def buildInputCollection(self, parentObj, inputParams, patternId):
		inputDict = {}
		channelsBoundToMulti = []
		for inputChannelId in inputParams:
			if inputParams[inputChannelId]['type'] == 'multi':
				newInputInstanceId = self.createNewInput(inputParams[inputChannelId].copy())
				if 'channels' in inputParams[inputChannelId].keys():
					for i in range(len(inputParams[inputChannelId]['channels'])):
						self.registerAndGetInput(patternId, newInputInstanceId, inputParams[inputChannelId]['channels'][i])
						inputDict[inputParams[inputChannelId]['channels'][i]] = {'inputObj' : self.inputInstances[newInputInstanceId], 'outputIndexOfInput' : i}
					channelsBoundToMulti += inputParams[inputChannelId]['channels']
				else:
					inputObj = self.registerAndGetInput(patternId, newInputInstanceId, inputChannelId)
					inputDict[inputChannelId] = {'inputObj' : inputObj, 'outputIndexOfInput' : [i for i in range(len(inputObj.getCurrentStateData()['outputs']))]}
		for inputChannelId in inputParams:
			if not (inputParams[inputChannelId]['type'] == 'multi' or inputChannelId in channelsBoundToMulti):
				newInputInstanceId = self.createNewInput(inputParams[inputChannelId].copy())
				if 'outputIndexOfInput' in inputParams[inputChannelId].keys():
					outputIndexOfInput = inputParams[inputChannelId][outputIndexOfInput]
				else:
					outputIndexOfInput = 0
				inputDict[inputChannelId] = {'inputObj' : self.inputInstances[newInputInstanceId], 'outputIndexOfInput' : outputIndexOfInput}
				self.registerAndGetInput(patternId, newInputInstanceId, inputChannelId)
		return InputCollection(parentObj, self, inputDict, inputParams)

	def createNewInput(self, params):
		newInputInstanceId = self.nextInputInstanceId
		self.nextInputInstanceId += 1
		inputClassName = utils.makeCamelCase([params['subType'], params['type'], 'input'], True)
		if 'unavailable' in self.inputModules.inputParams[inputClassName].keys():
			return False
		inputClass = getattr(self.inputModules, inputClassName)
		self.inputInstances[newInputInstanceId] = inputClass(params, newInputInstanceId)
		return newInputInstanceId

	def registerAndGetInput(self, userId, inputInstanceId, inputChannelId = False):
		if inputChannelId:
			self.unRegisterInput(userId, inputChannelId = inputChannelId)
		if not inputInstanceId in self.inputInstanceUses.keys():
			self.inputInstanceUses[inputInstanceId] = []
		self.inputInstanceUses[inputInstanceId].append([userId, inputChannelId])
		return self.getInputObj(inputInstanceId)

	def unRegisterInput(self, userId, inputInstanceId = False, inputChannelId = False):
		def checkItem(l, userId, inputChannelId):
			return userId == l[0] and (not inputChannelId or inputChannelId == l[1])
		def unRegisterForInput(userId, inputInstanceId, inputChannelId):
			self.inputInstanceUses[inputInstanceId][:] = [l for l in self.inputInstanceUses[inputInstanceId] if not checkItem(l, userId, inputChannelId)]
			if len(self.inputInstanceUses[inputInstanceId]) == 0:
				if inputInstanceId in self.inputInstances.keys():
					self.inputInstances[inputInstanceId].stop()
					del self.inputInstances[inputInstanceId]

		if not inputInstanceId:
			for inputInstanceId in self.inputInstanceUses:
				unRegisterForInput(userId, inputInstanceId, inputChannelId)
		else:
			unRegisterForInput(userId, inputInstanceId, inputChannelId)

	def getCurrentStateData(self):
		currentInputData = {}
		for inputInstanceId in self.inputInstances:
			currentInputData[inputInstanceId] = self.inputInstances[inputInstanceId].getCurrentStateData()
		data = {'inputs' : currentInputData, 'availableInputTypes' : self.availableInputTypes}
		return data

	def getInputObj(self, inputInstanceId):
		return self.inputInstances[inputInstanceId]

class InputCollection(object):
	def __init__(self, parentObj, inputManager, inputCollection, inputParams):
		self.inputCollection = inputCollection
		self.inputParams = inputParams
		self.parentObj = parentObj
		self.messengerBindingIds = {}
		self.inputManager = inputManager
		for inputChannelId in inputParams:
			self.addMessengerBindingsIfNeeded(inputChannelId)

	def __getattr__(self, patternInputId):
		if isinstance(self.inputCollection[patternInputId]['outputIndexOfInput'], list):
			return self.inputCollection[patternInputId]['inputObj'].getValue
		else:
			return self.inputCollection[patternInputId]['inputObj'].getValue(self.inputCollection[patternInputId]['outputIndexOfInput'])

	def getBinding(self, patternInputId):
		return [self.inputCollection[patternInputId]['inputObj'].getId(), self.inputCollection[patternInputId]['outputIndexOfInput']]
		
	def doCommand(self, args):
		function = getattr(self.inputCollection[args.pop(0)]['inputObj'], args.pop(0))
		return function(*args)
	
	def replaceInput (self, patternInputId, inputInstanceId, outputIndexOfInput = 0):
		inputObj = self.inputManager.registerAndGetInput(self.parentObj.getId(), inputInstanceId, patternInputId)
		self.inputCollection[patternInputId]['inputObj'] = inputObj
		self.inputCollection[patternInputId]['outputIndexOfInput'] = outputIndexOfInput
		self.removeExistingMessengerBindings(patternInputId)
		self.addMessengerBindingsIfNeeded(patternInputId)

	def addMessengerBindingsIfNeeded(self, patternInputId):
		if 'bindToFunction' in self.inputParams[patternInputId].keys():
			inputBinding = self.getBinding(patternInputId)
			function = getattr(self.parentObj, self.inputParams[patternInputId]['bindToFunction'])
			if isinstance(inputBinding[1], list):
				self.messengerBindingIds[patternInputId] = [appMessenger.addBinding('output%s_%s' %(inputBinding[0], i), function, (patternInputId, i)) for i in range(len(inputBinding[1]))]
			else:
				self.messengerBindingIds[patternInputId] = appMessenger.addBinding('output%s_%s' %(inputBinding[0], inputBinding[1]), function, (patternInputId,  inputBinding[1]))

	def removeExistingMessengerBindings(self, patternInputId):
		if patternInputId in self.messengerBindingIds.keys():
			if isinstance(self.messengerBindingIds[patternInputId], list):
				for messengerBindingId in self.messengerBindingIds[patternInputId]:
					appMessenger.removeBinding(messengerBindingId)
			else:
				appMessenger.removeBinding(self.messengerBindingIds[patternInputId])
			del self.messengerBindingIds[patternInputId]

	def getCurrentStateData(self):
		data = {}
		for patternInputId in self.inputParams:
			if not('channels' in self.inputParams[patternInputId].keys()):
				inputBinding = self.getBinding(patternInputId) 
				data[patternInputId] = {'type' : self.inputParams[patternInputId]['type'], 'inputInstanceId' : inputBinding[0], 'outputIndexOfInput' : inputBinding[1], 'description' : self.inputParams[patternInputId]['descriptionInPattern']}
		return data
		
	
	def stop(self):
		for patternInputId in self.inputParams:
			self.removeExistingMessengerBindings(patternInputId)
		self.inputManager.unRegisterInput(self.parentObj.getId())
		self.parentObj = False



