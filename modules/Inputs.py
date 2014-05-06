from threading import Timer, Thread, Event

class InputBase():
	def __init__(self, id):
		self.interval = ParamInput
		self.id = id

	def getParamInputs(self):
		pass
	def setParam(self, paramIndex, value):
		pass
	def getOutputs(self, index = -1):
		if index >= 0:
			return self.values[index]
		else:
			return self.values
		
		
class TimerInput(InputBase):
	class TimerThread(Thread):
		def __init__(self, parent, event):
			Thread.__init__(self)
			self.stopped = event
			self.delayInput = parent.paramInputs[0]
			self.parent = parent
		def run(self):
			while not self.stopped.wait(self.delayInput.getOutputs(0) / 1000):
				self.parent.sendMessage()
	def __init__(self, id):
		self.paramInputs = [ParamInput(False, 0, 2000, "Pulse Time")]
		self.id = id
		self.startTimer()
	def startTimer(self):
		self.stopEvent = Event()
		thread = TimerInput.TimerThread(self, self.stopEvent)
		thread.start()
	def stopTimer(self):
		self.stopEvent.set()
	def sendMessage(self):
		appMessenger.putMessage('patternTimers', self.id)
		
class ParamInput(InputBase):
	def __init__(self, id, min, max, name):
		self.id = id
		self.min = min
		self.max = max
		self.name = name
		self.values = [min + (max - min) / 2]
		
		