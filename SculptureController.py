import json
import os
import inspect

from ProgramModules.DataChannelManager import DataChannelManager
from ProgramModules.InputManager import InputManager
from ProgramModules import SculptureModules
from ProgramModules import Inputs
from ProgramModules.Messenger import Messenger

class SafeModeController():
	def __init__(self):
		self.safeMode = True
	def isSet(self):
		return self.safeMode
	def set(self, value):
		self.safeMode = value


class SculptureController():
	def __init__(self):
		__builtins__['appMessenger'] = Messenger()
		__builtins__['safeMode'] = SafeModeController()
		configFileName = 'config.json'
		definitionFileDirectory = 'sculptureDefinitions'
		self.sculptureDefinitions = {}
		self.sculptureModules = {}
		self.globalInputs = {}
		self.inputManager = False
		self.dataChannelManager = False
		self.availableGlobalInputs = []
		for inputType in [['multi', 'osc'], ['pulse', 'audio']]:
			className = inputType[1][0].upper() + inputType[1][1:] + inputType[0][0].upper() + inputType[0][1:] + 'Input'
			if not 'unavailable' in Inputs.inputParams.keys():
				self.availableGlobalInputs.append(inputType)
		for definitionFileName in os.listdir(definitionFileDirectory):
			try:
				definition = json.load(open("%s/%s" %(definitionFileDirectory, definitionFileName)))
				self.sculptureDefinitions[definition['sculptureId']] = definition
			except:
				pass
		self.globalConfig = json.load(open(configFileName))
		self.availableInputs = {}
		self.methodList = [m[0] for m in inspect.getmembers(self, predicate=inspect.ismethod)]
		self.doReset()
	



	def doReset(self):
		for moduleId in self.sculptureModules:
			self.sculptureModules[moduleId].stop()
		for inputInstanceId in self.globalInputs:
			self.globalInputs[inputInstanceId].stop()
		if self.inputManager:
			self.inputManager.unRegisterInput('main')
		if self.dataChannelManager:
			self.dataChannelManager.stop()
		self.dataChannelManager = False
		self.inputManager = False
		self.sculptureConfig = False
		self.sculptureModules = {}
		self.globalInputs = {}
		appMessenger.doReset()
		


	def loadSculpture(self, sculptureId):
		self.doReset()
		self.sculptureConfig = self.sculptureDefinitions[sculptureId]
		self.dataChannelManager = DataChannelManager(self.sculptureConfig)
		self.inputManager = InputManager(self.dataChannelManager)
		self.currentSculptureId = sculptureId
		for moduleId in self.sculptureConfig['modules']:
			moduleConfig = self.sculptureConfig['modules'][moduleId]
			moduleConfig['moduleId'] = moduleId
			sculptureModuleClass = getattr(SculptureModules, moduleConfig['moduleType'] + 'Module')
			self.sculptureModules[moduleId] = sculptureModuleClass(self.dataChannelManager, self.inputManager, moduleConfig)
		appMessenger.addBinding('outputChanged', getattr(self, 'getCurrentOutputState'))


	def setInputValue(self, inputInstanceId, *args):
		inputObj = self.inputManager.getInputObj(inputInstanceId)
		inputObj.setInputValue(*args)


	def doCommand(self, command):
		functionName = command[0]
		if functionName in self.methodList:
			command.pop(0)
			function = getattr(self, functionName)
			return function(*command)
		else:
			moduleId = command.pop(1)
			return self.sculptureModules[moduleId].doCommand(command)

	def getCurrentOutputState(self):
		if self.sculptureConfig:
			data = {'sculptures' : {self.currentSculptureId : {'modules' : {}}}}
			for moduleId in self.sculptureConfig['modules']:
				data['sculptures'][self.currentSculptureId]['modules'][moduleId] = {'currentOutputState' : self.sculptureModules[moduleId].getCurrentOutputState()}
		else:
			data = {'sculptures' : {}}
		return data
			
	
	def getCurrentStateData(self, sculptureId = False, moduleId = False, *args): 
		if self.sculptureConfig:
			data = {'currentSculpture' : self.sculptureConfig.copy(), 'safeMode' : safeMode.isSet()}
			for moduleId in self.sculptureConfig['modules']:
				data['currentSculpture']['modules'][moduleId] = dict(self.sculptureConfig['modules'][moduleId], **self.sculptureModules[moduleId].getCurrentStateData())
			data = dict(data, **self.inputManager.getCurrentStateData())
			data['appMessenger'] = appMessenger.getCurrentStateData()
		else:
			data = {'sculptures' : {}}
			for sculptureId in self.sculptureDefinitions:
				data['sculptures'][sculptureId] = self.sculptureDefinitions[sculptureId]
		data['globalInputs'] = self.globalInputs.keys()
		data['availableGlobalInputs'] = self.availableGlobalInputs
		return data

	def addGlobalInput(self, inputParams):
		newInputId = self.inputManager.createNewInput(inputParams)
		self.globalInputs[newInputId] = self.inputManager.registerAndGetInput('main', newInputId)

	def removeGlobalInput(self, inputInstanceId):
		self.inputManager.unRegisterInput('main', inputInstanceId)
		del self.globalInputs[inputInstanceId]
		
	def setSafeMode(self, value):
		safeMode.set(value)

