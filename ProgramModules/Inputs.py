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
		print params
		self.outputValue = False
		self.instanceId = 0
		self.persistant = False
		if not 'settings' in self.params.keys():
			self.params['settings'] = []
		for settingIndex in range(len(self.params['settings'])):
			
			if 'default' in self.params['settings'][settingIndex].keys():
				value = self.params['settings'][settingIndex]['default']
			else:
				value = 0
			self.params['settings'][settingIndex]['currentSetting'] = value
	def setInstanceId(self, id):
		self.instanceId = id
	def setInputValue(self, value, settingIndex = 0):
		setting = self.params['settings'][settingIndex]
		value = float(value)
		if 'min' in setting.keys():
			if value < setting['min']:
				value = setting['min']
		if 'max' in setting.keys():
			if value > setting['max']:
				value = setting['max']
		print value
		self.params['settings'][settingIndex]['currentSetting'] = value
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
		self.params['settings'][0]['name'] = 'Interval(ms)'
		self.params['settings'][0]['type'] = 'param'
		self.timer = Timer(True, self.params['settings'][0]['currentSetting'], getattr(self, 'sendMessage'))
	def stop(self):
		self.timer.stop()
	def sendMessage(self):
		appMessenger.putMessage('pulse%s' %(self.instanceId), True)
	def setInputValue(self, *args):
		InputBase.setInputValue(self, *args)
		self.timer.changeInterval(self.params['settings'][0]['currentSetting'])


class AlwaysOnPulseInput(InputBase):
	def updateValue(self):
		self.outputValue = True


class BasicParamInput(InputBase):
	def __init__(self, *args):
		InputBase.__init__(self, *args)
		self.params['settings'][0]['name'] = 'Value'
		self.params['settings'][0]['type'] = 'param'
		if not 'min' in self.params['settings'][0].keys():
			self.params['settings'][0]['min'] = 0
		if not 'max' in self.params['settings'][0].keys():
			self.params['settings'][0]['max'] = 100
		if not 'default' in self.params['settings'][0].keys():
			self.params['settings'][0]['currentSetting'] = self.params['settings'][0]['min']
	def updateValue(self):
		self.outputValue = self.inputValues[0]


class DiscreteParamInput(BasicParamInput):
	def updateValue(self):
		self.outputValue = int(float(self.params['settings'][0]['currentSetting']) + 0.5)




		