''' An input is anything that creates a value for patterns to use. These can be numerical parameters(which will be set by the GUI), physical devices,
keyboard bindings, timers, audio pulse thingeys, etc. There will be several broad types such as pulse and value, and any input of the same type 
will be interchangeable
''' 
from ProgramModules.Timers import Timer
from threading import Thread, Event

outputTypes = ['pulse', 'toggle', 'value']

availableInputTypes = {'pulse' : ['timer', 'onOff', 'button'], 'value' : ['', 'int'], 'multi' : ['osc']}
inputTypeSettings = {
	'TimerPulseInput' : {
		'longDescription' : 'Timer pulse input, variable timing',
		'shortDescription' : 'Timer Pulse',
		'inputs' : [{'type' : 'value', 'description' : 'Interval(ms)', 'initInputData' : [['int', 'Maximum time(ms)', 'max'], ['int', 'Minimum time(ms)', 'min']]}],
		'outputs' : [{'type' : 'pulse', 'sendMessageOnChange' : True}]
	},
	'OnOffPulseInput' : {
		'longDescription' : 'On/off toggle control',
		'shortDescription' : 'On/off control',
		'inputs' : [{'type' : 'toggle', 'description' : '', 'default' : True}],
		'outputs' : [{'type' : 'toggle', 'sendMessageOnChange' : True}]
	},
	'ButtonPulseInput' : {
		'longDescription' : 'On/off instantaneous button control',
		'shortDescription' : 'Button Pulse control',
		'inputs' : [{'type' : 'pulse', 'description' : '', 'default' : False}],
		'outputs' : [{'type' : 'pulse', 'sendMessageOnChange' : True}]
	},
	'ValueInput' : {
		'longDescription' : 'Variable value input, can be decimal',
		'shortDescription' : 'Value setting',
		'inputs' : [{'type' : 'value', 'description' : 'Value', 'default' : 0, 'min' : 0, 'max' : 100}],
		'outputs' : [{'type' : 'value'}]
	},
	'IntValueInput' : {
		'longDescription' : 'Variable value input, integer',
		'shortDescription' : 'Value setting',
		'inputs' : [{'type' : 'value', 'subType' : 'int', 'description' : 'Value', 'default' : 0, 'min' : 0, 'max' : 100}],
		'outputs' : [{'type' : 'value'}]
	},
	'OscMultiInput' : {
		'longDescription' : 'OpenSoundControl server', 
		'shortDescription' : 'OSC server', 
		'inputs' : [],
		'host' : '127.0.0.2', 
		'port' : 8000, 
		'initInputData' : [['text', 'Host', 'host'], ['int', 'Port', 'port'], ['text', 'Button addresses(separated by space)', 'buttonAddressesString'], ['text', 'Value addresses(separated by space)', 'valueAddressesString']],
		'callbackAddresses' : {'pulse' : ['/1/button1', '/1/button2', '/1/button3'], 'toggle' : [], 'value' : ['/1/value1', '/1/value2', '/1/value3']}
	}

}

try:
	from OSC import OSCServer,OSCClient, OSCMessage
except:
	inputTypeSettings['OscMultiInput']['unavailable'] = True


class InputCollectionWrapper(object):
	def __init__(self, inputCollection):
		self.inputCollection = inputCollection
		


	def __getattr__(self, patternInputId):
		return self.inputCollection[patternInputId]['inputObj'].getValue(self.inputCollection[patternInputId]['outputIndexOfInput'])

	def getBinding(self, patternInputId):
		return [self.inputCollection[patternInputId]['inputObj'].getId(), self.inputCollection[patternInputId]['outputIndexOfInput']]
		
	def doCommand(self, args):
		function = getattr(self.inputCollection[args.pop(0)]['inputObj'], args.pop(0))
		return function(*args)
	
	def replaceInput (self, patternInputId, inputObj, outputIndexOfInput = 0):
		self.inputCollection[patternInputId]['inputObj'] = inputObj
		self.inputCollection[patternInputId]['outputIndexOfInput'] = outputIndexOfInput


class InputBase():
	def __init__(self, configParams, instanceId):
		self.defaultParams = inputTypeSettings[self.__class__.__name__]
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
		print value
		self.inputs[settingIndex].setValue(value)
		self.updateOutputValues()


	def getValue(self, outputIndex = 0):
		self.updateOutputValues()
		return self.outputs[outputIndex].getValue()


	def getId(self):
		return self.instanceId


	def updateOutputValues(self):
		if len(self.outputs) == len(self.inputs):
			for i in range(len(self.outputs)):
				self.outputs[i].setValue(self.inputs[i].getValue())


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
		InputBase.__init__(self, *args)
		self.timer = Timer(True, self.inputs[0].getValue(), getattr(self, 'sendPulse'))

	def stop(self):
		self.timer.stop()

	def refresh(self):
		self.timer.refresh()

	def sendPulse(self):
		self.outputs[0].setValue(True)


	def setInputValue(self, *args):
		InputBase.setInputValue(self, *args)
		self.timer.changeInterval(self.inputs[0].getValue())
		
	def updateOutputValues(self):
		pass


