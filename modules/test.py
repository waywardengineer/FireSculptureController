import json
from Messenger import Messenger
appMessenger = Messenger()
config = json.load(open("../sculptureDefinitions/tympani.json"))
foo = 5
setattr(__builtins__, 'appMessenger', appMessenger)



from DataChannelManager import DataChannelManager
dcm = DataChannelManager(config)
dcm.send('poofers', [[[0, 15], [True]]])

for message in appMessenger.getMessages('log'):
	print message