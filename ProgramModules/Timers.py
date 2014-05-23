from threading import Thread, Event
import timer

class Timer():
	class TimerThread(Thread):
		def __init__(self, parent):
			Thread.__init__(self)
			self.parent = parent
			self.waitEvent = Event()
			self.timer = timer.Timer(parent.interval*1000, self.waitEvent.set)
			self.doReset = False
		def run(self):
			self.timer.start()
			if self.parent.repeating:
				self.parent.doFunction()
			while not self.parent.stopEvent.isSet():
				while not self.waitEvent.isSet():
					pass
				if self.parent.fireFunction:
					self.parent.doFunction()
					self.parent.fireFunction = False
				if self.parent.repeating or self.doReset:
					self.waitEvent = Event()
					self.timer = timer.Timer(self.parent.interval*1000, self.waitEvent.set)
					self.parent.fireFunction = True
					self.timer.start()
					self.doReset = False

					
	def __init__(self, repeating, interval, function, args = False):
		self.function = function
		self.repeating = repeating
		self.args = args
		self.fireFunction = True
		self.interval = interval
		self.stopEvent = Event()
		self.thread = Timer.TimerThread(self)
		self.thread.start()

	def stop(self):
		self.fireFunction = False
		self.repeating = False
		self.thread.doReset = False
		self.thread.timer.stop()
		self.thread.waitEvent.set()
		self.stopEvent.set()
	
	def refresh(self):
		self.fireFunction = False
		self.thread.doReset = True
		self.thread.timer.stop()
		self.thread.waitEvent.set()
		self.fireFunction = True
		if self.repeating:
			self.doFunction()
	
	def changeInterval(self, interval):
		self.interval = interval
	def doFunction(self):
		if self.args:
			self.function(*self.args)
		else:
			self.function()
