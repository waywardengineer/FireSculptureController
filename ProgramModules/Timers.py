from threading import Thread, Event

class Timer():
	class TimerThread(Thread):
		def __init__(self, parent, interval):
			Thread.__init__(self)
			self.parent = parent
			self.waitEvent = Event()
			self.functionQueued = True
			self.interval = interval
		def run(self):
			if self.parent.repeating:
				self.parent.doFunction()
			while not self.parent.stopEvent.isSet():
				self.waitEvent.wait(self.interval / 1000.)
				if self.functionQueued:
					self.parent.doFunction()
					self.functionQueued = False
				if self.parent.repeating:
					self.restartInternal()
					
		def restartInternal(self):
			self.waitEvent.clear()
			self.functionQueued = True
		
		
		def restartExternal(self):
			self.functionQueued = False
			self.waitEvent.set()
			self.restartInternal()


					
	def __init__(self, repeating, interval, function, args = False):
		self.function = function
		self.repeating = repeating
		self.args = args
		self.stopEvent = Event()
		self.thread = Timer.TimerThread(self, interval)
		self.thread.start()

	def stop(self):
		self.fireFunction = False
		self.repeating = False
		self.thread.waitEvent.set()
		self.stopEvent.set()
	
	
	def refresh(self):
		self.thread.restartExternal()
	
	def changeInterval(self, interval):
		self.thread.interval = interval
	def doFunction(self):
		if self.args:
			self.function(*self.args)
		else:
			self.function()
