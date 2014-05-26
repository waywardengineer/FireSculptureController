''' An input is anything that creates a value for patterns to use. These can be numerical parameters(which will be set by the GUI), physical devices,
keyboard bindings, timers, audio pulse thingeys, etc. There will be several broad types such as pulse and value, and any input of the same type 
will be interchangeable
''' 
from ProgramModules.Timers import Timer
from ProgramModules import utils

from threading import Thread, Event
outputTypes = ['pulse', 'toggle', 'value']
import json
import time
availableInputTypes = {'pulse' : ['timer', 'onOff', 'button', 'audio'], 'value' : ['', 'int'], 'multi' : ['osc']}
inputParams = {
	'TimerPulseInput' : {
		'longDescription' : 'Timer pulse input, variable timing',
		'shortDescription' : 'Timer Pulse',
		'inputs' : [{'type' : 'value', 'subType' : 'int', 'description' : 'Interval(ms)', 'max' : 2000, 'min' : 50}],
		'outputs' : [{'type' : 'pulse', 'sendMessageOnChange' : True}]
	},
	'OnOffPulseInput' : {
		'longDescription' : 'On/off toggle control',
		'shortDescription' : 'On/off switch',
		'inputs' : [{'type' : 'toggle', 'description' : '', 'default' : True}],
		'outputs' : [{'type' : 'toggle', 'sendMessageOnChange' : True}]
	},
	'ButtonPulseInput' : {
		'longDescription' : 'On/off instantaneous button control',
		'shortDescription' : 'Button',
		'inputs' : [{'type' : 'pulse', 'description' : '', 'default' : False}],
		'outputs' : [{'type' : 'pulse', 'sendMessageOnChange' : True, 'toggleTimeOut' : 20}]
	},
	'ValueInput' : {
		'longDescription' : 'Variable value input, can be decimal',
		'shortDescription' : 'Value setting',
		'inputs' : [{'type' : 'value', 'description' : '', 'default' : 0, 'min' : 0, 'max' : 100}],
		'outputs' : [{'type' : 'value', 'min' : False, 'max' : False}]
	},
	'IntValueInput' : {
		'longDescription' : 'Variable value input, integer',
		'shortDescription' : 'Value setting',
		'inputs' : [{'type' : 'value', 'subType' : 'int', 'description' : '', 'default' : 0, 'min' : 0, 'max' : 100}],
		'outputs' : [{'type' : 'value', 'min' : False, 'max' : False}]
	},
	'OscMultiInput' : {
		'longDescription' : 'OpenSoundControl server', 
		'shortDescription' : 'OSC server', 
		'inputs' : [],
		'host' : '127.0.0.2', 
		'port' : 8000, 
		'initInputData' : [['text', 'Host', 'host'], ['int', 'Port', 'port'], ['text', 'Button addresses(separated by space)', 'pulseAddressString'], ['text', 'Toggle addresses(separated by space)', 'toggleAddressString'], ['text', 'Value addresses(separated by space)', 'valueAddressString']],
		'callbackAddresses' : {'pulse' : ['/1/button1', '/1/button2', '/1/button3'], 'toggle' : [], 'value' : ['/1/value1', '/1/value2', '/1/value3']}
	},
	'AudioPulseInput' : {
		'longDescription' : 'Audio responsive pulse input',
		'shortDescription' : 'Audio Pulse',
		'inputs' : [{'type' : 'value', 'description' : 'Sensitivity', 'default' : 1000, 'min' : 1000, 'max' : 10000}],
		'outputs' : [{'type' : 'pulse', 'sendMessageOnChange' : True}]
	},
}

try:
	from OSC import OSCServer,OSCClient, OSCMessage
except:
	inputTypeSettings['OscMultiInput']['unavailable'] = True

	
try:
	import pyaudio
	import sys
	import numpy 
	import struct
except:
	inputTypeSettings['AudioPulseInput']['unavailable'] = True

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
		self.configParams = utils.extendSettings(inputParams[self.__class__.__name__], configParams)
		if 'initInputData' in self.configParams.keys():
			del self.configParams['initInputData']
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
		for input in self.inputs:
			input.stop()
		for output in self.outputs:
			output.stop()


	def isPersistant(self):
		return False




