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


	def doCommand(self, command):
		functionName = command[0]
		if functionName in ['getCurrentStateData', 'getCurrentOutputState', 'loadSculpture']:
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
			data['inputs'] = self.inputManager.getCurrentStateData()['inputs']
			
		else:
			for sculptureId in self.sculptureDefinitions:
				data['sculptures'][sculptureId] = {'config' : self.sculptureDefinitions[sculptureId], 'modules' : False}
				if self.sculptureConfig and sculptureId == self.sculptureConfig['sculptureId']:
					data['sculptures'][sculptureId]['modules'] = {}
					for moduleId in self.sculptureModules:
						data['sculptures'][sculptureId]['modules'][moduleId] = self.sculptureModules[moduleId].getCurrentStateData()
			data['globalInputs'] = {}
			for inputInstanceId in self.globalInputs:
				data['globalInputs'][inputInstanceId] = self.globalInputs[inputInstanceId].getCurrentStateData()
		return data


