''' Adaptors specify the interface to the hardware such as a serial bus, ethernet, or a dummy interface. They 
take the params needed to open the connection, send the already processed data over the connection,
(eventually) recieve data, and make sure it stays connected. '''


class SerialAdaptor():
	def __init__ (self, configData):
		pass
	def transmitData(self, data):
		print data
		return True

