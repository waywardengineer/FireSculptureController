''' Protocols take data from the program and convert it into a specific language for talking to the sculpture, then sends it over an adaptor. They are constructed with 
an adaptor instance, so each one has all the "stuff" for talking to the sculpture. Protocols to be added: Soma, OpenPixel, Tympani LED, Serpent LED, Helyx maybe, motor contollers
To send data, each takes a command like [ [address, data], [address2, data2], ...]. Each address is itself a list, usually corresponding to [row, column]. Data is also a list, with length 
depending on type of data
'''



class ProtocolBase():
	def __init__(self, adaptorObj, mapping):
		self.adaptorObj = adaptorObj
		self.mapping = mapping
		self.dataCache = ''
	def transmitData(self):
		if self.adaptorObj.transmitData(self.dataCache):
			self.dataCache = ''
	def send(self, data):
		for command in data:
			self.dataCache += self.formatData(command[0], command[1])
		self.transmitData()

class FlgRelayProtocol(ProtocolBase): #Poofer relay boards used on Serpent, Angel, Tympani, Mutopia
	def formatData(self, addr, data):   
		if data[0] in [True, '1', 1]:
			cmd = '1'
		else:
			cmd = '0'
		return "!%02X%s%s." %(self.mapping[addr[0]][addr[1]][0], self.mapping[addr[0]][addr[1]][1], cmd)

class TympaniLedProtocol(ProtocolBase): #Tympani Mobius Leds
	def formatData(self, command, value):   
		return "!%02X%01X%02X." %(self.mapping[command][0], self.mapping[command][1], int(value))
