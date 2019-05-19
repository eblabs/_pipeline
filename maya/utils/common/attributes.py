#=================#
# IMPORT PACKAGES #
#=================#

## import maya packages
import maya.cmds as cmds

## import utils
import variables
#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

ATTR_CONFIG = {'all': ['translateX', 'translateY', 'translateZ',
					   'rotateX', 'rotateY', 'rotateZ',
					   'scaleX', 'scaleY', 'scaleZ', 'visibility'],
			   'translate': ['translateX', 'translateY', 'translateZ'],
			   'rotate': ['rotateX', 'rotateY', 'rotateZ'],
			   'scale': ['scaleX', 'scaleY', 'scaleZ'],
			   'vis': ['visibility'],
			   'scaleVis': ['scaleX', 'scaleY', 'scaleZ', 'visibility']}

#=================#
#      CLASS      #
#=================#
class Attr(object):
	"""Attr class to acess common attribute vars"""
	def __init__(self):
		pass

for key, item in ATTR_CONFIG.iteritems():
	setattr(Attr, key, item)
					
#=================#
#    FUNCTION     #
#=================#
def connect_attrs(driverAttrs, drivenAttrs, **kwargs):
	'''
	Connect driver attrs to driven attrs

	Args:
		driverAttrs(str/list): source attrs
		drivenAttrs(str/list): target attrs
	Kwargs:
		driver(str): override the node in driverAttrs
		driven(str): override the drivenAttrs
		force(bool)[True]: override the connection/lock status
	'''
	# get vars
	driver = variables.kwargs('driver', None, kwargs)
	driven = variables.kwargs('driven', None, kwargs)
	force = variables.kwargs('force', True, kwargs, shortName='f')

	# check if driverAttrs/drivenAttrs is string/list
	if isinstance(driverAttrs, basestring):
		driverAttrs = [driverAttrs]
	if isinstance(drivenAttrs, basestring):
		drivenAttrs = [drivenAttrs]

	# connect each attr
	for attrs in zip(driverAttrs, drivenAttrs):
		_connect_single_attr(attrs[0], attrs[1], 
							 driver=driver, driven=driven,
							 force=force)
	if len(driverAttrs) == 1:
		if not __check_attr_exists(driverAttrs[0]):
			return
		for attr in drivenAttrs[1:]:
			_connect_single_attr(drivenAttrs[0], attr, 
								 driver=driver, driven=driven,
								 force=force)

def lock_hide_attrs(node, attrs):
	'''
	lock and hide attrs

	Args:
		node(str/list): the node to lock hide attrs
		attrs(str/list): lock and hide given attrs
	'''
	if isinstance(node, basestring):
		node = [node]
	if isinstance(attrs, basestring):
		attrs = [attrs]
	for n in node:
		for attr in attrs:
			if cmds.attributeQuery(attr, node=n, ex=True):
				cmds.setAttr('{}.{}'.format(n, attr), keyable=False,
							 lock=True, channelBox=False)
			else:
				Logger.warn('{} does not have attribute: {}'.format(n, attr))

def unlock_attrs(node, attrs, **kwargs):
	'''
	unlock attrs

	Args:
		node(str/list): the node to unlock attrs
		attrs(str/list): unlock and show given attrs
	Kwargs:
		keyable(bool)[True]: set attr keyable
		channelBox(bool)[True]: show attr in channelBox (none keyable if False)
	'''
	# get vars
	keyable = variables.kwargs('keyable', True, kwargs, shortName='k')
	channelBox = variables.kwargs('channelBox', True, kwargs, shortName='cb')
	if isinstance(node, basestring):
		node = [node]
	if isinstance(attrs, basestring):
		attrs = [attrs]
	for n in node:
		for attr in attrs:
			if cmds.attributeQuery(attr, node=n, ex=True):
				cmds.setAttr('{}.{}'.format(n, attr), lock=False)
				cmds.setAttr('{}.{}'.format(n, attr), channelBox=channelBox)
				if channelBox == False:
					keyable = False
				cmds.setAttr('{}.{}'.format(n, attr), keyable=keyable)
			else:
				Logger.warn('{} does not have attribute: {}'.format(n, attr))

