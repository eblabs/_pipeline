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
import attributes
import apiUtils
import nodeUtils
# ---- import end ----

# create transform node
def createTransformNode(name, lockHide=[], parent=None, rotateOrder=0, vis=True, posPoint=None, posOrient=None, posParent=None, inheritsTransform=True):	
	'''
	create transform node

	parameters:

	name(string): transform node's name
	lockHide(list): lock and hide transform node's attributes, default is []
	parent(string): parent transform node to the given node, default is None
	rotateOrder(int): transform node's rotate order, default is 0(xyz)
	vis(bool): transform node's visibility, default is True
	posPoint(string/list): match transform node's translate to given node or
						   position, default is None
	posOrient(string/list): match transform node's rotation to given node or 
							position, default is None
	posParent(string/list): match transform node's position to given node or 
							position, default is None
	inheritsTransform(bool): set transform node's inheritance, default is True
	'''

	# create group node
	cmds.group(empty  = True, name = name)

	# set rotate order
	cmds.setAttr('{}.ro'.format(name), rotateOrder)

	# set visibility
	cmds.setAttr('{}.v'.format(name), vis)

	# set inheritance
	cmds.setAttr('{}.inheritsTransform'.format(name), inheritsTransform)

	# matach position
	setNodePos(name, posPoint = posPoint, posOrient = posOrient, posParent = posParent)

	# check if need parent the transform node to given object
	if parent and cmds.objExists(parent):
		cmds.parent(name, parent)

	# lock and hide attrs
	attributes.lockHideAttrs(name, lockHide)

	return name

# create transform nodes chain on nodes
def createOnHierarchy(nodes, search, replace, suffix='', parent=None, rotateOrder=False, lockHide=[]):
	nodesList = []
	if isinstance(search, basestring):
		search = [search]
	if isinstance(replace, basestring):
		replace = [replace]
	for i, n in enumerate(nodes):
		nodeNew = n
		for name in zip(search, replace):
			nodeNew = nodeNew.replace(name[0], name[1])
		NamingNode = naming.Naming(nodeNew)
		NamingNode.part += suffix
		nodeNew = createTransformNode(NamingNode.name, parent = parent, 
			rotateOrder = rotateOrder, posParent = node)
		nodesList.append(nodeNew)

	# connect
	for trans in zip(nodesList, nodes):
		parentNode = cmds.listRelatives(trans[1], p = True)
		if parentNode and parentNode[0] in nodes:
			index = nodes.index(parentNode[0])
			parent = nodesList[index]
			cmds.parent(trans[0], parent)
		attributes.lockHideAttrs(trans[0], lockHide)
		
	return nodesList

# set position
def setNodePos(node, posPoint=None, posOrient=None, posParent=None):
	# check if need match both translation and rotation
	if posParent:
		if isinstance(posParent, basestring) and cmds.objExists(posParent):
			transformSnap([posParent, node], type = 'parent')
		elif isinstance(posParent, list):
			cmds.xform(node, t = posParent[0], ws = True)
			cmds.xform(node, ro = posParent[1], ws = True)
	else:
		# check if need match translation
		if posPoint:
			if isinstance(posPoint, basestring) and cmds.objExists(posPoint):
				transformSnap([posPoint, node], type = 'point')
			elif isinstance(posPoint, list):
				cmds.xform(node, t = posPoint, ws = True)

		# check if need match rotation
		if posOrient:
			if isinstance(posOrient, basestring) and cmds.objExists(posOrient):
				transformSnap([posOrient, node], type = 'orient')
			elif isinstance(posOrient, list):
				cmds.xform(node, ro = posOrient, ws = True)