class TimerPulseInput(InputBase):
	def __init__(self, *args):
		InputBase.__init__(self, *args)
		self.timer = Timer(True, self.inputs[0].getValue(), getattr(self, 'sendPulse'))

	def stop(self):
		self.timer.stop()
		InputBase.stop(self)

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
	def setInputValue(self, value, settingIndex = 0):
		if value:
			self.outputs[0].setValue(True)

	def updateOutputValues(self):
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
		callbackAddresses = {}
		callbacksInStringForm = False
		for outputType in outputTypes:
			callbackAddresses[outputType] = []
			key = outputType + 'AddressString'
			if key in params.keys():
				callbackAddresses[outputType] = params[key].split()
				if len(callbackAddresses[outputType]) > 0:
					callbacksInStringForm = True
				del params[key]
		# params = dict(self.defaultParams, **params)
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
		InputBase.stop(self)

	def doPulseCallback(self, path, tags, args, source):
		print 'pulseCallBack' + json.dumps(args)
		outputIndex = self.getOutputIndexFromAddress(path, 'pulse')
		self.outputs[outputIndex].setValue(args[0] in ['1', 1, 'true', 'True'])
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
		defaultParams = {'description' : '', 'type' : 'value', 'subType' : '', 'min' : 0, 'max' : 100, 'default' : 0, 'sendMessageOnChange' : False, 'toggleTimeOut' : 30}
		self.params = utils.extendSettings(defaultParams, params)
		self.parentId = parentId
		self.indexId = indexId
		self.timer = False
		self.constrainValueFunction = getattr(self, utils.makeCamelCase(['constrain', self.params['subType'], self.params['type']]))
		self.value = False
		if self.params['type'] == 'value':
			self.value = self.constrainValueFunction(self.params['default'])
	def getValue(self):
		return self.value
	def setValue(self, newValue):
		if (not self.value == newValue) or self.params['type'] == 'pulse':
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
			if value < float(self.params['min']):
				value = float(self.params['min'])
		if self.params['max']:
			if value > float(self.params['max']):
				value = float(self.params['max'])
		return value
	def constrainIntValue(self, value):
		return int(self.constrainValue(value) + 0.5)
		
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

	def stop(self):
		if self.timer:
			self.timer.stop()

class AudioPulseInput(InputBase):
	class AudioInputThread(Thread):
		def __init__(self, parent, stopEvent, callBackFunction, configParams = {'chunk' : 1024, 'format' : pyaudio.paInt16, 'channels' : 1, 'rate' : 22500, 'recordSeconds' : 5}):
			Thread.__init__(self)
			self.configParams = configParams
			self.callBackFunction = callBackFunction
			self.p=pyaudio.PyAudio()
			self.stopEvent = stopEvent
			self.stream = self.p.open(
				format = configParams['format'],
				channels = configParams['channels'], 
				rate = configParams['rate'], 
				input = True,
				output = True
			)
			csum = []
			spectlen = configParams['rate'] / configParams['chunk'] * configParams['recordSeconds']
			self.makebands(configParams['chunk']/2)
			self.bmax=0
			self.gain = 1.0
			self.skip =8            # skip this many windows

		def setgain(self,intgain):
				self.gain = 2*intgain/100.0

		def makebands(self,max):
				"make a set of power-of-two bands. Max must be power of 2"
				self.bands = []
				self.scale = []
				while max > 2:
						self.bands.append(range(max/2, max))
						self.scale.append(max)
						max = max/2
				self.bands[-1] = range(0,4)
				self.bands.reverse()
				self.scale.reverse()

		def run(self):
			i = 0
			while not self.stopEvent.isSet():
				i += 1
				try:
					data = self.stream.read(self.configParams['chunk'])
				except Exception as e: # HO HUM!
					data = False
					time.sleep(0.01)
				if i>2 and data:
					i = 0
					buff = numpy.array(struct.unpack_from('1024h',data))
					bdata = range(len(self.bands))    
					self.callBackFunction(bands=bdata, value = buff.std())
					time.sleep(0.01)

		def stop(self):
			sys.stdout.flush()
			self.stopEvent.set()
			self.stream.stop_stream()
			self.stream.close()
			self.p.terminate()

	def __init__(self, *args):
		InputBase.__init__(self, *args)
		self.audioThread = AudioPulseInput.AudioInputThread(self, Event(), self.handleAudioUpdate)
		self.audioThread.start()
		
	def stop(self):
		self.audioThread.stop()
		InputBase.stop(self)

	def handleAudioUpdate(self, bands, value):
		if (value > self.inputs[0].getValue()):
			self.outputs[0].setValue(True)
	
	def updateOutputValues(self):
		pass



