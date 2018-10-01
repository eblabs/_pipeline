# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import time
import time

# -- import os
import os

# -- import maya lib
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
# -- import lib
import common.naming.naming as naming
import common.transforms as transforms
import common.files.files as files
import common.apiUtils as apiUtils
import common.attributes as attributes
import common.naming.namingDict as namingDict
import modeling.curves as curves
import modeling.geometries as geometries
# ---- import end ----

# ---- global variable
path_ctrlShapeDic = 'C:/_pipeline/maya/lib/rigging/controls/controlShapes.json'
path_ctrlColorDic = 'C:/_pipeline/maya/lib/rigging/controls/controlColors.json'
path_sideColorDic = 'C:/_pipeline/maya/lib/rigging/controls/sideColors.json'

class Control(object):
	"""
	a wrapper for controller

	property:
	name: return the control's name
	side: return the control's side
	part: return the control's part
	index: return the control's index
	zero: return the control's zero group
	passer: return the control's passer group
	space: return the control's space group
	stacks: return the control's stack groups list
	StacksNum: return how many stack groups the control have
	sub: return the control's sub control name
	output: return the node used to constraint with other objects
	sideLongName: return the control's side's long name
	MMatrixLocal: return the control's local matrix as MMatrix(or MMatrixV2) 
				  object (local matrix is from output to passer)
	MMatrixWorld: return the control's world matrix as MMatrix(or MMatrixV2)
				  object (world matrix is from output to zero)
	MMatrixLocalInverse: return the control's local matrix inverse as 
						 MMatrix(or MMatrixV2) object (local matrix is from 
						 output to passer)
	MMatrixWorldInverse: return the control's world matrix inverse as 
						 MMatrix(or MMatrixV2) object (world matrix is from 
						 output to zero)
	matrixLocalPlug: return the control's local matrix attribute plug(local matrix
					 is from output to passer)// format: control.attr
	matrixWorldPlug: return the control's world matrix attribute plug() (world matrix 
					 is from output to zero)// format: control.attr
	matrixLocalInversePlug: return the control's local inverse matrix attribute plug
							(local matrix is from output to passer)// format: control.attr
	matrixWorldInversePlug: return the control's world inverse matrix attribute plug
							(world matrix is from output to zero)// format: control.attr
	matrixLocalAttr: return the control's local matrix attribute(local matrix
					 is from output to passer)
	matrixWorldAttr: return the control's world matrix attribute (world matrix is from 
					 output to zero)
	matrixLocalInverseAttr: return the control's local inverse matrix attribute
							(local matrix is from output to passer)
	matrixWorldInverseAttr: return the control's world inverse matrix attribute
							(world matrix is from output to zero)

	functions:
	transformCtrlShape: transform control's shape node
	matchCtrlShape: match control's shape node between control and sub control
	changeCtrlShape: change control's shape
	setCtrlShapeColor: change control's shape's color

	setAttr:
	side: set the control's side
	part: set the control's part name
	index: set the control's index
	stacks: set how many stacks the control has
	sub: set if the control has a sub control or not

	"""
	def __init__(self, ctrl):
		super(Control, self).__init__()
		self.__getControlInfo(ctrl)

	def __str__(self):
		self.__name

	@property
	def name(self):
		return self.__name

	@property
	def side(self):
		return self.__side

	@property
	def sideLongName(self):
		return namingDict.dNameConvensionInverse['side'][self.__side]

	@property
	def part(self):
		return self.__part

	@property
	def index(self):
		return self.__index

	@property
	def zero(self):
		return self.__zero

	@property
	def passer(self):
		return self.__passer

	@property
	def space(self):
		return self.__space

	@property
	def stacks(self):
		return self.__stacks

	@property
	def stacksNum(self):
		return self.__stacksNum

	@property
	def sub(self):
		return self.__sub

	@property
	def output(self):
		return self.__output

	@property
	def MMatrixLocal(self, type='MMatrix'):
		matrix = cmds.getAttr('{}.matrixLocal'.format(self.__name))
		MMatrix = apiUtils.convertListToMMatrix(matrix, type = type)
		return MMatrix

	@property
	def MMatrixWorld(self, type='MMatrix'):
		matrix = cmds.getAttr('{}.matrixWorld'.format(self.__name))
		MMatrix = apiUtils.convertListToMMatrix(matrix, type = type)
		return MMatrix

	@property
	def MMatrixLocalInverse(self, type='MMatrix'):
		matrix = cmds.getAttr('{}.matrixLocalInverse'.format(self.__name))
		MMatrix = apiUtils.convertListToMMatrix(matrix, type = type)
		return MMatrix

	@property
	def MMatrixWorldInverse(self, type='MMatrix'):
		matrix = cmds.getAttr('{}.matrixWorldInverse'.format(self.__name))
		MMatrix = apiUtils.convertListToMMatrix(matrix, type = type)
		return MMatrix
	
	@property
	def matrixLocalPlug(self):		
		return '{}.matrixLocal'.format(self.__name)

	@property
	def matrixWorldPlug(self):
		return '{}.matrixWorld'.format(self.__name)

	@property
	def matrixLocalInversePlug(self):
		return '{}.matrixLocalInverse'.format(self.__name)

	@property
	def matrixWorldInversePlug(self):
		return '{}.matrixWorldInverse'.format(self.__name)

	@property
	def matrixLocalAttr(self):		
		return 'matrixLocal'

	@property
	def matrixWorldAttr(self):
		return 'matrixWorld'

	@property
	def matrixLocalInverseAttr(self):
		return 'matrixLocalInverse'

	@property
	def matrixWorldInverseAttr(self):
		return 'matrixWorldInverse'

	@side.setter
	def side(self, key):
		shortName, longName = naming.Naming.getKeyFullNameFromDict(key, 
							  namingDict.dNameConvension['side'], 
							  namingDict.dNameConvensionInverse['side'])
		self.__side = shortName
		self.__updateControlName()

	@part.setter
	def part(self, key):
		self.__part = key
		self.__updateControlName()

	@index.setter
	def index(self, num):
		if isinstance(num, int) and num >= 0:
			self.__index = num
		else:
			self.__index = None
		self.__updateControlName()

	@stacks.setter
	def stacks(self, num):
		if isinstance(num, int) and num > 0:
			stacks = num
		else:
			stacks = 1
		self.__updateStacks(stacks)

	@sub.setter
	def sub(self, key):
		self.__updateSub(key)

	def __getControlInfo(self, ctrl):
		# get controller's information

		self.__name = ctrl # get controller name

		CtrlName = naming.Naming(ctrl) # wrap control's name as an object

		self.__side = CtrlName.side
		self.__part = CtrlName.part
		self.__index = CtrlName.index

		self.__stacksNum = cmds.getAttr('{}.stacks'.format(ctrl))
		self.__subExists = cmds.getAttr('{}.sub'.format(ctrl))

		CtrlName.type = 'space' # get space grp name
		self.__space = CtrlName.name

		CtrlName.type = 'passer' # get passer name
		self.__passer = CtrlName.name

		CtrlName.type = 'zero' # get zero grp name 
		self.__zero = CtrlName.name

		CtrlName.type = 'output' # get output node name
		self.__output = CtrlName.name

		CtrlName.type = 'stack' # get stack name
		self.__stacks = []
		for i in range(self.__stacksNum):
			CtrlName.suffix = i + 1
			self.__stacks.append(CtrlName.name)

		if self.__subExists:
			# if controller have sub control
			CtrlSubName = naming.Naming(type = 'control', 
										side = self.__side,
										part = '{}Sub'.format(self.__part),
										index = self.__index)
			self.__sub = CtrlSubName.name
		else:
			self.__sub = None

		# matrix nodes
		MatrixName = naming.Naming(type = 'multMatrix', side = self.__side,
								   part = '{}MatrixLocal'.format(self.__part),
								   index = self.__index)
		self.__multMatrixLocal = MatrixName.name

		MatrixName.type = 'inverseMatrix'
		self.__inverseMatrixLocal = MatrixName.name

	def __updateControlName(self):
		# update control name
		NamingGrp = naming.Naming(type = 'zero', side = self.__side, 
								  part = self.__part, index = self.__index)
		# zero
		self.__zero = cmds.rename(self.__zero, NamingGrp.name)

		# passer
		NamingGrp.type = 'passer'
		self.__passer = cmds.rename(self.__passer, NamingGrp.name)

		# space
		NamingGrp.type = 'passer'
		self.__space = cmds.rename(self.__space, NamingGrp.name)

		# stacks
		NamingGrp.type = 'stack'
		for i in range(self.__stacksNum):
			NamingGrp.suffix = i + 1
			self.__stacks[i] = cmds.rename(self.__stacks[i], NamingGrp.name)

		# ctrl
		NamingGrp.type = 'ctrl'
		NamingGrp.suffix = None
		NamingGrp.index = self.__index
		self.__name = cmds.rename(self.__name, NamingGrp.name)

		# output
		NamingGrp.type = 'output'
		self.__output = cmds.rename(self.__output, NamingGrp.name)

		# sub
		if self.__subExists:
			NamingGrp.type = 'ctrl'
			NamingGrp.part = '{}Sub'.format(self.__part)
			self.__sub = cmds.rename(self.__sub, NamingGrp.name)

		# matrix nodes
		NamingGrp.type = 'multMatrix'
		NamingGrp.part = '{}MatrixLocal'.format(self.__part)
		self.__multMatrixLocal = cmds.rename(self.__multMatrixLocal, 
											 NamingGrp.name)

		NamingGrp.type = 'inverseMatrix'
		self.__inverseMatrixLocal = cmds.rename(self.__inverseMatrixLocal,
												NamingGrp.name)

	def __updateStacks(self, num):
		NamingStack = naming.Naming(type = 'stack', side = self.__side, 
									part = self.__part, index = self.__index,
									suffix = self.__stacksNum)
		childs = cmds.listRelatives(NamingStack.name, c = True, 
									type = 'transforms')
		stack = NamingStack.name
		if self.__stacksNum < num:
			# check if need more
			childs = cmds.listR
			for i in rang(num - self.__stacksNum):
				NamingStack.suffix = self.__stacksNum + i + 1
				stack = transforms.createTransformNode(NamingStack.name, 
													   parent = stack,
													   posParent = stack)
				self.__stacks.append(stack)
			# reparent nodes
			cmds.parent(childs, stack)
		elif self.__stacksNum > num:
			# need delete extras
			NamingStack.suffix = num
			# reparent nodes
			cmds.parent(nodes, NamingStack.name)
			# delete extras
			NamingStack.suffix = num + 1
			cmds.delete(NamingStack.name)
			self.__stacks = self.__stacks[:num]

		self.__stacksNum = num

		# update ctrl attr
		attributes.setAttrs('stacks', num, node = self.__name, force=True)

	def __updateSub(self, key):
		if self.__subExists and not key:
			# delete
			cmds.delete(self.__sub)
			cmds.deleteAttr('%s.subCtrlVis' %self.__name)
			self.__sub = None
		elif not self.__subExists and key:
			# add
			NamingSub = naming.Naming(type = 'ctrl', side = self.__side,
									  part = '{}Sub'.format(self.__part),
									  index = self.__index)

			# get lock hide attrs from ctrl
			lockHide = []
			for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 
						 'sx', 'sy', 'sz', 'v']:
				if not attributes.attrInChannelBox(self.__name, attr):
					lockHide.append(attr)

			self.__sub = createTransformNode(NamingSub.name, 
											 parent = self.__name,
											 posParent = self.__name,
											 lockHide = lockHide)

			# add sub ctrl vis attr
			attributes.addAttrs(self.__name, 'subCtrlVis', 
						attributeType = 'bool', defaultValue = 0, 
						keyable = False, channelBox = True)

			# show rotate order
			attributes.unlockAttrs(self.__sub, 'rotateOrder', keyable = True, 
								   channelBox = True)

			# connect with output
			attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz',
									 'sx', 'sy', 'sz', 'rotateOrder'],
									['tx', 'ty', 'tz', 'rx', 'ry', 'rz',
									 'sx', 'sy', 'sz', 'rotateOrder'],
					 				driver = self.__sub, 
					 				driven = self.__output, force = True)

			# connect with ctrl vis
			attributes.connectAttrs('subCtrlVis', 'v', driver = self.__name, 
									driven = self.__sub, force = True)

			self.matchSubCtrlShape()

		self.__subExists = key
		attributes.setAttrs('sub', key, node = self.__name, force=True)

	def __getControllers(self, sub=True, subOnly=False):
		ctrls = []
		if not subOnly:
			ctrls.append(self.__name)
			if sub and self.__subExists:
				ctrls.append(self.__sub)
		elif self.__subExists:
			ctrls.append(self.__sub)
		return ctrls

	def transformCtrlShape(self, translate = [0,0,0], rotate=[0,0,0], scale=[1,1,1], pivot = 'transform', sub=False):
		ctrlShapes = [cmds.listRelatives(self.__name, s = True)[0]]
		if sub and self.__subExists:
			subShape = cmds.listRelatives(self.__sub, s = True)[0]
			ctrlShapes.append(subShape)
		transformCtrlShape(ctrlShapes, translate = translate, rotate = rotate,
		 				   scale = scale, pivot = pivot)

	def matchCtrlShape(self, size=0.8, sub=True):
		if self.__subExists:
			if sub:
				ctrlSource = self.__name
				ctrlTarget = self.__sub
			else:
				ctrlSource = self.__sub
				ctrlTarget = self.__name
			# get shape info from ctrl
			ctrlShapeInfo = __getCtrlShapeInfo(ctrlSource)

			# add sub ctrl shape
			addCtrlShape(ctrlTarget, shape = ctrlShapeInfo, size = size)

	def changeCtrlShape(self, shape, size=1, color=None, colorOverride=False, sub=True, subOnly=False):
		
		ctrls = self.__getControllers(sub=True, subOnly=False)

		for i, c in enumerate(ctrls):
			ctrlShapeInfo = __getCtrlShapeInfo(c)
			colorCtrl = ctrlShapeInfo['color']
			if colorOverride:
				colorCtrl = color

			if i == 1:
				size = size * 0.8
			addCtrlShape(c, shape = shape, size = size, color = colorCtrl, 
						 colorOverride = True)

	def setCtrlShapeColor(self, color, sub=False, subOnly=False):
		
		ctrls = self.__getControllers(sub=True, subOnly=False)
		
		for c in ctrls:
			setCtrlShapeColor(c, color)

	def setRotateOrder(self, ro, sub=True, subOnly=False):
		
		ctrls = self.__getControllers(sub=True, subOnly=False)
		
		for c in ctrls:
			cmds.setAttr('{}.ro'.format(c), ro)

	def lockHideAttrs(self, attrs, sub=True, subOnly=False):
		
		ctrls = self.__getControllers(sub=True, subOnly=False)
		
		for c in ctrls:
			attributes.lockHideAttrs(c, attrs)

	def unlockAttrs(self, attrs, sub=True, subOnly=False):
		
		ctrls = self.__getControllers(sub=True, subOnly=False)
		
		for c in ctrls:
			attributes.unlockAttrs(c, attrs)

