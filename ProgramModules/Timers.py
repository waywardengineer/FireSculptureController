from threading import Timer, Thread, Event

class Timer():
	class TimerThread(Thread):
		def __init__(self, parent):
			Thread.__init__(self)
			self.parent = parent
		def run(self):
			while not self.parent.stopEvent.wait(self.parent.interval / 1000.):
				self.parent.doFunction()
	def __init__(self, repeating, interval, function, args = False):
		self.stopEvent = Event()
		self.function = function
		self.repeating = repeating
		self.args = args
		thread = Timer.TimerThread(self)
		if repeating:
			self.interval = 50
			thread.start()
			self.interval = interval
		else:
			self.interval = interval
			thread.start()
	def stop(self):
		self.stopEvent.set()
	def changeInterval(self, interval):
		self.interval = interval
	def doFunction(self):
		if self.args:
			self.function(*self.args)
		else:
			self.function()
		if not self.repeating:
			self.stop()