#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#    FUNCTION     #
#=================#

def kwargs(longName, defaultValue, kwargs, shortName=None):
	'''
	get variable value from given dictionary, support short cut key

	Args:
		longName(str): key name
		defaultValue: default value
		kwargs(dict): given dictionary
	Kwargs:
		shortName(str)[None]: short key name
	Returns:
		value
	'''
	if longName in kwargs:
		val = kwargs[longName]
	elif shortName and shortName in kwargs:
		val = kwargs[shortName]
	else:
		val = defaultValue
	
	return val