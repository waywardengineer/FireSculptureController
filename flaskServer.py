from SculptureController import SculptureController
from ProgramModules.Messenger import Messenger


from flask import Flask, request, jsonify, Response
import json
app = Flask(__name__,  static_folder='jsGui', static_url_path='/jsGui')

import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue


class ServerSentEvent(object):

	def __init__(self, data):
		self.data = data
		self.event = None
		self.id = None
		self.desc_map = {
			self.data : "data",
			self.event : "event",
			self.id : "id"
		}

	def encode(self):
		if not self.data:
			return ""
		lines = ["%s: %s" % (v, k) 
					 for k, v in self.desc_map.iteritems() if k]
		
		return "%s\n\n" % "\n".join(lines)

appMessenger = Messenger()
setattr(__builtins__, 'appMessenger', appMessenger)
sculpture = SculptureController()
dataQueue = ''
subscriptions = []

def sendNewOutputState(argData):
	whatChanged = argData['whatChanged']
	data = {}
	if whatChanged == 'outputChanged':
		data = sculpture.getCurrentOutputState()
	elif whatChanged == 'log':
		data = {'log' : appMessenger.getMessages('log')}
	for sub in subscriptions[:]:
		sub.put(json.dumps(data))


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
	if command == 'loadSculpture':
		appMessenger.addBinding('outputChanged', globals()['sendNewOutputState'], {'whatChanged' : 'outputChanged'})
		appMessenger.addBinding('log', globals()['sendNewOutputState'], {'whatChanged' : 'log'})

	return jsonify({'command' : command, 'result' : result})


@app.route("/dataStream")
def subscribe():
	def gen():
		q = Queue()
		subscriptions.append(q)
		try:
			while True:
				result = q.get()
				ev = ServerSentEvent(str(result))
				yield ev.encode()
		except GeneratorExit: # Or maybe use flask signals
			subscriptions.remove(q)
	return Response(gen(), mimetype="text/event-stream")





if __name__ == '__main__':
	app.debug = True
	server = WSGIServer(("", 5000), app)
	server.serve_forever()
