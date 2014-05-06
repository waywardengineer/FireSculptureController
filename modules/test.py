import json
config = json.load(open("../sculptureDefinitions/tympani.json"))




from DataChannelManager import DataChannelManager
dcm = DataChannelManager(config)
dcm.send('poofers', [[[0, 15], [True]]])