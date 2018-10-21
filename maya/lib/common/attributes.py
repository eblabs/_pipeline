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
import nodeUtils
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
			attrDict = {'longName': attr}
			if attributeType != 'string':
				attrDict.update({'attributeType': attributeType})
				if attributeType != 'matrix':
					attrDict.update({'keyable': keyable})
					if not channelBox:
						attrDict['keyable'] = False
					if defaultValue[i] != None:
						attrDict.update({'defaultValue': defaultValue[i]})
					if attributeType not in ['bool', 'enum']:
						if minValue != None:
							attrDict.update({'minValue': minValue})
						if maxValue != None:
							attrDict.update({'maxValue': maxValue})
					elif attributeType == 'enum':
						attrDict.update({'enumName': enumName})
			else:
				attrDict.update({'dataType': attributeType})
			# add attr to node	
			cmds.addAttr(node, **attrDict)
			if attributeType in ['string', 'matrix'] and defaultValue[i]:
				cmds.setAttr('{}.{}'.format(node, attr), defaultValue[i], type = attributeType)
			# lock
			cmds.setAttr('{}.{}'.format(node, attr), lock = lock)
			# channelBox
			if attributeType not in ['string', 'matrix']:
				if channelBox and not attrDict['keyable']:
					cmds.setAttr('{}.{}'.format(node, attr), 
								 channelBox = True)

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
				setAttrDict = {}
				if type != 'matrix':
					if isinstance(value, list):
						v = value[i]
					else:
						v = value
					if type == 'string':
						setAttrDict.update({'type': 'string'})
				else:
					if isinstance(value[0], list):
						v = value[i]
					else:
						v = value
					setAttrDict.update({'type': 'matrix'})

				lock = cmds.getAttr(attrCompose, lock = True)
				if not lock or force:
					cmds.setAttr(attrCompose, lock = False)
					cmds.setAttr(attrCompose, v, **setAttrDict)
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
			cmds.setAttr('{}.{}'.format(node, attr), lock = False)
			cmds.setAttr('{}.{}'.format(node, attr), channelBox = channelBox)
			cmds.setAttr('{}.{}'.format(node, attr), keyable = keyable)

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

# add divider
def addDivider(nodes, name):
	if isinstance(nodes, basestring):
		nodes = [nodes]
	for n in nodes:
		attrName = name + 'Divider'
		if not cmds.attributeQuery(attrName, n = n, ex = True):
			cmds.addAttr(n, ln = attrName, nn = '{}{}__________:'.format(name[0].upper(), name[1:]), at = 'enum', en = ' ')
			cmds.setAttr('{}.{}'.format(n, attrName), channelBox = True, lock = True)

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
					if maxVal:
						kwargs.update({'max': maxVal})
					if minVal:
						kwargs.update({'min': minVal})
				else:
					enumName = cmds.attributeQuery(attr, node = driven, le = True)[0]
					kwargs.update({'enumName': enumName})
				cmds.addAttr(driver, **kwargs)
				cmds.setAttr(driver + '.' + attr, channelBox = True, lock = lock)
				cmds.setAttr(driver + '.' + attr, keyable = keyable)
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
	rvsNode = nodeUtils.create(type = 'reverse', side = NamingNode.side,
				part = '{}{}{}Rvs'.format(NamingNode.part, attr[0].upper(), attr[1:]), 
				index = NamingNode.index)
	cmds.connectAttr('{}.{}'.format(node, attr), '{}.inputX'.format(rvsNode))
	outputPlug = '{}.outputX'.format(rvsNode)
	if addAttr:
		if not attributeQuery(attr, node = node, ex = True):
			cmds.addAttr(node, ln = '{}Rvs'.format(attr), at = 'float', 
						 min = 0, max = 1, keyable = False)
		cmds.connectAttr(outputPlug, '{}.{}Rvs'.format(node, attr), f = True)
		outputPlug = '{}.{}Rvs'.format(node, attr)
	return outputPlug

# add weight attr
def addWeightAttr(node, attr, weight=-1, addAttr=False, attrName=None):
	NamingNode = naming.Naming(node)
	multNode = nodeUtils.create(type = 'multDoubleLinear', side = NamingNode.side,
				part = '{}{}{}Weight'.format(NamingNode.part, attr[0].upper(), attr[1:]), 
				index = NamingNode.index)
	cmds.connectAttr('{}.{}'.format(node, attr), '{}.input1'.format(multNode))
	cmds.setAttr('{}.input2'.format(multNode), weight, lock = True)
	outputPlug = '{}.output'.format(multNode)
	if addAttr:
		if not attrName:
			attrName = '{}Weight'.format(attr)
		if not cmds.attributeQuery(attrName, node = node, ex = True):
			cmds.addAttr(node, ln = attrName, at = 'float', keyable = False)
		cmds.connectAttr(outputPlug, '{}.{}'.format(node, attrName), f = True)
		outputPlug = '{}.{}'.format(node, attrName)
	return outputPlug

