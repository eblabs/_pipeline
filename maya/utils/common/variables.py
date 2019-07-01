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
		kwargInfo_ui[longName].update(uiKwargs)
	
	if defaultValue != None:
		# update kwargs ui value info
		kwargInfo_ui[longName].update({'value': defaultValue})
	elif uiKwargs:
		if 'value' in uiKwargs and uiKwargs['value'] != None:
			# get default value if set 'value' in uiKwargs
			defaultValue = uiKwargs['value']
		elif 'type' in uiKwargs:
			# get default value from specific type item from PROPERTY_ITEMS
			itemType = uiKwargs['type']
			defaultValue = PROPERTY_ITEMS[itemType]

	if not attributeName:
		attributeName = longName
	kwargInfo = {attributeName: [longName, defaultValue, shortName]}

	return kwargInfo, kwargInfo_ui
