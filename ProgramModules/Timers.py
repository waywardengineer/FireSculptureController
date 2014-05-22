from threading import Timer, Thread, Event

class Timer():
	class TimerThread(Thread):
		def __init__(self, parent):
			Thread.__init__(self)
			self.parent = parent
		def run(self):
			while not self.parent.stopEvent.wait(self.parent.interval / 1000.):
				if self.parent.fireFunction:
					self.parent.doFunction()
					
	def __init__(self, repeating, interval, function, args = False):
		self.function = function
		self.repeating = repeating
		self.args = args
		self.fireFunction = True
		self.interval = interval
		self.startThread()

	def startThread(self):
		self.stopEvent = Event()
		thread = Timer.TimerThread(self)
		if self.repeating:
			intervalSetting = self.interval
			self.interval = 50
			thread.start()
			self.interval = intervalSetting
		else:
			thread.start()


	def stop(self):
		self.stopEvent.set()
	
	def refresh(self):
		self.fireFunction = False
		self.stop()
		self.fireFunction = True
		self.startThread()
		
	
	
	def changeInterval(self, interval):
		self.interval = interval
	def doFunction(self):
		if self.args:
			self.function(*self.args)
		else:
			self.function()
		if not self.repeating:
			self.stop()