class DataChannelManager():
	def __init__(self, sculptureConfigData):
		self.adaptors = {}
		self.dataChannels = {}
		adaptorModules = __import__('Adaptors')
		protocolModules = __import__('Protocols')
		for adaptorConfig in sculptureConfigData['adaptors']:
			adaptorClassName = adaptorConfig['type'][0].upper() + adaptorConfig['type'][1:] + 'Adaptor'
			adaptorClass = getattr(adaptorModules, adaptorClassName)
			self.adaptors[adaptorConfig['id']] = adaptorClass(adaptorConfig)
		for moduleConfig in sculptureConfigData['modules']:
			protocolClassName = moduleConfig['protocol']['type'][0].upper() + moduleConfig['protocol']['type'][1:] + 'Protocol'
			protocolClass = getattr(protocolModules, protocolClassName)
			self.dataChannels[moduleConfig['id']] = protocolClass(self.adaptors[moduleConfig['adaptor']], moduleConfig['protocol']['mapping'])
	def send(self, moduleId, data):
		self.dataChannels[moduleId].send(data)