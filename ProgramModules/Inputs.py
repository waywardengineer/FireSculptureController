''' An input is anything that creates a value for patterns to use. These can be numerical parameters(which will be set by the GUI), physical devices,
keyboard bindings, timers, audio pulse thingeys, etc. There will be several broad types such as pulse and value, and any input of the same type 
will be interchangeable
''' 
from ProgramModules.Timers import Timer
from ProgramModules import utils

from threading import Thread, Event
import json
import time
import random
availableInputTypes = {'pulse' : ['timer', 'onOff', 'button', 'audio', 'random'], 'value' : ['', 'int'], 'multi' : ['osc', 'basic', 'randomPulse'], 'text' : ['', 'choice']}
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
		'inputs' : [{'type' : 'toggle', 'sendMessageOnChange' : True, 'default' : 'True'}],
		'direct' : True
	},
	'ButtonPulseInput' : {
		'longDescription' : 'On/off instantaneous button control',
		'shortDescription' : 'Button',
		'inputs' : [{'type' : 'pulse', 'sendMessageOnChange' : True, 'toggleTimeOut' : 20, 'default' : False}],
		'direct' : True
	},
	'ValueInput' : {
		'longDescription' : 'Variable value input, can be decimal',
		'shortDescription' : 'Value setting',
		'inputs' : [{'type' : 'value', 'description' : '', 'default' : 0, 'min' : 0, 'max' : 100}],
		'direct' : True

	},
	'IntValueInput' : {
		'longDescription' : 'Variable value input, integer',
		'shortDescription' : 'Value setting',
		'inputs' : [{'type' : 'value', 'subType' : 'int', 'description' : '', 'default' : 0, 'min' : 0, 'max' : 100}],
		'direct' : True
	},
	'TextInput' : {
		'longDescription' : 'Text input',
		'shortDescription' : 'Text',
		'inputs' : [{'type' : 'text', 'subType' : '', 'description' : '', 'default' : ''}],
		'direct' : True
	},
	'ChoiceTextInput' : {
		'longDescription' : 'Choice input',
		'shortDescription' : 'Choice',
		'inputs' : [{'type' : 'text', 'subType' : 'choice', 'description' : '', 'choices' : {}}],
		'direct' : True
	},
	'OscMultiInput' : {
		'longDescription' : 'OpenSoundControl server', 
		'shortDescription' : 'OSC server', 
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
	'BasicMultiInput' : {
		'longDescription' : 'Multiple basic inputs',
		'shortDescription' : 'Multi Basic',
		'number' : 5,
		'basicInputType' : 'IntValueInput',
		'description' : '',
		'min' : 0,
		'max' : 100,
		'default' : 0,
		'initInputData' : [['textList', 'Descriptions', 'description'], ['textList', 'Mins', 'min'], ['textList', 'Maxes', 'max'], ['textList', 'Defaults', 'default']],
		'direct' : True
	},
	'RandomPulseInput' : {
		'longDescription' : 'Random pulse input',
		'shortDescription' : 'Random Pulse',
		'inputs' : [
			{'type' : 'value', 'description' : 'Rarity', 'default' : 10, 'min' : 2, 'max' : 100},
			{'type' : 'value', 'description' : 'Min time', 'default' : 200, 'min' : 50, 'max' : 1000},
			{'type' : 'value', 'description' : 'Max time', 'default' : 800, 'min' : 50, 'max' : 1000},
		],
		'outputs' : [{'type' : 'toggle', 'sendMessageOnChange' : True}]
	},
	'RandomPulseMultiInput' : {
		'longDescription' : 'Multi random pulse input',
		'shortDescription' : 'MultiRand Pulse',
		'number' : 5
	}
}

try:
	from OSC import OSCServer,OSCClient, OSCMessage
except:
	inputParams['OscMultiInput']['unavailable'] = True

	
try:
	import pyaudio
	import sys
	import numpy 
	import struct
