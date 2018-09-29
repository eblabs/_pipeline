# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import naming.naming as naming
import nodes
# ---- import end ----

# add attr
def addAttrs(node, attrs, attributeType='float', minValue=None, maxValue=None, defaultValue=None, keyable=True, channelBox=True, enumName='', lock=False):
	'''
	add attrs

	parameters:

	node(string): the node to add attrs
	attrs(string/list): add attrs
	attributeType(string): 'bool', 'long', 'enum', float', 'double', 
						   'string', 'matrix'
	minValue(float/int): min value
	maxValue(float/int): max value
	defaultValue(float/int/list): default value
	keyable(bool): set attr keyable, default is True
	channelBox(bool): show attr in channel box, default is True
	enumName(string): enum attr name
	lock(bool): lock attr, default is False
	'''
	if isinstance(attrs, basestring):
		attrs = [attrs]

	if not isinstance(defaultValue, list):
		defaultValue = [defaultValue]*len(attrs)

	for i, attr in enumerate(attrs):
		if not cmds.attributeQuery(attr, node = node, ex = True):
			# skip if the attr already exists
			# update parameters
			attrDic = {'longName': attr}
			if attributeType != 'string':
				attrDic.update({'attributeType': attributeType})
				if attributeType != 'matrix':
					attrDic.update({'keyable': keyable})
					if not channelBox:
						attrDic['keyable'] = False
					if defaultValue[i] != None:
						attrDic.update({'defaultValue': defaultValue[i]})
					if attributeType not in ['bool', 'enum']:
						if minValue != None:
							attrDic.update({'minValue': minValue})
						if maxValue != None:
							attrDic.update({'maxValue': maxValue})
					elif attributeType == 'enum':
						attrDic.update({'enumName': enumName})
			else:
				attrDic.update({'dataType': attributeType})
			# add attr to node	
			cmds.addAttr(node, **attrDic)
			# lock
			cmds.setAttr('{}.{}'.format(node, attr), lock = lock)
			# channelBox
			if attributeType not in ['string', 'matrix']:
				cmds.setAttr('{}.{}'.format(node, attr), 
							 channelBox = channelBox)

# set attrs
def setAttrs(attrs, value, node=None, type=None, force=True):
	'''
	set attrs

	parameters:

	attrs(string/list): attrs need to be set
	value(int/float/string/matrix/bool/list): attrs value
	node(string): node to override the attr
	type(string): if need to be specific, string/matrix
	force: force set value if locked (will skip connections anyway) 	
	'''
	if isinstance(attrs, basestring):
		attrs = [attrs]
	for i, attr in enumerate(attrs):
		attrCompose = __attrExistsCheck(attr, node = node)
		if attrCompose:
			# set if exists
			# check connections, skip if have connection
			connections = cmds.listConnections(attrCompose, source = True, 
									   destination = False, plugs = True, 
									   skipConversionNodes = True)
			if not connections:
				# check if type not matrix
				setAttrDic = {}
				if type != 'matrix':
					if isinstance(value, list):
						v = value[i]
					else:
						v = value
					if type == 'string':
						setAttrDic.update({'type': 'string'})
				else:
					if isinstance(value[0], list):
						v = value[i]
					else:
						v = value
					setAttrDic.update({'type': 'matrix'})

				lock = cmds.getAttr(attrCompose, lock = True)
				if not lock or force:
					cmds.setAttr(attrCompose, lock = False)
					cmds.setAttr(attrCompose, v, **setAttrDic)
					if lock:
						lock = cmds.setAttr(attrCompose, lock = True)
				else:
					logger.warn('{} is locked, skipped'.format(attrCompose))
			else:
				logger.warn('{} is connected, skipped'.format(attrCompose))
		else:
			logger.warn('{} does not exist, skipped'.format(attrCompose))

# lock and hide attrs
def lockHideAttrs(node, attrs):
	'''
	lock and hide attrs
	
	parameters:

	node(string): the node to lock and hide attrs
	attrs(string/list): lock and hide given attrs
	'''
	if isinstance(attrs, basestring):
		attrs = [attrs]

	for attr in attrs:
		if cmds.attributeQuery(attr, node = node, ex = True):
			# check if attr exists, skip if not
			cmds.setAttr('{}.{}'.format(node, attr), 
						 keyable = False,
						 lock = True,
						 channelBox = False)

# unlock attrs
def unlockAttrs(node, attrs, keyable=True, channelBox=True):
	'''
	unlock attrs

	parameters:

	node(string): the node to unlock and show attrs
	attrs(string/list): unlock and show(optional) given attrs
	keyable(bool): set attr keyable, default is True
	channelBox(bool): show attr in channel box, default is True
	'''
	if isinstance(attrs, basestring):
		attrs = [attrs]

	if not channelBox:
		keyable = False

	for attr in attrs:
		if cmds.attributeQuery(attr, node = node, ex = True):
			# check if attr exists, skip if not
			cmds.setAttr('{}.{}'.format(node, attr), 
						 lock = False,
						 keyable = keyable)
			cmds.setAttr('{}.{}'.format(node, attr), channelBox = channelBox)