# -- function ------

def create(part, side='middle', index=None, sub=True, stacks=1, parent=None, posPoint=None, posOrient=None, posParent=None, rotateOrder=0, shape='cube', size=1, color=None, colorSub = None, lockHide=[]):
	'''
	create controller function

	hierarchy:
	-zero
	--passer
	---space
	----stack_001
	-----stack_002
	------stack_...
	-------ctrl
	--------subCtrl
	--------output

	parameters:

	part(string): part name of the control
	side(string): side name of the control, default is 'middle'
	index(int): index of the control, None means no index, default is None
	sub(bool): if the control has sub control or not, default is True
	stacks(int): stack group number, minimum value is 1, default is 1
	parent(string): where to parent the control, default is None
	posPoint(string/list): match control's translate to given node or position,
						   default is None
	posOrient(string/list): match control's rotation to given node or position,
							default is None
	posParent(string/list): match control's position to given node or position,
							default is None
	rotateOrder(int): control's rotate order, default is 0(xyz)
	shape(string): control's shape, default is 'cube'
	size(float/list): control's size, default is 1
	color(string/int): control's color, it will follow the side's preset if set
					   to None, default is None
	colorSub(string/int): sub control's color, same with control if None,
	 					  default is None
	lockHide(list): lock and hide control's attributes, default is []

	'''
	if 'v' not in lockHide:
		lockHide.append('v')
		
	CtrlName = naming.Naming(type = 'control', side = side, part = part,
							 index = index) # get control's name

	# create hierarchy
	# zero transform node
	NamingGrp = naming.Naming(type = 'zero', side = side, part = part,
							  index = index)

	zero = transforms.createTransformNode(NamingGrp.name, parent = parent, 
										  posPoint = posPoint, 
										  posOrient = posOrient,
										  posParent = posParent)

	# passer transform node
	NamingGrp.type = 'passer'

	passer = transforms.createTransformNode(NamingGrp.name, parent = zero,
											posParent = zero)

	# space transform node
	NamingGrp.type = 'space'

	space = transforms.createTransformNode(NamingGrp.name, parent = passer,
										   posParent = passer)

	# stack transform node
	stackParent = space
	NamingGrp.type = 'stack'
	for i in range(stacks):
		NamingGrp.suffix = i+1
		stack = transforms.createTransformNode(NamingGrp.name, 
										       parent = stackParent,
										       posParent = stackParent)
		stackParent = stack

	# control transform node
	NamingGrp.type = 'ctrl'
	NamingGrp.suffix = None
	NamingGrp.index = index

	ctrl = transforms.createTransformNode(NamingGrp.name, parent = stack,
										  rotateOrder = rotateOrder,
										  posParent = stack,
										  lockHide = lockHide)

	# show rotate order
	attributes.unlockAttrs(ctrl, 'rotateOrder', keyable=True, channelBox=True)

	# add sub ctrl vis attr
	attributes.addAttrs(ctrl, 'subCtrlVis', attributeType = 'bool',
					    defaultValue = 0, keyable = False, channelBox = True)

	# output transform node
	NamingGrp.type = 'output'

	output = transforms.createTransformNode(NamingGrp.name, parent = ctrl,
											posParent = ctrl, vis = True,
											lockHide = ['tx', 'ty', 'tz',
														'rx', 'ry', 'rz',
														'sx', 'sy', 'sz',
														'v'])

	# add ctrl shape
	addCtrlShape(ctrl, shape = shape, size = size, color = color)

	# sub transform node
	if sub:
		NamingGrp.type = 'control'
		NamingGrp.part = '{}Sub'.format(NamingGrp.part)

		sub = transforms.createTransformNode(NamingGrp.name, parent = ctrl,
											 rotateOrder = rotateOrder,
											 posParent = ctrl,
											 lockHide = lockHide)

		# show rotate order
		attributes.unlockAttrs(sub, 'rotateOrder', keyable = True, 
							   channelBox = True)

		# connect with output
		attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz',
								 'sx', 'sy', 'sz', 'rotateOrder'],
								['tx', 'ty', 'tz', 'rx', 'ry', 'rz',
								 'sx', 'sy', 'sz', 'rotateOrder'],
				 				driver = sub, driven = output, force = True)

		# connect with ctrl vis
		attributes.connectAttrs('subCtrlVis', 'v', 
								driver = ctrl, driven = sub, force = True)

		# add sub ctrl shape
		if not colorSub:
			colorSub = color
		addCtrlShape(sub, shape = shape, size = size * 0.8, color = colorSub)

	# write control info
	attributes.addAttrs(ctrl, 'stacks', attributeType = 'long', 
							defaultValue = stacks, keyable = False, 
							channelBox = False, lock = True)

	attributes.addAttrs(ctrl, 'sub', attributeType = 'bool',
						defaultValue = bool(sub), keyable = False,
						channelBox = False, lock = True)

	attributes.addAttrs(ctrl, ['matrixLocal', 'matrixWorld', 
						'matrixLocalInverse', 'matrixWorldInverse'], 
						attributeType = 'matrix')

	# connect matrix
	# matrix world and inverse
	transforms.createLocalMatrix(output, zero, attrNode = ctrl, 
								  nodeMatrix = 'worldMatrix[0]', 
								  parentMatrix = 'parentInverseMatrix[0]', 
								  attr = 'matrixWorld',
								  inverseAttr = 'matrixWorldInverse', inverse=True)

	# matrix local and inverse
	transforms.createLocalMatrix(output, zero, attrNode = ctrl,
								 attr = 'matrixLocal', 
					  			 inverseAttr = 'matrixLocalInverse')

	return Control(ctrl)

