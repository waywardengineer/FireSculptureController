import json
import os

from ProgramModules.DataChannelManager import DataChannelManager
from ProgramModules.InputManager import InputManager
from ProgramModules import SculptureModules



class SculptureController():
	def __init__(self):
		definitionFileDirectory = 'sculptureDefinitions'
		self.sculptureDefinitions = {}
		for definitionFileName in os.listdir(definitionFileDirectory):
			try:
				definition = json.load(open("%s/%s" %(definitionFileDirectory, definitionFileName)))
				self.sculptureDefinitions[definition['sculptureId']] = definition
			except:
				pass
		self.doReset()



	def doReset(self):
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
		data = {'sculptures' : {}}
		if self.sculptureConfig:
			data['activeSculptureId'] = self.sculptureConfig['sculptureId']
		else:
			data['activeSculptureId'] = False
		if sculptureId:
			data['sculptures'][sculptureId] = {'modules' : False}
			if moduleId:
				data['sculptures'][sculptureId]['modules'] = {moduleId : {}}
				if self.sculptureConfig and sculptureId == self.sculptureConfig['sculptureId']:
					data['sculptures'][sculptureId]['modules'][moduleId] = self.sculptureModules[moduleId].getCurrentStateData(*args)
				return data
			data['sculptures'][sculptureId]['sculptureConfig'] = self.sculptureDefinitions[sculptureId]
			return data
		for sculptureId in self.sculptureDefinitions:
			data['sculptures'][sculptureId] = {'config' : self.sculptureDefinitions[sculptureId], 'modules' : False}
			if self.sculptureConfig and sculptureId == self.sculptureConfig['sculptureId']:
				data['sculptures'][sculptureId]['modules'] = {}
				for moduleId in self.sculptureModules:
					data['sculptures'][sculptureId]['modules'][moduleId] = self.sculptureModules[moduleId].getCurrentStateData()
		return data


