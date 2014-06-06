from InputBase import InputBase
from ProgramModules import utils

from Basic import *
from Osc import *
from Audio import *

import Osc, Basic, Audio
inputTypes = utils.multiExtendSettings(Basic.inputTypes, Osc.inputTypes, Audio.inputTypes)
availableInputTypes = {}
for key in inputTypes.keys():
	subType = False
	parts = key.split(' ')
	type = parts[-1]
	if len(parts) > 1:
		subType = parts[0]
	if not type in availableInputTypes.keys():
		availableInputTypes[type] = []
	if subType:
		availableInputTypes[type].append(subType)

