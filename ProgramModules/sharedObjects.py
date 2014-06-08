from SafeModeController import SafeModeController
from Messenger import Messenger

inputManager = object()
dataChannelManager = object()
messenger = Messenger()
safeMode = SafeModeController()

def isSafeModeOff():
	return not safeMode.isSet()