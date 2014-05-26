from Patterns.PatternBase import PatternBase
from ProgramModules.Timers import Timer
class Chase(PatternBase):
	def __init__(self, *args):
		self.inputParams = {
			'triggerStep' : {
				'descriptionInPattern' : 'Trigger next step in sequence',
				'type' : 'pulse',
				'subType' : 'timer',
				'inputs' : [{
					'min' : 50,
					'max' : 3000, 
					'default' : 100
				}]
			},
			'triggerSequence' : {
				'descriptionInPattern' : 'Trigger chase',
				'type' : 'pulse',
				'subType' : 'onOff'
			},
			'numberOn' : {
				'descriptionInPattern' : 'Number of poofers on at once',
				'type' : 'value',
				'subType' : 'int',
				'inputs' : [{
					'min' : 1,
					'max' : 5,
					'default' : 2
				}]
			},
			'stepping' : {
				'descriptionInPattern' : 'Number of poofers to jump per step',
				'type' : 'value',
				'subType' : 'int',
				'inputs' : [{
					'min' : 1,
					'max' : 5,
					'default' : 1
				}]
			},
			'numberPulses' : {
				'descriptionInPattern' : 'Number of pulses chasing each other',
				'type' : 'value',
				'subType' : 'int',
				'inputs' : [{
					'min' : 1,
					'max' : 3,
					'default' : 1
				}]
			}
		}
		PatternBase.__init__(self, *args)
		self.patternName = 'Poofer Chase'

		self.position = 0
		self.sequenceTriggered = True

	def triggerStep(self):
		if self.inputs.triggerStep and self.sequenceTriggered:
			self.updateTriggerFunction()
			self.position += self.inputs.stepping
			if self.position > self.gridSize[1]:
				if self.inputs.numberPulses > 1:
					self.position -= self.gridSize[1]
				else:
					self.position = 0
				self.sequenceTriggered = self.inputs.triggerSequence
				if not self.sequenceTriggered:
					self.updateTriggerFunction()

		
	def triggerSequence(self):
		if self.inputs.triggerSequence:
			self.inputs.doCommand(['triggerStep', 'refresh'])
			self.position = 0
			self.sequenceTriggered = True
			
	def getState(self, row, col):
		result = False
		if self.sequenceTriggered:
			spacing = self.gridSize[1] / self.inputs.numberPulses
			intervalCount = 0
			while intervalCount < self.inputs.numberPulses and not result:
				lowerLimit = self.position + intervalCount * spacing
				upperLimit = lowerLimit + self.inputs.numberOn
				if col >= lowerLimit and col < upperLimit:
					result = True
				if self.inputs.numberPulses > 1:
					lowerLimit = self.position - intervalCount * spacing
					upperLimit = lowerLimit + self.inputs.numberOn
					if col >= lowerLimit and col < upperLimit:
						result = True
				intervalCount += 1
		return result
		
class AllPoof(PatternBase):
	def __init__(self, *args):
		self.inputParams = {
			'poofButton' : {
				'descriptionInPattern' : 'Poof!',
				'type' : 'pulse',
				'subType' : 'button'
			},
			'stayOnTime' : {
				'descriptionInPattern' : 'Time to stay on for',
				'type' : 'value',
				'subType' : 'int',
				'inputs' : [{
					'min' : 100,
					'max' : 1000,
					'default' : 200,
					'description' : 'Milliseconds'
				}]
			},
		}
		PatternBase.__init__(self, *args)
		self.patternName = 'Allpoof'
		self.timer = Timer(False, self.inputs.stayOnTime, self.turnOff)
		self.poofState = False
	def poofButton(self):
		if self.inputs.poofButton:
			self.timer.changeInterval(self.inputs.stayOnTime)
			self.timer.refresh()
			self.poofState = True
			self.updateTriggerFunction()
	
	def turnOff(self):
		self.poofState = False
		self.updateTriggerFunction()

	def getState(self, row, col):
		return self.poofState
		
	def stop(self):
		self.timer.stop()
		PatternBase.stop(self)
