from SculptureController import SculptureController

from ProgramModules.Messenger import Messenger

from time import sleep
appMessenger = Messenger()
setattr(__builtins__, 'appMessenger', appMessenger)

sc = SculptureController()
sc.loadSculpture('tympani')
id = sc.doCommand(['addPattern', 'poofers', 'Chase'])
sleep(5)
sc.doCommand(['removePattern', 'poofers', id])

