#=================#
# IMPORT PACKAGES #
#=================#

## import utils
import variables

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#    FUNCTION     #
#=================#
def import_module(path, **kwargs):
	'''
	import module from given path

	Args:
		path(str): path should be sth like 'dev.rigging.function'
	Kwargs:
		function(str): function name, if None will use the file name
					   like dev.rigging.task.Task()
	'''
	func = variables.kwargs('function', '', kwargs, shortName='func')

	modules = path.split('.')
	if not func:
		func = modules[-1][0].upper() + modules[-1][1:]
	if len(modules) > 1:
		path = ''
		for m in modules:
			path += '{}.'.format(m)
		module = __import__(path[:-1], fromlist = [modules[-1]])
	else:
		module = __import__(path)
	return module, func