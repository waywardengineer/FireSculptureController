''' An input is anything that creates a value for patterns to use. These can be numerical parameters(which will be set by the GUI), physical devices,
keyboard bindings, timers, audio pulse thingeys, etc. There will be several broad types such as pulse and value, and any input of the same type 
will be interchangeable
''' 


from threading import Timer, Thread, Event
class InputWrapper(object):
	def __init__(self, inputParamData):
		self.inputParamData = inputParamData
	def __getattr__(self, attr):
		return self.inputParamData[attr]
	def replaceInput (self, patternInputId, inputObj):
		self.inputParamData[patternInputId]['inputInstanceId'] = inputObj

		
class InputBase():
	def __init__(self, params):
		self.params = params
		if 'default' in params.keys():
			self.inputValues = [params['default']]
			print self.inputValues[0]
		else:
			self.inputValues = [False]
		self.outputValue = False
		self.instanceId = 0
	def setInstanceId(self, id):
		print "instance id set"
		self.instanceId = id
	def setInputValue(self, value, paramIndex = 0):
		if 'min' in params.keys:
			if value < params['min']:
				value = params['min']
		if 'max' in params.keys:
			if value > params['max']:
				value = params['max']
		self.inputValues[paramIndex] = value
	def getValue(self):
		self.updateValue()
		return self.outputValue
	def getId(self):
		return self.instanceId
	def updateValue(self):
		pass


class TimerPulseInput(InputBase):
	class TimerThread(Thread):
		def __init__(self, parent, event):
			Thread.__init__(self)
			self.stopped = event
			self.parent = parent
		def run(self):
			while not self.stopped.wait(self.parent.inputValues[0] / 1000.):
				self.parent.sendMessage()
	def __init__(self, *args):
		InputBase.__init__(self, *args)
		self.startTimer()
	def startTimer(self):
		self.stopEvent = Event()
		thread = TimerPulseInput.TimerThread(self, self.stopEvent)
		thread.start()
	def stopTimer(self):
		self.stopEvent.set()
	def sendMessage(self):
		appMessenger.putMessage('pulse%s' %(self.instanceId), True)
		#print "Pulse sent"

class AlwaysOnPulseInput(InputBase):
	def updateValue(self):
		self.outputValue = True


class BasicParamInput(InputBase):
	def __init__(self, *args):
		InputBase.__init__(self, *args)
		if not 'min' in self.params.keys():
			self.params['min'] = 0
		if not 'max' in self.params.keys():
			self.params['max'] = 100
		if not 'default' in self.params.keys():
			self.inputValues[0] = self.params['min']
	def updateValue(self):
		self.outputValue = self.inputValues[0]


class DiscreteParamInput(BasicParamInput):
	def updateValue(self):
		self.outputValue = int(float(self.inputValues[0]) + 0.5)




		