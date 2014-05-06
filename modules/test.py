import json
from Messenger import Messenger
from Inputs import *
from time import sleep
appMessenger = Messenger()
config = json.load(open("../sculptureDefinitions/tympani.json"))
foo = 5
setattr(__builtins__, 'appMessenger', appMessenger)
from PatternManager import PatternManager


from DataChannelManager import DataChannelManager
dcm = DataChannelManager(config)
dcm.send('poofers', [[[0, 15], [True]]])
pm = PatternManager(dcm, False, config['modules'][0])
for message in appMessenger.getMessages('log'):
	print message
	
timerInput = TimerInput(1)
while 1:
	sleep(0.1)
	messages = appMessenger.getMessages('patternTimers')
	for message in messages:
		print message
