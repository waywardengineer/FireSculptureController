''' Builds collections of input objects based on defaults. Manages uses: Inputs 
can be used by multiple things, so this keeps track of who's using what and deletes unused inputs'''
from ProgramModules import utils
import Inputs
class InputManager():
	def __init__ (self, dataChannelManager):
		self.dataChannelManager = dataChannelManager
		#self.inputModules = __import__('Inputs')
		self.nextInputInstanceId = 1
		self.inputInstances = {}
		self.inputInstanceUses = {}
		self.availableInputTypes = {}
		self.inputCollections = {}
		for inputType in Inputs.availableInputTypes:
			self.availableInputTypes[inputType] = {}
			for subType in Inputs.availableInputTypes[inputType]:
				if not ('unavailable' in Inputs.inputTypes[' '.join([subType, inputType]).strip()].keys()):
					self.availableInputTypes[inputType][subType] = Inputs.inputTypes[' '.join([subType, inputType]).strip()]

	def buildInputCollection(self, parentObj, inputParams):
		inputDict = {}
		channelsBoundToMulti = []
		for inputChannelId in inputParams: #handle multi channels first
			if inputParams[inputChannelId]['type'] == 'multi':
				newInputInstanceId = self.createNewInput(inputParams[inputChannelId].copy())
				if 'channels' in inputParams[inputChannelId].keys(): #multi input that assigned to several non-multi channels
					for i in range(len(inputParams[inputChannelId]['channels'])):
						self.registerAndGetInput(parentObj.getId(), newInputInstanceId, inputParams[inputChannelId]['channels'][i])
						inputDict[inputParams[inputChannelId]['channels'][i]] = {'inputObj' : self.inputInstances[newInputInstanceId], 'outParamIndex' : i}
					channelsBoundToMulti += inputParams[inputChannelId]['channels']
				else:# multi input that is assigned to multi channel
					inputObj = self.registerAndGetInput(parentObj.getId(), newInputInstanceId, inputChannelId)
					inputDict[inputChannelId] = {'inputObj' : inputObj, 'outParamIndex' : [i for i in range(len(inputObj.getCurrentStateData()['outParams']))]}
		for inputChannelId in inputParams: #single channels
			if not (inputParams[inputChannelId]['type'] == 'multi' or inputChannelId in channelsBoundToMulti):
				newInputInstanceId = self.createNewInput(inputParams[inputChannelId].copy())
				if 'outParamIndex' in inputParams[inputChannelId].keys():
					outParamIndex = inputParams[inputChannelId][outParamIndex]
				else:
					outParamIndex = 0
				inputDict[inputChannelId] = {'inputObj' : self.inputInstances[newInputInstanceId], 'outParamIndex' : outParamIndex}
				self.registerAndGetInput(parentObj.getId(), newInputInstanceId, inputChannelId)
		return InputCollection(parentObj, self, inputDict, inputParams)

	def createNewInput(self, params):
		newInputInstanceId = self.nextInputInstanceId
		self.nextInputInstanceId += 1
		inputTypeKey = ' '.join([params['subType'], params['type']]).strip()
		params = utils.extendSettings(Inputs.inputTypes[inputTypeKey], params)
		if 'unavailable' in Inputs.inputTypes[inputTypeKey].keys():
			return False
		params['inputTypeKey'] = inputTypeKey
		if params['hasOwnClass']:
			inputClassName = utils.makeCamelCase([params['subType'], params['type'], 'input'], True)
		else:
			inputClassName = 'InputBase'
		inputClass = getattr(Inputs, inputClassName)
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



