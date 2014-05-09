from SculptureController import SculptureController
from ProgramModules.Messenger import Messenger


from flask import Flask, request, jsonify
import json
app = Flask(__name__,  static_folder='jsGui', static_url_path='/jsGui')

appMessenger = Messenger()
setattr(__builtins__, 'appMessenger', appMessenger)

sculpture = SculptureController()


@app.route('/')
def jsGui():
	return app.send_static_file('index.htm')


@app.route('/getData', methods =['GET', 'POST'])
def getData():
	return jsonify(sculpture.getCurrentStateData())

@app.route('/doCommand', methods =['POST'])
def doCommand():
	requestData = json.loads(request.data)
	command = requestData[0]
	result = sculpture.doCommand(requestData)
	return jsonify({'command' : command, 'result' : result})

if __name__ == '__main__':
	host = '127.0.0.1'
	debug = True
	app.run(host=host, debug=debug)