# add ctrl shape
def addCtrlShape(ctrls, shape='cube', size=1, color=None, asCtrl=None, colorOverride=False):
	'''
	add shape node to ctrls

	parameters:
	
	ctrl(string/list): ctrls to assign the shape node
	shape(string/dictionary): ctrl shape
	size(flaot/list): ctrl shape size
	color(int/string): ctrl shape color
	asCtrl(string): if this shape is an extra ctrl (like ikfk switch)
	overrideType(int/string): 0 normal
							  1 template
							  2 reference
	'''
	if isinstance(ctrls, basestring):
		ctrls = [ctrls]
	for c in ctrls:
		if not asCtrl:
			NamingCtrl = naming.Naming(c)
			NamingCtrl.type = 'ctrlShape'
			if cmds.objExists(NamingCtrl.name):
				# delete shape node if exist
				cmds.delete(NamingCtrl.name)
			# set color if color is None, base on side
			if not color and isinstance(shape, basestring) and not colorOverride:
				sideColorsDic = files.readJsonFile(path_sideColorDic)
				if 'left' in NamingCtrl.sideLongName:
					colorCtrl = sideColorsDic['left']
				elif 'right' in NamingCtrl.sideLongName:
					colorCtrl = sideColorsDic['right']
				else:
					colorCtrl = sideColorsDic['middle']
			else:
				colorCtrl = color
			# add ctrlshape
			ctrlShape, ctrlName = __addCtrlShapeToTransform(c, 
									  shape = shape, color = colorCtrl, 
									  size = size, colorOverride = colorOverride)
	
			# assign shape
			cmds.reorder(ctrlShape, f = True)

		else:
			ctrlShape, ctrlName = __addCtrlShapeAsCtrl(c, asCtrl)

