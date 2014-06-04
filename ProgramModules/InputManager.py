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
		for inputChannelId in inputParams: #handle multi channels first
			if inputParams[inputChannelId]['type'] == 'multi':
				newInputInstanceId = self.createNewInput(inputParams[inputChannelId].copy())
				if 'channels' in inputParams[inputChannelId].keys(): #multi input that assigned to several non-multi channels
					for i in range(len(inputParams[inputChannelId]['channels'])):
						self.registerAndGetInput(patternId, newInputInstanceId, inputParams[inputChannelId]['channels'][i])
						inputDict[inputParams[inputChannelId]['channels'][i]] = {'inputObj' : self.inputInstances[newInputInstanceId], 'outParamIndex' : i}
					channelsBoundToMulti += inputParams[inputChannelId]['channels']
				else:# multi input that is assigned to multi channel
					inputObj = self.registerAndGetInput(patternId, newInputInstanceId, inputChannelId)
					inputDict[inputChannelId] = {'inputObj' : inputObj, 'outParamIndex' : [i for i in range(len(inputObj.getCurrentStateData()['outputs']))]}
		for inputChannelId in inputParams: #single channels
			if not (inputParams[inputChannelId]['type'] == 'multi' or inputChannelId in channelsBoundToMulti):
				newInputInstanceId = self.createNewInput(inputParams[inputChannelId].copy())
				if 'outParamIndex' in inputParams[inputChannelId].keys():
					outParamIndex = inputParams[inputChannelId][outParamIndex]
				else:
					outParamIndex = 0
				inputDict[inputChannelId] = {'inputObj' : self.inputInstances[newInputInstanceId], 'outParamIndex' : outParamIndex}
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

class InputCollection(object): #a package of all the inputs used by a module or pattern instance
	def __init__(self, parentObj, inputManager, inputCollection, inputParams):
		self.inputCollection = inputCollection
		self.inputParams = inputParams
		self.parentObj = parentObj
		self.messengerBindingIds = {}
		self.inputManager = inputManager
		for inputChannelId in inputParams:
			self.addMessengerBindingsIfNeeded(inputChannelId)

	def __getattr__(self, inputChannelId):
		if isinstance(self.inputCollection[inputChannelId]['outParamIndex'], list):
			return self.inputCollection[inputChannelId]['inputObj'].getValue
		else:
			return self.inputCollection[inputChannelId]['inputObj'].getValue(self.inputCollection[inputChannelId]['outParamIndex'])

	def getInputAssignment(self, inputChannelId):
		return [self.inputCollection[inputChannelId]['inputObj'].getId(), self.inputCollection[inputChannelId]['outParamIndex']]
		
	def doCommand(self, args):
		function = getattr(self.inputCollection[args.pop(0)]['inputObj'], args.pop(0))
		return function(*args)
	
	def reassignInput (self, inputChannelId, inputInstanceId, outParamIndex = 0):
		inputObj = self.inputManager.registerAndGetInput(self.parentObj.getId(), inputInstanceId, inputChannelId)
		self.inputCollection[inputChannelId]['inputObj'] = inputObj
		self.inputCollection[inputChannelId]['outParamIndex'] = outParamIndex
		self.removeExistingMessengerBindings(inputChannelId)
		self.addMessengerBindingsIfNeeded(inputChannelId)

	def addMessengerBindingsIfNeeded(self, inputChannelId):
		if 'bindToFunction' in self.inputParams[inputChannelId].keys():
			inputAssignment = self.getInputAssignment(inputChannelId)
			function = getattr(self.parentObj, self.inputParams[inputChannelId]['bindToFunction'])
			if isinstance(inputAssignment[1], list):
				self.messengerBindingIds[inputChannelId] = [appMessenger.addBinding('output%s_%s' %(inputAssignment[0], i), function, (inputChannelId, i)) for i in range(len(inputAssignment[1]))]
			else:
				self.messengerBindingIds[inputChannelId] = appMessenger.addBinding('output%s_%s' %(inputAssignment[0], inputAssignment[1]), function, (inputChannelId,  inputAssignment[1]))

	def removeExistingMessengerBindings(self, inputChannelId):
		if inputChannelId in self.messengerBindingIds.keys():
			if isinstance(self.messengerBindingIds[inputChannelId], list):
				for messengerBindingId in self.messengerBindingIds[inputChannelId]:
					appMessenger.removeBinding(messengerBindingId)
			else:
				appMessenger.removeBinding(self.messengerBindingIds[inputChannelId])
			del self.messengerBindingIds[inputChannelId]

	def getCurrentStateData(self):
		data = {}
		for inputChannelId in self.inputParams:
			if not('channels' in self.inputParams[inputChannelId].keys()):
				inputAssignment = self.getInputAssignment(inputChannelId) 
				data[inputChannelId] = {'type' : self.inputParams[inputChannelId]['type'], 'inputInstanceId' : inputAssignment[0], 'outParamIndex' : inputAssignment[1], 'description' : self.inputParams[inputChannelId]['descriptionInPattern']}
		return data
		
	
	def stop(self):
		for inputChannelId in self.inputParams:
			self.removeExistingMessengerBindings(inputChannelId)
		self.inputManager.unRegisterInput(self.parentObj.getId())
		self.parentObj = False