def add_attrs(node, attrs, **kwargs):
	'''
	add attrs

	Args:
		node(str/list): nodes to assign attrs
		attrs(str/list): add attrs
	Kwargs:
		attributeType(str)['float']: 'bool', 'long', 'enum', 'float', 'double', 
						    		 'string', 'matrix', 'message'
		range(list)[[]]:min/max value
		defaultValue(float/int/list)[None]: default value
		keyable(bool)[True]: set attr keyable
		channelBox(bool)[True]: show attr in channel box
		enumName(str)['']: enum attr name
		multi(m)[False]: add attr as a multi-attribute
		lock(bool)[False]: lock attr  
	'''
	# get vars
	attrType = variables.kwargs('attributeType', 'float', kwargs, shortName='at')
	attrRange = variables.kwargs('range', [], kwargs)
	defaultVal = variables.kwargs('defaultValue', None, kwargs, shortName='dv')
	keyable = variables.kwargs('keyable', True, kwargs, shortName='k')
	channelBox = variables.kwargs('channelBox', True, kwargs, shortName='cb')
	enumName = variables.kwargs('enumName', '', kwargs, shortName='enum')
	multi = variables.kwargs('multi', False, kwargs, shortName='m')
	lock = variables.kwargs('lock', False, kwargs)
	
	if isinstance(node, basestring):
		node = [node]
	if isinstance(attrs, basestring):
		attrs = [attrs]
	if not isinstance(defaultVal, list):
		defaultVal = [defaultVal]*len(attrs)
	elif not isinstance(defaultVal[0], list) and attributeType == 'matrix':
		defaultVal = [defaultVal]*len(attrs)

	if not channelBox or lock:
		keyable=False
	if attrType != 'string':
		attrTypeKey = 'attributeType'
	else:
		attrTypeKey = 'dataType'

	attrDict = {attrTypeKey: attrType,
				'keyable': keyable,
				'multi': multi}

	for n in node:
		for attr, val in zip(attrs, defaultVal):
			# check if attr exists
			if not cmds.attributeQuery(attr, node=n, ex=True):
				attrDict.update({'longName': attr})
				if val:
					attrDict.update({'defaultValue': val})
				if attrRange:
					if attrRange[0]:
						attrDict.update({'minValue': attrRange[0]})
					if attrRange[1]:
						attrDict.update({'maxValue': attrRange[1]})
				if enumName:
					attrDict.update(enumName)
				# add attr
				cmds.addAttr(n, **attrDict)
				# skip message
				if attrType != 'message':
					# set default value for string/matrix
					if attrType in ['string', 'matrix'] and val:
						cmds.setAttr('{}.{}'.format(n, attr), val, type=attrType)
					# lock
					cmds.setAttr('{}.{}'.format(n, attr), lock=lock)
					# channelBox
					if attrType not in ['string', 'matrix'] and channelBox:
						cmds.setAttr('{}.{}'.format(n, attr), channelBox=channelBox)
			else:
				Logger.warn('{} already havs attribute: {}'.format(n, attr))

def set_attrs(attrs, value, node=None, type=None, force=True):
	'''
	set attrs

	Args:
		attrs(str/list): attrs need to be set
		value: attrs values
	Kwargs:
		node(str): node name to override the attrs
		type(str): if need to be specific
		force(bool)[True]: force set value if locked
	'''
	if isinstance(attrs, basestring):
		attrs = [attrs]
	attrsNum = len(attrs)
	if not isinstance(value, list):
		value = [value]*attrsNum
	elif type='matrix' and not isinstance(value[0], list):
		value = [value]*attrsNum
	for attr, val in zip(attrs, value):
		attrCompose = __check_attr_exists(attr, node=node)
		if attrCompose:
			# check if connected
			connections = cmds.listConnections(attrCompose, source = True, 
									   destination = False, plugs = True, 
									   skipConversionNodes = True)
			if not connections:
				setAttrDict={}
				if type in ['matrix', 'string']:
					setAttrDict.update({'type': type})
				# check if locked
				lock = cmds.getAttr(attrCompose, lock=True)
				if not lock or force:
					cmds.setAttr(attrCompose, lock=False)
					cmds.setAttr(attrCompose, val, **setAttrDict)
					if lock:
						cmds.setAttr(attrCompose, lock=True)
				else:
					Logger.warn('{} is locked, skipped'.format(attrCompose))
			else:
				Logger.warn('{} has input connection: {}, skipped'.format(attrCompose, connections[0]))
		else:
			Logger.warn('{} does not exist, skipped'.format(attrCompose))

def attr_in_channelBox(node, attr):
	'''
	check if given attr is in channelBox

	Args:
		node(str)
		attr(str)
	Returns:
		check(bool)
	'''
	attr = '{}.{}'.format(node, attr)
	keyable = cmds.getAttr(attr, keyable=True)
	channelBox = cmds.getAttr(attr, cb=True)
	check = keyable or channelBox
	return check

#=================#
#  SUB FUNCTION   #
#=================#
def __check_attr_exists(attr, node=None):
	'''
	Check if attr exists
	'''
	attrSplit = attr.split('.')
	if not node:
		node = attrSplit[0]
	if len(attrSplit)>1:
		attr = attr.replace(attrSplit[0]+'.', '')

	try:
		cmds.getAttr('{}.{}'.format(node, attr))
		return '{}.{}'.format(node, attr)
	except:
		Logger.warn('{} does not have attr {}'.format(node, attr))
		return None

def _connect_single_attr(driverAttr, drivenAttr, driver=None, driven=None, force=True):
	'''
	Connect single attr
	'''
	attrConnect=[]
	for attr, node in zip([driverAttr, drivenAttr],
						  [driver, driven]):
		attrCheck = __check_attr_exists(attr, node=node)
		if not attrCheck:
			break
		else:
			attrConnect.append(attrCheck)
	if not attrCheck:
		return

	# check if driven attr has connection
	inputPlug = cmds.listConnections(attrConnect[1], source=True,
									 destination=False, plugs=True,
									 skipConversionNodes=True)
	# check if driven attr is locked
	lock = cmds.getAttr(attrConnect[1], lock=True)

	# connect attr
	if not inputPlug and not lock:
		cmds.connectAttr(attrConnect[0], attrConnect[1])
	else:
		if force:
			cmds.setAttr(attrConnect[1], lock=False)
			cmds.connectAttr(attrConnect[0], attrConnect[1], force=True)
			if lock:
				cmds.setAttr(attrConnect[1], lock=True)
		else:
			if inputPlug:
				Logger.warn('{} already has connection from {}, skipped'.format(attrConnect[1], inputPlug[0]))
			elif lock:
				logger.warn('{} is locked, skipped'.format(attrConnect[1]))