# transform ctrl shape
def transformCtrlShape(ctrlShapes, translate=[0,0,0], rotate=[0,0,0], scale=[1,1,1], pivot='transform'):
	'''
	transform ctrls shape node

	parameters:

	ctrlShapes(string/list): ctrl's shape node need to transform shape node
	translate(float/list): move shape node
	rotate(float/list): rotate shape node
	scale(float/list): scale shape node
	pivot(string): transform/shape, define where is the pivot
	'''
	if isinstance(ctrlShapes, basestring):
		ctrlShapes = [ctrlShapes]
	if not isinstance(translate, list):
		translate = [translate, translate, translate]
	if not isinstance(rotate, list):
		rotate = [rotate, rotate, rotate]
	if not isinstance(scale, list):
		scale = [scale, scale, scale]

	# transform shapes
	for c in ctrlShapes:
		if cmds.objExists(c):
			# transform if exists
			# get curve info
			ctrlShapeInfo = curves.__getCurveInfo(c)
			# get point local position
			ctrlPnts = ctrlShapeInfo['controlVertices']
			# get offset matrix
			MMatrixOffset = apiUtils.composeMMatrix(translate = translate, 
												rotate = rotate, scale = scale)
			# get pivot matrix
			if pivot == 'shape':
				cpPos, cpMin, cpMax = getNodesBoundingBoxInfo(ctrlPnts)
				MMatrixPivot = apiUtils.composeMMatrix(translate = cpPos)
			else:
				MMatrixPivot = apiUtils.composeMMatrix() 
			# move each point
			for i, pnt in enumerate(ctrlPnts):
				# get matrix
				MMatrixPnt = apiUtils.composeMMatrix(translate = pnt)

				# mult matrix
				MMatrixPos = MMatrixPnt * MMatrixPivot.inverse() * MMatrixOffset * MMatrixPivot
				
				# decompose matrix and get pos
				pos = apiUtils.decomposeMMatrix(MMatrixPos)[0]

				# update ctrlPnts
				ctrlPnts[i] = pos

			# convert ctrlPnts to MPointArray
			MPointArray = apiUtils.convertListToMPointArray(ctrlPnts)

			# get MFnNurbsCurve Obj
			MFnNurbsCurve = curves.__setMFnNurbsCurve(c)
			
			# set pos
			MFnNurbsCurve.setCVs(MPointArray, OpenMaya.MSpace.kObject)