except:
	inputParams['AudioPulseInput']['unavailable'] = True


class InputBase():
	def __init__(self, configParams, instanceId):
		self.configParams = utils.multiExtendSettings({'inputs' : [], 'outputs' : [], 'direct' : False}, inputParams[self.__class__.__name__], configParams)
		inputParamKeys = [key for key in ['min', 'max', 'default', 'description', 'sendMessageOnChange', 'choices'] if key in self.configParams]
		if inputParamKeys and self.__class__.__name__ not in ['BasicMultiInput']:
			if len(self.configParams['inputs']) == 0:
				self.configParams['inputs'].append({})
			for key in inputParamKeys:
				self.configParams['inputs'][0][key] = self.configParams[key]
				del self.configParams[key]
		if 'initInputData' in self.configParams.keys():
			del self.configParams['initInputData']
		self.outputs = []
		self.inputs = []
		self.instanceId = instanceId
		if self.configParams['direct']:
			for paramIndex in range(len(self.configParams['inputs'])):
				self.outputs.append(InputOutputParam(self.configParams['inputs'][paramIndex], self.instanceId, paramIndex))
				self.inputs.append(self.outputs[paramIndex])
		else:
			for inputParam in self.configParams['inputs']:
				self.inputs.append(InputOutputParam(inputParam))
			for paramIndex in range(len(self.configParams['outputs'])):
				self.outputs.append(InputOutputParam(self.configParams['outputs'][paramIndex], self.instanceId, paramIndex))


	def setInputValue(self, value, settingIndex = 0):
		self.inputs[settingIndex].setValue(value)
		self.updateOutputValues()


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
		if not self.configParams['direct']:
			for input in self.inputs:
				input.stop()
		for output in self.outputs:
			output.stop()



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
	pass

class ValueInput(InputBase):
	pass

class IntValueInput(InputBase):
	pass

class TextInput(InputBase):
	pass

class ChoiceTextInput(InputBase):
	pass


class BasicMultiInput(InputBase):
	def __init__(self, configParams, *args):
		configParams = utils.multiExtendSettings({'inputs' : []}, inputParams[self.__class__.__name__], configParams)
		inputParamKeys = [key for key in ['min', 'max', 'default', 'description', 'choices'] if key in configParams]
		for i in range(configParams['number']):
			configParam = {}
			for key in inputParamKeys:
				if isinstance(configParams[key], list):
					configParam[key] = configParams[key][i % len(configParams[key])]
				else:
					configParam[key] = configParams[key]
			configParam['relevance'] = [i]
			configParams['inputs'].append(utils.extendSettings(inputParams[configParams['basicInputType']]['inputs'][0], configParam))
		for key in inputParamKeys:
			del configParams[key]
		
		InputBase.__init__(self, configParams, *args)


