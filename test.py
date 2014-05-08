from SculptureController import SculptureController

from ProgramModules.Messenger import Messenger

appMessenger = Messenger()
setattr(__builtins__, 'appMessenger', appMessenger)

sc = SculptureController()
sc.loadSculpture('tympani')
sc.doCommand(['addPattern', 'poofers', 'Chase'])