# set ctrl color
def setCtrlShapeColor(ctrlShapes, color):
	if isinstance(ctrlShapes, basestring):
		ctrlShapes = [ctrlShapes]
	if isinstance(color, basestring):
		ctrlColorDic = files.readJsonFile(path_ctrlColorDic)
		color = ctrlColorDic[color]
	for c in ctrlShapes:
		if cmds.objectType(c) == 'transform':
			c = cmds.listRelatives(c, s = True)[0]
		cmds.setAttr('{}.colorOverride'.format(c), color)

# mirror ctrl shape
def mirrorCtrlShape(ctrls, sub = False, posToNeg=True, leftRight=True, upDown=False, frontBack = False):

	left = naming.namingDict['side']['left']
	right = naming.namingDict['side']['right']
	up = naming.namingDict['side']['up']
	down = naming.namingDict['side']['down']
	front = naming.namingDict['side']['front']
	back = naming.namingDict['side']['back']

	if isinstance(ctrls, basestring):
		ctrls = [ctrls]

	for c in ctrls:
		if cmds.objectType(c) != 'transform':
			c = cmds.listRelatives(c, p = True)[0]
		NamingCtrl = naming.Naming(c)
		side = NamingCtrl.side
		sideMirror = side
		mirrorAxis = [1,1,1]

		if posToNeg:
			if left not in side and up not in side and front not in side:
				# can not mirror from positive to negative
				logger.warn('{} can not mirror from positive axis to negative'.format(c))
			else:
				if left in side and leftRight:
					# mirror left to right
					mirrorAxis[0] = -1
					sideMirror.replace(left, right)
				if up in side.lower() and upDown:
					# mirror up to down
					mirrorAxis[1] = -1
					sideMirror.replace(up, down)
				if front in side.lower() and frontBack:
					# mirror front to back
					mirrorAxis[2] = -1
					sideMirror.replace(front, back)
		else:
			if right not in side and down not in side and back not in side:
				# can not mirror from negative to positive
				logger.warn('{} can not mirror from negative axis to positive'.format(c))
			else:
				if right in side and leftRight:
					# mirror left to right
					mirrorAxis[0] = -1
					sideMirror.replace(right, left)
				if down in side.lower() and upDown:
					# mirror up to down
					mirrorAxis[1] = -1
					sideMirror.replace(down, up)
				if back in side.lower() and frontBack:
					# mirror front to back
					mirrorAxis[2] = -1
					sideMirror.replace(back, front)

		NamingCtrl.side = sideMirror
		__mirrorSingleCtrlShape(c, NamingCtrl.name, mirrorAxis)

		if sub:
			NamingCtrl = naming.Naming(c)
			NamingCtrl.part = '{}Sub'.format(NamingCtrl.part)
			sub = NamingCtrl.name
			if cmds.objExists(sub):
				NamingCtrl.side = sideMirror
				__mirrorSingleCtrlShape(sub, NamingCtrl.name, mirrorAxis)