class OscMultiInput(InputBase):
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
		self.outputTypes = ['pulse', 'toggle', 'value']
		callbackAddresses = {}
		callbacksInStringForm = False
		for outputType in self.outputTypes:
			callbackAddresses[outputType] = []
			key = outputType + 'AddressString'
			if key in params.keys():
				callbackAddresses[outputType] = params[key].split()
				if len(callbackAddresses[outputType]) > 0:
					callbacksInStringForm = True
				del params[key]
		if callbacksInStringForm:
			params['callbackAddresses'] = callbackAddresses
		params['outputs'] = []
		for outputType in self.outputTypes:
			for address in params['callbackAddresses'][outputType]:
				params['outputs'].append({'type' : outputType, 'description' : outputType[0].upper() + outputType[1:] + ' ' + address, 'sendMessageOnChange' : True})
			
		InputBase.__init__(self, params, *args)
		self.callbackLinkList = []
		self.stopEvent = Event()
		self.server = OscMultiInput.OscServerThread((self.configParams['host'], self.configParams['port']), self.stopEvent)
		self.buildCallbackLinkList()
		self.server.setCallBacks(self.callbackLinkList)
		self.server.start()
		self.persistant = True


	def buildCallbackLinkList(self):
		for callbackType in self.outputTypes:
			if callbackType in self.configParams['callbackAddresses'].keys():
				function = getattr(self, 'do' + callbackType[0].upper() + callbackType[1:] + 'Callback')
				for callbackAddress in self.configParams['callbackAddresses'][callbackType]:
					self.callbackLinkList.append([callbackAddress, function])


	def stop(self):
		self.stopEvent.set()
		InputBase.stop(self)

	def doPulseCallback(self, path, tags, args, source):
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
		defaultParams = {'description' : '', 'type' : 'value', 'subType' : '', 'default' : 0, 'sendMessageOnChange' : False, 'toggleTimeOut' : 30, 'min' : False, 'max' : False}
		self.params = utils.extendSettings(defaultParams, params)
		self.parentId = parentId
		self.indexId = indexId
		self.timer = False
		self.constrainValueFunction = getattr(self, utils.makeCamelCase(['constrain', self.params['subType'], self.params['type']]))
		self.value = self.constrainValueFunction(self.params['default'])
		if self.params['sendMessageOnChange']:
			appMessenger.setQueuing("output%s_%s" %(self.parentId, self.indexId), False)
		
	def getValue(self):
		return self.value
	def setValue(self, newValue):
		newValue = self.constrainValueFunction(newValue)
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
	
	def constrainText(self, value):
		return value
		
	def constrainChoiceText(self, value):
		if value in self.params['choices'].keys():
			return value
		return False
		
	
	def getCurrentStateData(self):
		data = self.params.copy()
		data['currentValue'] = self.value
		return data

	def stop(self):
		if self.timer:
			self.timer.stop()

class AudioPulseInput(InputBase):
	class AudioInputThread(Thread):
		def __init__(self, parent, stopEvent, callBackFunction, configParams = {'chunk' : 1024, 'channels' : 1, 'rate' : 22500, 'recordSeconds' : 5}):
			Thread.__init__(self)
			configParams['format'] = pyaudio.paInt16
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

class RandomPulseInput(InputBase):
	def __init__(self, *args):
		InputBase.__init__(self, *args)
		self.checkTimer = Timer(True, 200, self.doCheck)
		self.numPulses = 1
		self.onStates = [False]
		self.offTimers = [Timer(False, self.inputs[1].getValue(), self.turnOff, (0,))]

	def stop(self):
		self.checkTimer.stop()
		for i in range(self.numPulses):
			self.offTimers[i].stop()
		InputBase.stop(self)
		
	def doCheck(self):
		for i in range(self.numPulses):
			if random.randint(0, self.inputs[0].getValue()) < 2:
				self.outputs[i].setValue(True)
				self.offTimers[i].changeInterval(random.randint(min(self.inputs[1].getValue(), self.inputs[2].getValue()), max(self.inputs[1].getValue(), self.inputs[2].getValue())))
				self.offTimers[i].refresh()
				
	def turnOff(self, index):
		self.outputs[index].setValue(False)
		
class RandomPulseMultiInput(RandomPulseInput):
	def __init__(self, params, *args):
		params = utils.multiExtendSettings(inputParams['RandomPulseInput'], inputParams['RandomPulseMultiInput'], params)
		self.numPulses = params['number']
		for inputIndex in range(len(params['inputs'])):
			params['inputs'][inputIndex]['relevance'] = [i for i in range(self.numPulses)]
		params['outputs'] = [{'type' : 'toggle', 'sendMessageOnChange' : True, 'description' : 'channel%s' %(i)} for i in range(self.numPulses)]
		InputBase.__init__(self, params, *args)
		self.checkTimer = Timer(True, 200, self.doCheck)
		self.onStates = [False for i in range(self.numPulses)]
		self.offTimers = [Timer(False, self.inputs[1].getValue(), self.turnOff, (i,)) for i in range(self.numPulses)]
	
	
