''' Creates instances of adaptor and protocol objects and passes data to them
One instance of this in the program seems to make more sense than one instance per module for now,
due to adaptors needing to serve multiple data channels in some cases
'''
from threading import Thread, Event

class DataChannelManager():
	class AdaptorThread(Thread):
		def __init__(self, adaptorObj):
			Thread.__init__(self)
			self.adaptorObj = adaptorObj
			self.data = False
			self.stopEvent = Event()
		
		def run(self):
			while not self.stopEvent.isSet():
				if self.data:
					if self.adaptorObj.transmitData(self.data):
						self.data = False
		
		def transmitData(self, data):
			self.data = data
			return True
					
		def stop(self):
			self.stopEvent.set()
			
		def connect(self):
			return self.adaptorObj.connect()
		
		
	def __init__(self, sculptureConfigData):
		self.adaptors = {}
		self.dataChannels = {}
		adaptorModules = __import__('ProgramModules.Adaptors')
		protocolModules = __import__('ProgramModules.Protocols')
		for adaptorId in sculptureConfigData['adaptors']:
			adaptorConfig = sculptureConfigData['adaptors'][adaptorId]
			adaptorConfig['adaptorId'] = adaptorId
			adaptorClassName = adaptorConfig['type'][0].upper() + adaptorConfig['type'][1:] + 'Adaptor'
			adaptorClass = getattr(adaptorModules, adaptorClassName)
			self.adaptors[adaptorId] = adaptorClass(adaptorConfig)
			# self.adaptors[adaptorId] = DataChannelManager.AdaptorThread(adaptorClass(adaptorConfig))
			# self.adaptors[adaptorId].start()
		for moduleId in sculptureConfigData['modules']:
			moduleConfig = sculptureConfigData['modules'][moduleId]
			protocolClassName = moduleConfig['protocol']['type'][0].upper() + moduleConfig['protocol']['type'][1:] + 'Protocol'
			protocolClass = getattr(protocolModules, protocolClassName)
			self.dataChannels[moduleId] = protocolClass(self.adaptors[moduleConfig['adaptor']], moduleConfig['protocol']['mapping'])
	def send(self, moduleId, data):
		return self.dataChannels[moduleId].send(data)
		
	def stop(self):
		for adaptorId in self.adaptors:
			self.adaptors[adaptorId].stop()
			
	def updateSerialConnection(self, adaptorId, data):
		return self.adaptors[adaptorId].updateSerialConnection(data)
	