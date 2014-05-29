from SculptureController import SculptureController

from flask import Flask, request, jsonify, Response
import json
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

app = Flask(__name__,  static_folder='jsGui', static_url_path='/jsGui')
sculpture = SculptureController()
subscriptions = []



def sendNewOutputState(whatChanged):
	data = {whatChanged : appMessenger.getMessages(whatChanged)}
	for sub in subscriptions[:]:
		sub.put(json.dumps(data), False)


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
		appMessenger.addBinding('outputChanged', sendNewOutputState, 'outputChanged')
		# appMessenger.addBinding('log', sendNewOutputState, 'log')

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
		except GeneratorExit:
			subscriptions.remove(q)
	return Response(gen(), mimetype="text/event-stream")



sculpture.loadSculpture('tympani')
sculpture.doCommand(['addPattern', 'poofers', 'RandomPoof'])
sculpture.doCommand(['addPattern', 'poofers', 'Chase'])
appMessenger.addBinding('outputChanged', sendNewOutputState, 'outputChanged')
sculpture.doCommand(['addGlobalInput', {'type' : 'pulse', 'subType' : 'audio'}])
sculpture.doCommand(['addGlobalInput', {'type' : 'multi', 'subType' : 'randomPulse'}])
sculpture.doCommand(['addGlobalInput', {'type' : 'multi', 'subType' : 'basic', 'number' : 5, 'min' : [0, 0, 1, 0,  1], 'max' : [1, 2, 3, 4,  5], 'description' : ['foo', 'bar', 'baz', 'bam', 'boo']}])
# sculpture.doCommand(["changePatternInputBinding","poofers","poofersPattern0","poofButton",2,0])

if __name__ == '__main__':
	app.debug = True
	server = WSGIServer(("", 80), app)
	try:
		server.serve_forever()
	except:
		sculpture.doReset()
