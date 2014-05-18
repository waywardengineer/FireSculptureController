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
	def __init__(self, configParams, instanceId):
		self.configParams = dict(self.defaultParams, **configParams)
		self.outputs = []
		self.inputs = []
		self.instanceId = instanceId
		if 'inputs' in self.configParams.keys():
			for inputParam in self.configParams['inputs']:
				self.inputs.append(InputOutputParam(inputParam))
		if 'outputs' in self.configParams.keys():
			for outputParamIndex in range(len(self.configParams['outputs'])):
				self.outputs.append(InputOutputParam(self.configParams['outputs'][outputParamIndex], self.instanceId, outputParamIndex))


	def setInputValue(self, value, settingIndex = 0):
		inputs[settingIndex].setValue(value)



	def getValue(self, outputIndex = 0):
		self.updateOutputValues()
		return self.outputs[outputIndex].getValue()


	def getId(self):
		return self.instanceId


	def updateOutputValues(self):
		pass


	def getCurrentStateData(self):
		self.updateOutputValues()
		data = self.configParams.copy()
		data['inputs'] = []
		data['outputs'] = []
		for input in self.inputs:
			data['inputs'].append(input.getCurrentStateData())
		for output in self.outputs:
			data['outputs'].append(output.getCurrentStateData())
		data['instanceId'] = self.instanceId
		return data


	def stop(self):
		pass


	def isPersistant(self):
		return False


class TimerPulseInput(InputBase):
	def __init__(self, *args):
		self.defaultParams = {
													'inputs' : [{'type' : 'value', 'description' : 'Interval(ms)'}],
													'outputs' : [{'type' : 'pulse'}]
													}
		InputBase.__init__(self, *args)
		self.timer = Timer(True, self.inputs[0].getValue(), getattr(self, 'sendMessage'))

	def stop(self):
		self.timer.stop()


	def sendMessage(self):
		appMessenger.putMessage('pulse%s_0' %(self.instanceId), True)


	def setInputValue(self, *args):
		InputBase.setInputValue(self, *args)
		self.timer.changeInterval(self.inputs[0].getValue())


class OnOffPulseInput(InputBase):
	def __init__(self, *args):
		self.defaultParams = {
													'inputs' : [{'type' : 'pulse', 'description' : 'On/Off', 'default' : True,  'sendMessageOnChange' : True}],
													'outputs' : [{'type' : 'pulse'}]
													}
		InputBase.__init__(self, *args)


class ValueInput(InputBase):
	def __init__(self, *args):
		self.defaultParams = {
													'inputs' : [{'type' : 'value', 'description' : 'Value', 'default' : 0, 'min' : 0, 'max' : 100}],
													'outputs' : [{'type' : 'value'}]
													}
		InputBase.__init__(self, *args)
		
	def updateOutputValues(self):
		self.outputs[0].setValue(self.inputs[0].getValue())


class IntValueInput(InputBase):
	def __init__(self, *args):
		self.defaultParams = {
													'inputs' : [{'type' : 'value', 'subType' : 'int', 'description' : 'Value', 'default' : 0, 'min' : 0, 'max' : 100}],
													'outputs' : [{'type' : 'value'}]
													}
		InputBase.__init__(self, *args)
		
	def updateOutputValues(self):
		self.outputs[0].setValue(self.inputs[0].getValue())


		
		

class MultiInput(InputBase):
	def __init__(self, *args):
		InputBase.__init__(self, *args)

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

	def __init__(self, params, *args):
		self.defaultParams = {'host' : ('127.0.0.2', 8000), 'callbackAddresses' : {'button' : ['/1/button1', '/1/button2', '/1/button3'], 'value' : ['/1/value1', '/1/value2', '/1/value3']}}
		params = dict(self.defaultParams, **params)
		params['outputs'] = []
		for buttonAddress in params['callbackAddresses']['button']:
			params['outputs'].append({'type' : 'pulse', 'description' : 'Button ' + buttonAddress, 'sendMessageOnChange' : True})
		for valueAddress in params['callbackAddresses']['value']:
			params['outputs'].append({'type' : 'value', 'description' : 'Value ' + valueAddress, 'sendMessageOnChange' : True})
			
		MultiInput.__init__(self, params, *args)
		self.callbackLinkList = []
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
		outputIndex = self.getOutputIndexFromAddress(path, 'button')
		self.outputs[outputIndex].setValue(args[0])
		appMessenger.putMessage('dataInputChanged', [self.instanceId, outputIndex, self.outputValues[outputIndex]])


	def doValueCallback(self, path, tags, args, source):
		outputIndex = self.getOutputIndexFromAddress(path, 'value')
		self.outputs[outputIndex].setValue(args[0])
		appMessenger.putMessage('dataInputChanged', [self.instanceId, outputIndex, self.outputValues[outputIndex]])


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


class InputOutputParam():
	def __init__(self, params, parentId = 0, indexId = 0):
		defaultParams = {'description' : 'Value', 'type' : 'value', 'subtype' : False, 'min' : False, 'max' : False, 'default' : 0, 'sendMessageOnChange' : False}
		self.params = dict(defaultParams, **params)
		self.value = self.params['default']
		type = self.params['type']
		subType = self.params['subtype']
		if self.params['subtype']:
			constrainValueFunctionName = 'constrain' + subtype[0].upper() + subtype[1:] + type[0].upper() + type[1:] 
		else:
			constrainValueFunctionName = 'constrain' + type[0].upper() + type[1:]
		self.constrainValueFunction = getattr(self, constrainValueFunctionName)
	def getValue(self):
		return self.value
	def setValue(self, value):
		self.value = self.constrainValueFunction(value)
		if self.params['sendMessageOnChange']:
			appMessenger.putMessage("%s%s_%s" %(self.params['type'], self.parentId, self.indexId), self.value)
	def constrainValue(self, value):
		value = float(value)
		if self.params['min']:
			if value < self.params['min']:
				value = self.params['min']
		if self.params['max']:
			if value > self.params['max']:
				value = self.params['max']
		return value
	def constrainIntValue(self, value):
		value = int(float(self.constrainValue(value)) + 0.5)
		return value
	def constrainPulse(self, value):
		if (value):
			return True
		else:
			return False
			
	def getCurrentStateData(self):
		data = self.params.copy()
		data['currentValue'] = self.value
		return data