# save ctrl shape info
def saveCtrlShapeInfo(ctrls, path):
	startTime = time.time()

	ctrlShapeInfoDic = {}
	for c in ctrls:
		if cmds.objExists(c):
			ctrlInfo = __getCurveInfo(c)
			ctrlShapeInfoDic.update({c:ctrlInfo})
		else:
			logger.warn('{} does not exist, skipped'.format(c))

	fileFormat = files.readJsonFile(files.path_fileFormat)
	path = os.path.join(path, 'controlShapes.{}'.format(fileFormat['control']))

	files.writeJsonFile(path, ctrlShapeInfoDic)

	endTime = time.time()

	logger.info('Save control shapes info at {}, took {} seconds'.format(path, endTime - startTime))

# load ctrl shape info
def loadCtrlShapeInfo(path):
	startTime = time.time()

	ctrlShapeInfoDic = files.readJsonFile(path)

	for ctrl in ctrlShapeInfoDic:
		if cmds.objExists(ctrl):
			addCtrlShape(ctrl, shape = ctrlShapeInfoDic[ctrl],
						 overrideType = ctrlShapeInfoDic[ctrl]['overrideType'])
		else:
			logger.warn('{} does not exist, skipped'.format(ctrl))

	endTime = time.time()
	logger.info('load control shapes info from {}, took {} seconds'.format(path, endTime - startTime))