# connect attrs
def connectAttrs(driverAttrs, drivenAttrs, driver=None, driven=None, force=True):
	'''
	connect attrs

	parameters:

	driverAttrs(string/list): source attr
	drivenAttrs(string/list): target attr
	driver(string): override the node in driverAttrs, default is None
	driven(string): override the node in drivenAttrs, default is None
	force(bool): override the connection/lock status, default is True
	'''
	# check if driverAttrs is string
	if isinstance(driverAttrs, basestring):
		driverAttrs = [driverAttrs]

	# check if drivenAttrs is string
	if isinstance(drivenAttrs, basestring):
		drivenAttrs = [drivenAttrs]

	if len(driverAttrs) == 1:
		# check if have single driver and multi driven attrs
		# check if attr exits, return if not
		driverExists = __attrExistsCheck(driverAttrs[0], node = driver)
		if not driverExists:
			return

		# loop each
		for attr in drivenAttrs:
			__connectSingleAttr(driverAttrs[0], attr, driver = driver,
								driven = driven, force = force)
	
	else:
		# attr should connect one by one from driver and driven
		# in case the two list's number not match, skip the extras
		num = min(len(driverAttrs), len(drivenAttrs))
		for i in range(num):
			__connectSingleAttr(driverAttrs[i], drivenAttrs[i], 
								driver = driver, driven = driven,
								force = force)

def attrInChannelBox(node, attr):
	attr = '{}.{}'.format(node, attr)
	return cmds.getAttr(attr, keyable = True) or cmds.getAttr(attr, cb = True)

def listAttrsInChannelBox(node):
	attrsAll = cmds.listAttr(node, w = True, r = True)
	attrsKeyable = cmds.listAttr(node, keyable = True)
	attrsNonKeyable = cmds.listAttr(node, cb = True)

	attrsSum = attrsKeyable + attrsNonKeyable
	attrsIndex = []

	for attr in attrsSum:
		index = attrsAll.index(attr)
		attrsIndex.append(index)

	attrsIndex.sort()

	attrs = []
	for index in attrsIndex:
		attrs.append(attrsAll[index])

	return attrs

def copyConnectAttrs(driver, driven, attrs=[]):
	attrsDriver = listAttrsInChannelBox(driver)
	attrsDriven = listAttrsInChannelBox(driven)

	if not attrs:
		attrs = attrsDriven

	if attrs == attrsDriver:
		return

	for attr in attrs:
		if attr in attrsDriven and attr not in attrsDriver:
			# in case the attr is hidden in driver
			if not cmds.attributeQuery(attr, node = driver, ex = True):
				kwargs = {'ln': attr}
				attrType = cmds.getAttr(driven + '.' + attr, type = True)
				dv = cmds.addAttr(driven + '.' + attr, q = True, dv = True)
				keyable = cmds.getAttr(driven + '.' + attr, keyable = True)

				kwargs.update({'at': attrType, 'dv': dv, 'keyable': keyable})
				
				lock = cmds.getAttr(driven + '.' + attr, lock = True)

				if attrType != 'enum':
					maxVal = cmds.addAttr(driven + '.' + attr, q = True, max = True)
					minVal = cmds.addAttr(driven + '.' + attr, q = True, min = True)
					kwargs.update({'max': maxVal, 'min': minVal})
				else:
					enumName = cmds.attributeQuery(attr, node = driven, le = True)[0]
					kwargs.update({'enumName': enumName})

				cmds.addAttr(driver, **kwargs)
				cmds.setAttr(driver + '.' + attr, channelBox = True, lock = lock)
				__connectSingleAttr(attr, attr, driver = driver, driven = driven)

				cmds.setAttr(driven + '.' + attr, keyable = False, channelBox = False)
			elif attr in attrsDriver:
				try:
					__connectSingleAttr(attr, attr, driver = driver, driven = driven)
				except:
					pass

# add reverse node
def addRvsAttr(node, attr, addAttr=False):
	NamingNode = naming.Naming(node)
	rvsNode = nodes.create(type = 'reverse', side = NamingNode.side,
				part = '{}{}{}Rvs'.format(NamingNode.part, attr[0].upper(), attr[1:]), 
				index = NamingNode.index)
	cmds.connectAttr('{}.{}'.format(node, attr), '{}.inputX'.format(rvsNode))
	outputPlug = '{}.outputX'.format(rvsNode)
	if addAttr:
		cmds.addAttr(node, ln = '{}Rvs'.format(attr), at = 'float', 
					 min = 0, max = 1, keyable = False)
		cmds.connectAttr(outputPlug, '{}.{}Rvs'.format(node, attr))
		outputPlug = '{}.{}Rvs'.format(node, attr)
	return outputPlug

# sub function
# check if attr exists
def __attrExistsCheck(attr, node=None):
	if node:
		if '.' in attr:
			attr = attr.split('.')[1]
	else:
		node = attr.split('.')[0]
		attr = attr.split('.')[1]

	if cmds.attributeQuery(attr, node = node, ex = True):
		return '{}.{}'.format(node, attr)
	else:
		logger.warn('{} does not have attr {}'.format(node, attr))
		return None

# connect single attr
def __connectSingleAttr(driverAttr, drivenAttr, driver=None, driven=None, force=True):
	driver = __attrExistsCheck(driverAttr, node = driver)
	if not driver:
		return

	driven = __attrExistsCheck(drivenAttr, node = driven)
	if not driven:
		return

	# check if driven has connection
	connections = cmds.listConnections(driven, source = True, 
									   destination = False, plugs = True, 
									   skipConversionNodes = True)
	# check if driven has been locked
	lock = cmds.getAttr(driven, lock = True)

	if not connections and not lock:
		cmds.connectAttr(driver, driven)
	else:
		if force:
			if connections[0] != driver:
				cmds.setAttr(driven, lock = False)
				cmds.connectAttr(driver, driven, f = True)						
				if lock:
					cmds.setAttr(driven, lock = True)
		else:
			if connections:
				logger.warn('{} already has connection from {}, skipped'.format(driven, connections[0]))
			elif lock:
				logger.warn('{} is locked, skipped'.format(driven))

