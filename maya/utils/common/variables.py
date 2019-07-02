#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger
from config.PROPERTY_ITEMS import PROPERTY_ITEMS 
#=================#
#    FUNCTION     #
#=================#

def kwargs(longName, defaultValue, kwargs, shortName=''):
	'''
	get variable value from given dictionary, support short cut key

	Args:
		longName(str): key name
		defaultValue: default value
		kwargs(dict): given dictionary
	Kwargs:
		shortName(str)['']: short key name
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

def register_single_kwarg(longName, defaultValue=None, shortName='', attributeName='', uiKwargs={}):
	'''
	this function is for class need register kwarg for in-class use and show on the ui

	Args:
		longName(str): kwarg key name
	Kwargs:	
		shortName(str)['']: kwarg short name
		defaultValue[None]: default value
		attributeName(str)['']: attribute name in class, will use longName if not any
		uiKwargs(dict)[{}]: kwargs for ui base on PROPERTY_ITEMS.py
	Returns:
		kwargInfo(dict)
		kwargInfo_ui(dict)
	'''
	kwargInfo_ui = {longName: {}}

	if uiKwargs:
		if 'type' in uiKwargs:
			attrType = uiKwargs['type']
		elif 'value' in uiKwargs and uiKwargs['value'] != None:
			attrType = _get_type_from_value(uiKwargs['value'])
	elif defaultValue != None:
		attrType = _get_type_from_value(defaultValue)

	if attrType:
		kwargInfo_ui[longName].update(PROPERTY_ITEMS[attrType])
	else:
		Logger.error('kwarg should at least has defaultValue or value/type in uiKwargs')

	if uiKwargs:
		kwargInfo_ui[longName].update(uiKwargs)
	
	if defaultValue != None:
		# update kwargs ui value info
		kwargInfo_ui[longName].update({'value': defaultValue})

	if not attributeName:
		attributeName = longName
	kwargInfo = {attributeName: [longName, kwargInfo_ui[longName]['value'], shortName]}

	return kwargInfo, kwargInfo_ui

def _get_type_from_value(value):
	if value in [True, False]:
		valType = 'bool'
	elif isinstance(value, float):
		valType = 'float'
	elif isinstance(self._value, int):
		valType = 'int'
	elif isinstance(self._value, list):
		valType = 'list'
	elif isinstance(self._value, dict):
		valType = 'dict'
	elif isinstance(self._value, basestring):
		valType = 'str'
	else:
		Logger.error('Can not recogonize value type')
	return valType