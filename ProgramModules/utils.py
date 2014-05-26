from copy import deepcopy

def makeCamelCase(parts, doFirstLetter = False):
	str = ''
	for i in range(len(parts)):
		part = parts[i]
		if len(part) > 0:
			if i > 0 or doFirstLetter:
				str += part[0].upper()
			else:
				str += part[0].lower()
		if len(part) > 1:
			str += part[1:]
	return str
	
def extendSettings(defaults, settings):
	typesMatch = False
	for type in [list, dict]:
		if isinstance(defaults, type) and isinstance(settings, type):
			typesMatch = True
	if not typesMatch:
		return deepcopy(settings)
	out = False
	if isinstance(defaults, list):
		if len(defaults) == len(settings):
			out = []
			for i in range(len(defaults)):
				out.append(extendSettings(defaults[i], settings[i]))
		else:
			out = deepcopy(settings)
	elif isinstance(defaults, dict):
		out = {}
		for key in defaults:
			if key in settings.keys():
				out[key] = extendSettings(defaults[key], settings[key])
			else:
				out[key] = deepcopy(defaults[key])
		for key in settings:
			if not (key in defaults.keys()):
				out[key] = deepcopy(settings[key])
	return out