# show and hide history in channelbox
def showHideHistory(nodes=[], exception=[], listAll=True, vis=0):
	visOrig = 1 - vis
	if not nodes:
		nodes = cmds.ls(persistentNodes = True)
	for n in nodes:
		historyVis = visOrig
		for t in exception:
			if n.statrswith(t):
				nodes.remove(n)
				historyVis += 1
				break
		historyVis = abs(historyVis - 1)*2
		cmds.setAttr('{}.isHistoricallyInteresting'.format(n), historyVis)

# weight blend attribute
def weightBlendAttr(nodes, attr, driverAttrs=[], weightList=[], attrType='single', attrRemap=['XYZ','XYZ']):
	if isinstance(nodes, basestring):
		nodes = [nodes]

	attrNum = len(driverAttrs)

	if not weightList:
		weightList = [float(1)/float(attrNum)] * attrNum

	NamingNode = naming.Naming(nodes[0])
	NamingNode.part = '{}{}{}Blend'.format(NamingNode.part, attr[0].upper(), attr[1:])
	plusAttr = nodeUtils.create(type = 'plusMinusAverage', side = NamingNode.side,
							part = NamingNode.part, index = NamingNode.index)
	
	if attrType == 'single':
		attrIn = 'output1D'
		attrOut = attr
		nodeTypeIn = 'multDoubleLinear'

	elif attrType == 'double':
		attrIn = ['output2Dx', 'output2Dy']
		attrOut = [attr + attrRemap[1][0], attr + attrRemap[1][1]]
		nodeTypeIn = 'multiplyDivide'

	elif attrType == 'triple':
		attrIn = ['output3Dx', 'output3Dy', 'output3Dz']
		attrOut = [attr + attrRemap[1][0],
				   attr + attrRemap[1][1],
				   attr + attrRemap[1][2]]
		nodeTypeIn = 'multiplyDivide'

	for node in nodes:
		connectAttrs(attrIn, attrOut, driver = plusAttr, driven = node)

	for i in range(attrNum):
		if weightList[i] != 0:
			mult = nodeUtils.create(type = nodeTypeIn, side = NamingNode.side,
								part = NamingNode.part, index = NamingNode.index,
								suffix = i+1)
			if attrType == 'single':
				cmds.connectAttr(driverAttrs[i], '{}.input1'.format(mult))
				cmds.setAttr('{}.input2'.format(mult), weightList[i], lock = True)
				cmds.connectAttr('{}.output'.format(mult), '{}.input1D[{}]'.format(plusAttr, i))
			
			elif attrType == 'double':
				connectAttrs([driverAttrs[i] + attrRemap[0][0],
							  driverAttrs[i] + attrRemap[0][1]] , 
							  ['{}.input1X'.format(mult),
							  '{}.input1Y'.format(mult)])
				setAttrs(['input2X', 'input2Y'], weightList[i], node = mult)
				connectAttrs(['outputX', 'outputY'], 
							 ['{}.input2D[0].input2Dx'.format(plusAttr), 
							  '{}.input2D[1].input2Dx'.format(plusAttr)],
							 driver = mult)

			elif attrType == 'triple':
				connectAttrs([driverAttrs[i] + attrRemap[0][0],
							  driverAttrs[i] + attrRemap[0][1],
							  driverAttrs[i] + attrRemap[0][2],] , 
							  ['{}.input1X'.format(mult),
							  '{}.input1Y'.format(mult),
							  '{}.input1Z'.format(mult)])
				setAttrs(['input2X', 'input2Y', 'input2Z'], weightList[i], node = mult)
				connectAttrs(['outputX', 'outputY', 'outputZ'], 
							 ['{}.input3D[0].input3Dx'.format(plusAttr), 
							  '{}.input3D[1].input3Dy'.format(plusAttr), 
							  '{}.input3D[2].input3Dz'.format(plusAttr)],
							 driver = mult)
	return plusAttr


# sub function
# check if attr exists
def __attrExistsCheck(attr, node=None):
	if not node:
		node = attr.split('.')[0]
		attr = attr.replace(node + '.', '')
	try:
		cmds.getAttr('{}.{}'.format(node, attr))
		return '{}.{}'.format(node, attr)
	except:
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
			cmds.setAttr(driven, lock = False)
			try:
				cmds.connectAttr(driver, driven, f = True)
			except:
				pass		
			if lock:
				cmds.setAttr(driven, lock = True)
		else:
			if connections:
				logger.warn('{} already has connection from {}, skipped'.format(driven, connections[0]))
			elif lock:
				logger.warn('{} is locked, skipped'.format(driven))

