''' An input is anything that creates a value for patterns to use. These can be numerical parameters(which will be set by the GUI), physical devices,
keyboard bindings, timers, audio pulse thingeys, etc. There will be several broad types such as pulse and value, and any input of the same type 
will be interchangeable
''' 
from ProgramModules.Timers import Timer

class InputCollectionWrapper(object):
	def __init__(self, inputParamData):
		self.inputParamData = inputParamData
	def __getattr__(self, attr):
		return self.inputParamData[attr]
	def replaceInput (self, patternInputId, inputObj):
		self.inputParamData[patternInputId] = inputObj


class InputBase():
	def __init__(self, params):
		self.params = params
		if 'default' in params.keys():
			self.inputValues = [params['default']]
		else:
			self.inputValues = [False]
		if not 'scope' in params.keys():
			self.params['scope'] = 'local'
		self.outputValue = False
		self.instanceId = 0
		self.persistant = False

	def setInstanceId(self, id):
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
	def getCurrentStateData(self):
		output = self.params
		self.updateValue()
		output['currentValue'] = self.outputValue
		output['instanceId'] = self.instanceId
		return output
	def stop(self):
		pass
	def isPersistant(self):
		return self.persistant


class TimerPulseInput(InputBase):
	def __init__(self, *args):
		InputBase.__init__(self, *args)
		self.timer = Timer(True, self.inputValues[0], getattr(self, 'sendMessage'))
	def stop(self):
		self.timer.stop()
	def sendMessage(self):
		appMessenger.putMessage('pulse%s' %(self.instanceId), True)
	def setInputValue(self, *args):
		InputBase.setInputValue(self, *args)
		self.timer.changeInterval(self.inputValues[0])


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




		