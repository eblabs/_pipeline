import sys

def importPackage(path, reloadPackage=False):
	pathSplit = path.split('.')
	if reloadPackage:
		for key in sys.modules.keys():
			if pathSplit[-1] in key:
				del(sys.modules[key])
	if len(pathSplit) > 1:
		pathImport = ''
		for c in pathSplit:
			pathImport += '{}.'.format(c)
		module = __import__(pathImport[:-1], fromlist = [pathSplit[-1]])
	else:
		module = __import__(path)
	return module