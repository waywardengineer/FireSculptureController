import json
import os

from ProgramModules.DataChannelManager import DataChannelManager
from ProgramModules.InputManager import InputManager
from ProgramModules import SculptureModules



class SculptureController():
	def __init__(self):
		configFileName = 'config.json'
		definitionFileDirectory = 'sculptureDefinitions'
		self.sculptureDefinitions = {}
		self.sculptureModules = {}
		self.globalInputs = {}
		for definitionFileName in os.listdir(definitionFileDirectory):
			try:
				definition = json.load(open("%s/%s" %(definitionFileDirectory, definitionFileName)))
				self.sculptureDefinitions[definition['sculptureId']] = definition
			except:
				pass
		self.globalConfig = json.load(open(configFileName))
			
		self.doReset()



	def doReset(self):
		for moduleId in self.sculptureModules:
			self.sculptureModules[moduleId].stop()
		for inputInstanceId in self.globalInputs:
			self.globalInputs[inputInstanceId].stop()
		self.globalInputs = {}
		self.sculptureModules = {}
		self.dataChannelManager = False
		self.inputManager = False
		self.sculptureConfig = False
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
		for inputDefinition in self.globalConfig['inputs']:
			newInputId = self.inputManager.createNewInput(inputDefinition)
			self.globalInputs[newInputId] = (self.inputManager.registerUsage('main', newInputId))
	def setInputValue(self, inputInstanceId, *args):
		inputObj = self.inputManager.getInputObj(inputInstanceId)
		inputObj.setInputValue(*args)


	def doCommand(self, command):
		functionName = command[0]
		if functionName in ['setInputValue', 'getCurrentStateData', 'getCurrentOutputState', 'loadSculpture']:
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
			data = {'currentSculpture' : self.sculptureConfig.copy()}
			for moduleId in self.sculptureConfig['modules']:
				data['currentSculpture']['modules'][moduleId] = dict(self.sculptureConfig['modules'][moduleId], **self.sculptureModules[moduleId].getCurrentStateData())
			data = dict(data, **self.inputManager.getCurrentStateData())
			
		else:
			data = {'sculptures' : {}}
			for sculptureId in self.sculptureDefinitions:
				data['sculptures'][sculptureId] = self.sculptureDefinitions[sculptureId]
		return data