# transform snap
def transformSnap(nodes, type='parent', snapType='oneToAll', skipTranslate=None, skipRotate=None, skipScale=None, centerPivot=True, weight=0.5):

	'''
	transform snap

	parameters:

	nodes(list): at least two objects, father and child
	type(string): the way to match the position, default is 'parent'
				  1. point: only translation
				  2. orient: only rotation
				  3. parent: translation and rotation
				  4. scale: only scale
				  5. all: translation, rotation and scale
	snapType(string): the way to define father objects and child objects,
	 				  default is 'oneToAll'
	 				  1. oneToAll: single father and multi children
	 				  2. allToOne: multi fathers and single child
	skipTranslate(list): skip axis for translation snapping, default is None
	skipRotate(list): skip axis for rotation snapping, default is None
	skipScale(list): skip axis for scale snapping, default is None
	centerPivot(bool): The way to find average position for multi fathers,
					   It will use bounding box if set to True, 
					   otherwise will average by dividing the values,
					   default is True
	weight(float/list): weight for each father nodes, 
						float: if only two father nodes, 
							   the first is 1 - weight, second is weight
							   if more than two, it will be average
						list: each father node will be assigned a value
						default is 0.5
	'''
	if snapType == 'oneToAll':
		# single father object and multi children
		driver = nodes[0] # father
		driven = nodes[1:] # children

		for drivenEach in driven:
			ro = cmds.getAttr('{}.rotateOrder'.format(drivenEach))
			transformInfoDriver = getNodeTransformInfo(driver, 
													   rotateOrder = ro)
			__transformSnapSingle(transformInfoDriver, drivenEach, 
								  type = type, skipTranslate = skipTranslate,
								  skipRotate = skipRotate,
								  skipScale = skipScale)

	elif snapType == 'allToOne':
		# multi father objects and single child
		drivers = nodes[:-1] # fathers
		driven = nodes[-1] # child

		# get driver objects blend node
		blendNode = cmds.group(empty = True, name = 'TEMP_BLEND')
		ro = cmds.getAttr('{}.rotateOrder'.format(driven))
		cmds.setAttr('{}.ro'.format(blendNode), ro)

		cmds.delete(cmds.pointConstraint(drivers, blendNode, mo = False))
		cmds.delete(cmds.orientConstraint(drivers, blendNode, mo = False))
		cmds.delete(cmds.scaleConstraint(drivers, blendNode, mo = False))

		# get transformInfo
		transformInfoBlend = getNodeTransformInfo(blendNode, 
												  rotateOrder = ro)

		cmds.delete(blendNode)

		# find average position if center pivot
		if centerPivot:
			centerPivot, pntMax, pntMin = getNodesBoundingBoxInfo(drivers)
			transformInfoBlend[0] = centerPivot

		# transform snap
		__transformSnapSingle(transformInfoBlend, 
							  driven,
							  type = type,
							  skipTranslate = skipTranslate,
							  skipRotate = skipRotate,
							  skipScale = skipScale)

# get node's transform info
def getNodeTransformInfo(node, rotateOrder=None):
	'''
	get node's transform info

	parameters:

	node(string): given node
	rotateOrder(int/None): override the rotateOrder, 
						  None will remain the exist node one
						  default is None
	''' 
	if not rotateOrder:
		rotateOrder = cmds.getAttr('{}.rotateOrder'.format(node))
	MMatrix = apiUtils.getMMatrixFromNode(node)
	transformInfo = apiUtils.decomposeMMatrix(MMatrix, 
											  rotateOrder = rotateOrder)
	return transformInfo

# get node list transform info
def getNodeListTransformInfo(nodes, translate=True, rotate=True, scale=True):
	transformList = []
	for node in nodes:
		nodeInfo = []
		transformInfo = getNodeTransformInfo(node)
		if translate:
			nodeInfo.append(transformInfo[0])
		if rotate:
			nodeInfo.append(transformInfo[1])
		if scale:
			nodeInfo.append(transformInfo[2])
		if len(nodeInfo) == 1:
			nodeInfo = nodeInfo[0]
		transformList.append(nodeInfo)
	return transformList

# get closest node from given point
def getClosestNode(nodes, point):
	if isinstance(point, basestring):
		point = cmds.xform(point, q = True, t = True, ws = True)
	distanceList = []
	for node in nodes:
		nodePos = cmds.xform(node, q = True, t = True, ws = True)
		dis = apiUtils.distance(point, nodePos)
		distanceList.append(dis)
	disMin = min(distanceList)
	indexMin = distanceList.index(disMin)
	return nodes[indexMin]