class OnOffPulseInput(InputBase):
	pass

class ButtonPulseInput(InputBase):
	pass

class ValueInput(InputBase):
	pass

class IntValueInput(InputBase):
	pass


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
		self.defaultParams = {'host' : '127.0.0.2', 'port' : 8000, 'callbackAddresses' : {'pulse' : ['/1/button1', '/1/button2', '/1/button3'], 'toggle' : [], 'value' : ['/1/value1', '/1/value2', '/1/value3']}}
		callbackAddresses = {}
		callbacksInStringForm = False
		for outputType in outputTypes:
			callbackAddresses[outputType] = []
			key = outputType + 'AddressString'
			if key in params.keys():
				callbacksInStringForm = True
				callbackAddresses[outputType] = params[key].split()
				del params[key]
		params = dict(self.defaultParams, **params)
		if callbacksInStringForm:
			params['callbackAddresses'] = callbackAddresses
		params['outputs'] = []
		for outputType in outputTypes:
			for address in params['callbackAddresses'][outputType]:
				params['outputs'].append({'type' : outputType, 'description' : outputType[0].upper() + outputType[1:] + ' ' + address, 'sendMessageOnChange' : True})
			
		MultiInput.__init__(self, params, *args)
		self.callbackLinkList = []
		self.stopEvent = Event()
		self.server = OscMultiInput.OscServerThread((self.configParams['host'], self.configParams['port']), self.stopEvent)
		self.buildCallbackLinkList()
		self.server.setCallBacks(self.callbackLinkList)
		self.server.start()
		self.persistant = True


	def buildCallbackLinkList(self):
		for callbackType in outputTypes:
			if callbackType in self.configParams['callbackAddresses'].keys():
				function = getattr(self, 'do' + callbackType[0].upper() + callbackType[1:] + 'Callback')
				for callbackAddress in self.configParams['callbackAddresses'][callbackType]:
					self.callbackLinkList.append([callbackAddress, function])


	def stop(self):
		self.stopEvent.set()

	def doPulseCallback(self, path, tags, args, source):
		outputIndex = self.getOutputIndexFromAddress(path, 'pulse')
		self.outputs[outputIndex].setValue(args[0])
		appMessenger.putMessage('dataInputChanged', [self.instanceId, outputIndex, self.outputs[outputIndex].getValue()])

	def doToggleCallback(self, path, tags, args, source):
		outputIndex = self.getOutputIndexFromAddress(path, 'toggle')
		self.outputs[outputIndex].setValue(args[0])
		appMessenger.putMessage('dataInputChanged', [self.instanceId, outputIndex, self.outputs[outputIndex].getValue()])

	def doValueCallback(self, path, tags, args, source):
		outputIndex = self.getOutputIndexFromAddress(path, 'value')
		self.outputs[outputIndex].setValue(args[0])
		appMessenger.putMessage('dataInputChanged', [self.instanceId, outputIndex, self.outputs[outputIndex].getValue()])


	def getOutputIndexFromAddress(self, path, callbackType):
		if path[:-2].isdigit():
			addrNum = int(path[:-2])
		elif path[:-1].isdigit():
			addrNum = int(path[:-1])
		else:
			return False
		index = addrNum-1
		done = False
		for outputType in outputTypes:
			if callbackType == outputType:
				done = True
			if not done:
				index += len(self.configParams[outputType])
		return index


class InputOutputParam():
	def __init__(self, params, parentId = 0, indexId = 0):
		defaultParams = {'description' : '', 'type' : 'value', 'subtype' : False, 'min' : False, 'max' : False, 'default' : 0, 'sendMessageOnChange' : False, 'toggleTimeOut' : 100}
		self.params = dict(defaultParams, **params)
		self.parentId = parentId
		self.indexId = indexId
		type = self.params['type']
		subType = self.params['subtype']
		self.timer = False
		if self.params['subtype']:
			constrainValueFunctionName = 'constrain' + subtype[0].upper() + subtype[1:] + type[0].upper() + type[1:] 
		else:
			constrainValueFunctionName = 'constrain' + type[0].upper() + type[1:]
		self.constrainValueFunction = getattr(self, constrainValueFunctionName)
		self.value = False
		self.setValue(self.params['default'])
	def getValue(self):
		return self.value
	def setValue(self, newValue):
		newValue = self.constrainValueFunction(newValue)
		if not self.value == newValue:
			self.value = newValue
			if self.params['sendMessageOnChange']:
				appMessenger.putMessage("output%s_%s" %(self.parentId, self.indexId), self.value)
		if self.params['type'] == 'pulse' and newValue:
			if self.timer:
				self.timer.refresh()
			else:
				self.timer = Timer(False, self.params['toggleTimeOut'], getattr(self, 'setValue'), [False])

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
		if value:
			return True
		else:
			return False
	def constrainToggle(self, value):
		return self.constrainPulse(value)
			
	def getCurrentStateData(self):
		data = self.params.copy()
		data['currentValue'] = self.value
		return data

