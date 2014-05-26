from threading import Thread, Event
import time
class Timer():
	class TimerThread(Thread):
		def __init__(self, parent):
			Thread.__init__(self)
			self.parent = parent
		def run(self):
			while not self.parent.stopEvent.isSet():
				self.parent.waitEvent.wait(self.parent.interval / 1000.)
				self.parent.doFunction()
		
	def __init__(self, repeating, interval, function, args = False):
		self.function = function
		self.repeating = repeating
		self.args = args
		self.stopEvent = Event()
		self.waitEvent = Event()
		self.thread = Timer.TimerThread(self)
		self.interval = interval
		self.functionQueue = 1
		self.thread.start()

	def stop(self):
		self.functionQueue = -1
		self.repeating = False
		self.waitEvent.set()
		self.stopEvent.set()
	
	
	def refresh(self):
		self.functionQueue = 1
		self.waitEvent.set()
		self.waitEvent.clear()
		
	def changeInterval(self, interval):
		self.interval = interval
		
	def doFunction(self):
		if self.functionQueue == 0 or self.repeating:
			if self.args:
				self.function(*self.args)
			else:
				self.function()
		if self.functionQueue > -1:
			self.functionQueue -= 1
