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
		for moduleConfig in self.sculptureConfig['modules']:
			sculptureModuleClass = getattr(SculptureModules, moduleConfig['moduleType'] + 'Module')
			self.sculptureModules[moduleConfig['id']] = sculptureModuleClass(self.dataChannelManager, self.inputManager, moduleConfig)
	def doCommand(self, command):
		function = getattr(self, command.pop(0))
		function(*command)
		
	def addPattern(self, moduleId, *args):
		self.sculptureModules[moduleId].addPattern(*args)
	


