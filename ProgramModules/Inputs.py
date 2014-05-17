''' An input is anything that creates a value for patterns to use. These can be numerical parameters(which will be set by the GUI), physical devices,
keyboard bindings, timers, audio pulse thingeys, etc. There will be several broad types such as pulse and value, and any input of the same type 
will be interchangeable
''' 
from ProgramModules.Timers import Timer

try:
	from OSC import OSCServer,OSCClient, OSCMessage
	from time import sleep
	import types
	from threading import Thread, Event
except:
	pass

class InputCollectionWrapper(object):
	def __init__(self, inputParamData):
		self.inputParamData = inputParamData


	def __getattr__(self, attr):
		return self.inputParamData[attr]


	def replaceInput (self, patternInputId, inputObj):
		self.inputParamData[patternInputId] = inputObj


class InputBase():
	def __init__(self, configParams):
		self.configParams = configParams
		print self.configParams
		self.outputValues = [False]
		self.outputValueTypes = ['value']
		self.inputValues = []
		self.inputValueTypes = []
		self.instanceId = 0
		self.persistant = False
		if not 'inputSettings' in self.configParams.keys():
			self.configParams['inputSettings'] = []
		for settingIndex in range(len(self.configParams['inputSettings'])):
			if 'default' in self.configParams['inputSettings'][settingIndex].keys():
				value = self.configParams['inputSettings'][settingIndex]['default']
			else:
				value = 0
			self.inputValues.append(value)


	def setInstanceId(self, id):
		self.instanceId = id


	def setInputValue(self, value, settingIndex = 0):
		setting = self.configParams['inputSettings'][settingIndex]
		value = float(value)
		if 'min' in setting.keys():
			if value < setting['min']:
				value = setting['min']
		if 'max' in setting.keys():
			if value > setting['max']:
				value = setting['max']
		self.inputValues[settingIndex] = value


	def getValue(self, outputIndex = 0):
		self.updateOutputValues()
		return self.outputValues[0]


	def getId(self):
		return self.instanceId


	def updateOutputValues(self):
		pass


	def getCurrentStateData(self):
		self.updateOutputValues()
		output = self.configParams.copy()
		print output
		for settingIndex in range(len(output['inputSettings'])):
			output['inputSettings'][settingIndex]['currentValue'] = self.inputValues[settingIndex]
		output['currentOutputValues'] = self.outputValues
		output['instanceId'] = self.instanceId
		return output


	def stop(self):
		pass


	def isPersistant(self):
		return self.persistant


class TimerPulseInput(InputBase):
	def __init__(self, *args):
		InputBase.__init__(self, *args)
		self.configParams['inputSettings'][0]['name'] = 'Interval(ms)'
		self.configParams['inputSettings'][0]['type'] = 'param'
		self.timer = Timer(True, self.inputValues[0], getattr(self, 'sendMessage'))


	def stop(self):
		self.timer.stop()


	def sendMessage(self):
		appMessenger.putMessage('pulse%s' %(self.instanceId), True)


	def setInputValue(self, *args):
		InputBase.setInputValue(self, *args)
		self.timer.changeInterval(self.inputValues[0])


class AlwaysOnPulseInput(InputBase):
	def updateOutputValues(self):
		self.outputValues[0] = True


class BasicParamInput(InputBase):
	def __init__(self, *args):
		InputBase.__init__(self, *args)
		self.configParams['inputSettings'][0]['name'] = 'Value'
		self.configParams['inputSettings'][0]['type'] = 'param'
		if not 'min' in self.configParams['inputSettings'][0].keys():
			self.configParams['inputSettings'][0]['min'] = 0
		if not 'max' in self.configParams['inputSettings'][0].keys():
			self.configParams['inputSettings'][0]['max'] = 100
		if not 'default' in self.configParams['inputSettings'][0].keys():
			self.inputValues[0] = self.configParams['inputSettings'][0]['min']
	def updateOutputValues(self):
		self.outputValues[0] = self.inputValues[0]


class DiscreteParamInput(BasicParamInput):
	def updateOutputValues(self):
		self.outputValues[0] = int(float(self.inputValues[0]) + 0.5)


		
		

class MultiInput(InputBase):
	def __init__(self, inputManager, *args):
		InputBase.__init__(self, *args)
		self.inputManager = inputManager
		self.childInputs = []
	def buildChildInputs(self):
		for outputIndex in range(len(self.outputValueTypes)):
			self.childInputs.append(self.inputManager.registerUsage(self.instanceId, self.inputManager.createNewInput({'type' : self.outputValueTypes[outputIndex], 'subtype' : 'driven'}), outputIndex))


class OscMultiInput(MultiInput):
	class OscServerThread(Thread):
		def __init__(self, host, stopEvent):
			Thread.__init__(self)
			self.server = OSCServer(host)
			self.stopEvent = stopEvent
		def setCallBacks(self, callBacks):
			for callBack in callBacks:
				self.server.addMsgHandler(callBack[0], callBack[1])
		def run(self):
			while not self.stopEvent.is_set():
				self.server.handle_request()
			self.server.close()

	def __init__(self, *args):
		MultiInput.__init__(self, *args)
		self.callbackLinkList = []
		defaults = {"host" : ("127.0.0.2", 8000), 'callbackAddresses' : {'button' : ['/1/button1', '/1/button2', '/1/button3'], 'value' : ['/1/value1', '/1/value2', '/1/value3']}}
		self.configParams = dict(defaults, **self.configParams.copy())
		self.outputValueTypes = ['pulse' for i in range(len(self.configParams['callbackAddresses']['button']))] + ['param' for i in range(len(self.configParams['callbackAddresses']['value']))]
		self.stopEvent = Event()
		self.server = OscMultiInput.OscServerThread(self.configParams['host'], self.stopEvent)
		self.buildCallbackLinkList()
		self.server.setCallBacks(self.callbackLinkList)
		self.server.start()
		self.persistant = True


	def buildCallbackLinkList(self):
		for callbackType in ['value', 'button']:
			if callbackType in self.configParams['callbackAddresses'].keys():
				function = getattr(self, 'do' + callbackType[0].upper() + callbackType[1:] + 'Callback')
				for callbackAddress in self.configParams['callbackAddresses'][callbackType]:
					self.callbackLinkList.append([callbackAddress, function])


	def stop(self):
		self.stopEvent.set()

	def doButtonCallback(self, path, tags, args, source):
		print path
		outputIndex = self.getOutputIndexFromAddress(path, 'button')
		if args[0] == 1.0:
			self.outputValues[outputIndex] = True
		else:
			self.outputValues[outputIndex] = False
		self.childInputs[outputIndex].setValue(args[0])



	def doValueCallback(self, path, tags, args, source):
		print path
		outputIndex = self.getOutputIndexFromAddress(path, 'value')
		self.outputValues[outputIndex] = args[0]
		self.updateChildInputs(outputIndex)
		self.childInputs[outputIndex].setValue(args[0])


	def getOutputIndexFromAddress(self, path, outputType):
		if path[:-2].isdigit():
			addrNum = int(path[:-2])
		elif path[:-1].isdigit():
			addrNum = int(path[:-1])
		else:
			return False
		if outputType == 'value':
			index = addrNum + len(self.configParams['callbackAddresses']['button']) - 1
		elif outputType == 'button':
			index = addrNum - 1
		else:
			return false
		return index

class DrivenPulseInput(InputBase):
	def setValue(self, value):
		self.outputValues[0] = value
		if value:
			appMessenger.putMessage('pulse%s' %(self.instanceId), True)

class DrivenParamInput(InputBase):
	def setValue(self, value):
		self.outputValues[0] = value