# get node bounding box info
def getNodesBoundingBoxInfo(nodes):
	
	# check if give node or transform info
	if isinstance(nodes, basestring):
		nodes = [nodes]

	pntMax = []
	pntMin = []
	for i in range(3):
		pos = []
		for n in nodes:
			if isinstance(n, basestring):
				# is a node, need get transform info
				posVal = getNodeTransformInfo(n)[0][i]
			else:
				posVal = n[i]
			pos.append(posVal)
		pntMax.append(max(pos))
		pntMin.append(min(pos))
	
	# get center pivot
	centerPivot = []
	for i in range(3):
		centerPivot.append((pntMax[i] + pntMin[i])*0.5)
	return centerPivot, pntMax, pntMin

# create local matrix
def createLocalMatrix(node, parent, attrNode=None, nodeMatrix='worldMatrix[0]', parentMatrix='worldInverseMatrix[0]', attr='matrixLocal', inverseAttr='matrixLocalInverse', inverse=True):
	'''
	create local matrix, node' worldMatrix * parent's worldInverseMatrix

	parameters:
	node(string): child node
	parent(string): parent node
	attrNode(string): where to put the attrs, None will be the child node
	nodeMatrix(string): node's attr to plug into multMatrix node
	parentMatrix(string): parent's attr to plug into multMatrix node
	attr(string): where to connect the matrix, create if not set
	inverseAttr(string): where to connect the inverse matrix, create if not set
	inverse(bool): if need add inverse matrix, default is True
	'''
	if not attrNode:
		attrNode = node
	NamingNode = naming.Naming(attrNode)
	NamingNode.type = 'multMatrix'
	NamingNode.part = NamingNode.part + attr[0].upper() + attr[1:]

	multMatrix = nodeUtils.create(name = NamingNode.name)
	attributes.connectAttrs(['{}.{}'.format(node, nodeMatrix),
							 '{}.{}'.format(parent, parentMatrix)],
							 ['matrixIn[0]', 'matrixIn[1]'], 
							 driven = multMatrix, force = True)

	if not cmds.attributeQuery(attr, node = attrNode, ex = True):
		cmds.addAttr(attrNode, ln = attr, at = 'matrix')

	driverAttrs = ['{}.matrixSum'.format(multMatrix)]
	drivenAttrs = ['{}.{}'.format(attrNode, attr)]

	if inverse:
		inverseAttr = attr + 'Inverse'
		NamingNode.type = 'inverseMatrix'
		inverseMatrix = nodeUtils.create(name = NamingNode.name)
		cmds.connectAttr('{}.matrixSum'.format(multMatrix),
						 '{}.inputMatrix'.format(inverseMatrix))

		if not cmds.attributeQuery(inverseAttr, node = attrNode, ex = True):
			cmds.addAttr(attrNode, ln = inverseAttr, at = 'matrix')

		driverAttrs.append('{}.outputMatrix'.format(inverseMatrix))
		drivenAttrs.append('{}.{}'.format(attrNode, inverseAttr))

	attributes.connectAttrs(driverAttrs, drivenAttrs, force = True)

# get node local matrix on the parent node
def getLocalMatrix(node, parent, nodeMatrix='worldMatrix[0]', parentMatrix='worldMatrix[0]', returnType = 'list'):
	matrixNode = cmds.getAttr('{}.{}'.format(node, nodeMatrix))
	matrixParent = cmds.getAttr('{}.{}'.format(parent, parentMatrix))

	MMatrixNode = apiUtils.convertListToMMatrix(matrixNode)
	MMatrixParent = apiUtils.convertListToMMatrix(matrixParent)

	outputMatrix = MMatrixNode * MMatrixParent.inverse()

	if returnType == 'list':
		outputMatrix = apiUtils.convertMMatrixToList(outputMatrix)

	return outputMatrix

