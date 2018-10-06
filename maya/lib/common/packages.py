import sys

def clear():
	if globals().has_key('init_modules'):
		# second or subsequent run: remove all but initially loaded modules
		for m in sys.modules.keys():
			if m not in init_modules:
				del(sys.modules[m])
	else:
		# first run: find out which modules were initially loaded
		init_modules = sys.modules.keys()

def importModule(path):
	components = path.split('.')
	if len(components) > 1:
		path = ''
		for c in components:
			path += '{}.'.format(c)
		module = __import__(path[:-1], fromlist = [components[-1]])
	else:
		module = __import__(path)
	return module