# append shape info to preset
def appendPreset(curveList):

	shapeInfoDic = files.readJsonFile(path_ctrlShapeDic)

	for c in curveList:
		crvShapeInfo = curves.__getCurveInfo(c)
		shapeInfoDic.update({c:crvShapeInfo})

	files.writeJsonFile(path_ctrlShapeDic, shapeInfoDic)

# sub function
# create ctrl shape
def __addCtrlShapeToTransform(ctrl, shape='cube', color=None, size=1, colorOverride=False):
	
	if isinstance(shape, basestring):
		ctrlShapeDic = files.readJsonFile(path_ctrlShapeDic)
		ctrlShapeInfo = ctrlShapeDic[shape]
	else:
		ctrlShapeInfo = shape

	ctrlShapeInfo = curves.__convertCurveInfo(ctrlShapeInfo)

	# get exists shapes
	shapeExist = cmds.listRelatives(ctrl, s = True)
	if not shapeExist:
		shapeExist = []

	# create curve shape
	ctrl = curves.__createCurve(ctrlShapeInfo, ctrl)

	# rename shape
	NamingShape = naming.Naming(ctrl)
	NamingShape.type = 'ctrlShape'
	shapes = cmds.listRelatives(ctrl, s = True)
	for s in shapes:
		if s not in shapeExist:
			ctrlShape = cmds.rename(s, NamingShape.name)
			break

	# set override
	cmds.setAttr('{}.overrideEnabled'.format(ctrlShape), 1)

	# color
	if 'color' in ctrlShapeInfo and not colorOverride:
		color = ctrlShapeInfo['color']
	elif isinstance(color, basestring):
		ctrlColorDic = files.readJsonFile(path_ctrlColorDic)
		color = ctrlColorDic[color]

	if color:
		cmds.setAttr('{}.overrideColor'.format(ctrlShape), color)

	# size
	transformCtrlShape(ctrlShape, scale = size)

	return ctrlShape, ctrl