# get pos world transform base on local transform and parent node
def getWorldTransformOnParent(translate=[0,0,0], rotate=[0,0,0], scale=[1,1,1], parent=None, parentMatrix='worldMatrix[0]', returnType='transformInfo'):
	MMatrixLocal = apiUtils.composeMMatrix(translate = translate, 
						rotate = rotate, scale = scale)
	matrixParent = cmds.getAttr('{}.{}'.format(parent, parentMatrix))
	MMatrixParent = apiUtils.convertListToMMatrix(matrixParent)

	MMatrixOutput = MMatrixLocal * MMatrixParent

	if returnType == 'transformInfo':
		outputInfo = apiUtils.decomposeMMatrix(MMatrixOutput)
	elif returnType == 'list':
		outputInfo = apiUtils.convertMMatrixToList(MMatrixOutput)
	else:
		outputInfo = MMatrixOutput

	return outputInfo

# extract twist
def extractTwist(node, nodeMatrix = 'worldMatrix[0]', attr='twist', reverseAttr = 'nonFlip', attrNode=None, quatOverride=None):
	if not attrNode:
		attrNode = node

	NamingNode = naming.Naming(node)
	if not quatOverride:
		decomposeMatrix = nodeUtils.create(type = 'decomposeMatrix', side = NamingNode.side,
							part = '{}TwistExctration'.format(NamingNode.part), index = NamingNode.index)
		cmds.connectAttr('{}.{}'.format(node, nodeMatrix), '{}.inputMatrix'.format(decomposeMatrix))
	else:
		decomposeMatrix = quatOverride
	quatToEuler = nodeUtils.create(type = 'quatToEuler', side = NamingNode.side,
						part = '{}TwistExctration'.format(NamingNode.part), index = NamingNode.index)
	
	cmds.connectAttr('{}.outputQuatX'.format(decomposeMatrix), '{}.inputQuatX'.format(quatToEuler))
	cmds.connectAttr('{}.outputQuatW'.format(decomposeMatrix), '{}.inputQuatW'.format(quatToEuler))
	
	if not cmds.attributeQuery(attr, node = attrNode, ex = True):
		cmds.addAttr(attrNode, ln = attr, at = 'float', keyable = False)

	attributes.connectAttrs('{}.outputRotateX'.format(quatToEuler), '{}.{}'.format(attrNode, attr), force = True)
	attributes.addWeightAttr(node, attr, weight = -1, addAttr = True, attrName = reverseAttr)

# ---- sub function
# single transform snap 
def __transformSnapSingle(transformInfoDriver, driven, type = 'parent', skipTranslate = None, skipRotate = None, skipScale = None,):

	# get driven transform info
	transformInfoDriven = getNodeTransformInfo(driven)

	# set skip axis for driven
	if type == 'point':
		skipRotate = ['x', 'y', 'z']
		skipScale = ['x', 'y', 'z']
	elif type == 'orient':
		skipTranslate = ['x', 'y', 'z']
		skipScale = ['x', 'y', 'z']
	elif type == 'parent':
		skipScale = ['x', 'y', 'z']
	elif type == scale:
		skipTranslate = ['x', 'y', 'z']
		skipRotate = ['x', 'y', 'z']

	if not skipTranslate:
		skipTranslate = []
	if not skipRotate:
		skipRotate = []
	if not skipScale:
		skipScale = []

	# get match transform info
	for i, axis in enumerate(['x', 'y', 'z']):
		if axis not in skipTranslate:
			transformInfoDriven[0][i] = transformInfoDriver[0][i]
		if axis not in skipRotate:
			transformInfoDriven[1][i] = transformInfoDriver[1][i]
		if axis not in skipScale:
			transformInfoDriven[2][i] = transformInfoDriver[2][i]

	# set value
	cmds.xform(driven, t = transformInfoDriven[0], ws = True)
	cmds.xform(driven, ro = transformInfoDriven[1], ws = True)
	cmds.xform(driven, s = transformInfoDriven[2], ws = True)

