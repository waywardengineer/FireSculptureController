from SculptureController import SculptureController
from ProgramModules.Messenger import Messenger


from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
app = Flask(__name__)

appMessenger = Messenger()
setattr(__builtins__, 'appMessenger', appMessenger)

sculpture = SculptureController()
sculpture.loadSculpture('tympani')

@app.route('/getData', methods =['GET', 'POST'])
def getData():
	return jsonify(sculpture.getCurrentStateData())

@app.route('/doCommand', methods =['POST'])
def doCommand():
	result = sculpture.doCommand(json.loads(request.data))
	return jsonify({'result' : result})

if __name__ == '__main__':
	host = '127.0.0.1'
	debug = True
	app.run(host=host, debug=debug)