def __addCtrlShapeAsCtrl(ctrl, ctrlShape):
	if cmds.objExists(ctrlShape):
		# assign shape
		cmds.parent(ctrlShape, ctrl, shape = True, addObject = True)
	else:
		ctrlShapeDic = files.readJsonFile(path_ctrlShapeDic)
		ctrlShapeInfo = ctrlShapeDic['line']

		ctrlShapeInfo = curves.__convertCurveInfo(ctrlShapeInfo)

		# create curve shape
		nodeTemp = transforms.createTransformNode('TEMP_CTRL')
		ctrlTemp = curves.__createCurve(ctrlShapeInfo, nodeTemp)
		shapeNode = cmds.listRelatives(nodeTemp, s = True)[0]
		cmds.rename(shapeNode, ctrlShape)
		# vis
		attributes.setAttrs('v', 0, node = ctrlShape, force = True)
		# assign shape
		cmds.parent(ctrlShape, ctrl, shape = True, addObject = True)
		cmds.delete(nodeTemp)

	return ctrlShape, ctrl



def __mirrorSingleCtrlShape(ctrlSource, ctrlTarget, mirrorAxis):
	if cmds.objExists(ctrlSource) and cmds.objExists(ctrlTarget):
		ctrlShapeInfo = curves.__getCurveInfo(ctrlSource)
		matrixListSource = cmds.getAttr('{}.worldMatrix[0]'.format(ctrlSource))
		matrixListTarget = cmds.getAttr('{}.worldMatrix[0]'.format(ctrlTarget))
		MMatrixSource = apiUtils.convertListToMMatrix(matrixListSource)
		MMatrixTarget = apiUtils.convertListToMMatrix(matrixListTarget)
		MMatrixMirror = apiUtils.composeMMatrix(scale = mirrorAxis)
		for i, c in enumerate(ctrlShapeInfo['controlVertices']):
			MMatrixPnt = apiUtils.composeMMatrix(translate = c)
			MMatrixMirrorPnt = MMatrixPnt*MMatrixSource*MMatrixMirror*MMatrixTarget.inverse()
			ctrlShapeInfo['controlVertices'][i] = apiUtils.decomposeMMatrix(MMatrixMirrorPnt)[0]
		
		# check if target has ctrl shape
		NamingShapeMirror = naming.Naming(ctrlTarget)
		NamingShapeMirror.type = 'ctrlShape'
		if cmds.objExists(NamingShapeMirror.name):
			color = cmds.getAttr('{}.colorOverride'.format(NamingShapeMirror.name))
			ctrlShapeInfo['color'] = color
			cmds.delete(NamingShapeMirror.name)

		# create shape for mirror ctrl
		addCtrlShape(ctrlTarget, shape=ctrlShapeInfo)

	else:
		if not cmds.objExists(ctrlSource):
			logger.warn('{} does not exist, skipped'.format(ctrlSource))
		if not cmds.objExists(ctrlTarget):
			logger.warn('{} does not exist, skipped'.format(ctrlTarget))

def __getCtrlShapeInfo(ctrlShape):
	if cmds.objectType(ctrlShape) == 'transform':
		ctrlShape = cmds.listRelatives(ctrlShape, s = True)[0]

	ctrlShapeInfo = curves.__getCurveInfo(ctrlShape)

	overrideType = cmds.getAttr('{}.overrideDisplayType'.format(ctrlShape))
	color = cmds.getAttr('{}.overrideColor'.format(ctrlShape))

	ctrlShapeInfo.update({'overrideType': overrideType, 'color': color})

	return ctrlShapeInfo




