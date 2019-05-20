#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import maya packages
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

## import utils
import utils.common.variables as variables
import utils.common.files as files
import utils.common.naming as naming
import utils.common.attributes as attributes
import utils.common.transforms as transforms
import utils.common.nodeUtils as nodeUtils
import utils.common.apiUtils as apiUtils
import utils.common.mathUtils as mathUtils
import utils.modeling.curves as curves

#=================#
#   GLOBAL VARS   #
#=================#
from . import PATH_CONFIG, Logger
SHAPE_CONFIG = files.read_json_file(os.path.join(PATH_CONFIG, 'CONTROL_SHAPE.cfg'))
COLOR_CONFIG = files.read_json_file(os.path.join(PATH_CONFIG, 'CONTROL_COLOR.cfg'))

SIDE_CONFIG = {'left':   'blue',
			   'middle': 'yellow',
			   'right':  'red'}
#=================#
#      CLASS      #
#=================#
class Control(object):
	"""class to get control information"""
	def __init__(self, ctrl):
		super(Control, self).__init__()
		self.__get_control_info(ctrl)

	@property
	def name(self):
		return self.__name

	@property
	def n(self):
		return self.__name

	@property
	def side(self):
		return self.__side

	@property
	def s(self):
		return self.__side

	@property
	def description(self):
		return self.__des

	@property
	def des(self):
		return self.__des

	@property
	def index(self):
		return self.__index

	@property
	def i(self):
		return self.__index

	@property
	def zero(self):
		return self.__zero

	@property
	def drive(self):
		return self.__drive

	@property
	def space(self):
		return self.__space

	@property
	def offsets(self):
		return self.__offsets

	@property
	def output(self):
		return self.__output
	
	@property
	def sub(self):
		return self.__sub

	@property
	def localMatrix(self):
		matrix = cmds.getAttr(self.__localMatrixAttr)
		return matrix

	@property
	def localMatrixAttr(self):
		return self.__localMatrixAttr

	@property
	def worldMatrix(self):
		matrix = cmds.getAttr(self.__worldMatrixAttr)
		return self.__worldMatrixAttr

	@property
	def worldMatrixAttr(self):
		return self.__worldMatrixAttr
	
	@side.setter
	def side(self, key):
		self.__side = key
		self.__update_control_name()

	@s.setter
	def s(self, key):
		self.__side = key
		self.__update_control_name()

	@description.setter
	def description(self, key):
		self.__des = key
		self.__update_control_name()

	@des.setter
	def des(self, key):
		self.__des = key
		self.__update_control_name()

	@index.setter
	def index(self, num):
		self.__index = num
		self.__update_control_name()

	@i.setter
	def i(self, num):
		self.__index = num
		self.__update_control_name()

	@offsets.setter
	def offsets(self, num):
		if isinstance(num, int) and num>0:
			self.__update_offsets(num)
		else:
			Logger.warning('Given number: {} is invalid, must be an integer'.format(num))

	@sub.setter
	def sub(self, key):
		self.__update_sub(key)

	def __get_control_info(self, ctrl):
		'''
		get control's information

		Args:
			ctrl(str): control's name
		'''
		self.__name = ctrl

		CtrlNamer = naming.Namer(ctrl)

		self.__side = CtrlNamer.side
		self.__des = CtrlNamer.description
		self.__index = CtrlNamer.index

		# zero
		CtrlNamer.type = naming.Type.zero
		self.__zero = CtrlNamer.name

		# drive
		CtrlNamer.type = naming.Type.drive
		self.__drive = CtrlNamer.name

		# space
		CtrlNamer.type = naming.Type.space
		self.__space = CtrlNamer.name

		# controlShape
		CtrlNamer.type = naming.Type.controlShape
		self.__ctrlShape = CtrlNamer.name

		# output
		CtrlNamer.type = naming.Type.output
		self.__output = CtrlNamer.name

		# offsets
		CtrlNamer.type = naming.Type.offset
		self.__offsets = cmds.ls(CtrlNamer.name+'_???', type='transform')

		# sub
		CtrlNamer.type = naming.Type.control
		CtrlNamer.description = CtrlNamer.description+'Sub'
		if cmds.objExists(CtrlNamer.name):
			self.__sub = CtrlNamer.name
			CtrlNamer.type = naming.Type.controlShape
			self.__subShape = CtrlNamer.name
		else:
			self.__sub = None
			self.__subShape = None

		self.__localMatrixAttr = self.__name+'.matrixLocal'
		self.__worldMatrixAttr = self.__name+'.matrixWorld'
		self.__multMatrix = cmds.listConnections(self.__localMatrixAttr, 
												 s=True, d=False, p=False)[0]

	def __update_control_name(self):
		CtrlNamer = naming.Name(type=naming.Type.zero, side=self.__side,
								description=self.__des, index=self.__index)
		# zero
		self.__zero = cmds.rename(self.__zero, CtrlNamer.name)

		# drive
		CtrlNamer.type = naming.Type.drive
		self.__drive = cmds.rename(self.__drive, CtrlNamer.name)

		# space
		CtrlNamer.type = naming.Type.space
		self.__space = cmds.rename(self.__space, CtrlNamer.name)

		# offsets
		CtrlNamer.type = naming.Type.offset
		for i, offset in enumerate(self.__offsets):
			CtrlNamer.suffix = i+1
			self.__offsets[i] = cmds.rename(self.__offsets[i], CtrlNamer.name)

		# control
		CtrlNamer.type = naming.Type.control
		CtrlNamer.suffix = None
		CtrlNamer.index = self.__index
		self.__name = cmds.rename(self.__name, CtrlNamer.name)

		# control shape
		CtrlNamer.type = naming.Type.controlShape
		self.__ctrlShape = cmds.rename(self.__ctrlShape, CtrlNamer.name)

		# output
		CtrlNamer.type = naming.Type.output
		self.__output = cmds.rename(self.__output, CtrlNamer.name)

		# sub
		if self.__sub:
			CtrlNamer.type = naming.Type.control
			CtrlNamer.part = CtrlNamer.part + 'Sub'
			self.__sub = cmds.rename(self.__sub, CtrlNamer.name)
			CtrlNamer.type = naming.Type.controlShape
			self.__subShape = cmds.rename(self.__subShape, CtrlNamer.name)

		# mult matrix node
		CtrlNamer.type = naming.Type.multMatrix
		CtrlNamer.part = CtrlNamer.part.replace('Sub', 'LocalMatrix')
		self.__multMatrix = cmds.rename(self.__multMatrix, CtrlNamer.name)

	def __update_offsets(self, num):
		offsetNum = len(self.__offsets)
		childs = cmds.listRelatives(self.__offsets[-1], c=True, type='transform')
		if num < offsetNum:
			# delete extra offsets
			cmds.parent(childs, self.__offsets[num-1])
			cmds.delete(self.__offsets[num])
			self.__offsets = self.__offsets[:num]
		elif num > offsetNum:
			CtrlNamer = naming.Name(self.__offsets[-1])
			parent = self.__offsets[-1]
			for i in range(num-offsetNum):
				CtrlNamer.suffix = CtrlNamer.suffix+1
				offset = transforms.create(CtrlNamer.name, parent=parent,
										   pos=parent)
				self.__offsets.append(offset)
				parent = offset
			# reparent childs
			cmds.parent(childs, self.__offsets[-1])

	def __update_sub(self, key):
		if not key and self.__sub:
			# delete sub
			cmds.delete(self.__sub)
			cmds.deleteAttr(self.__name+'.subControlVis')
			self.__sub = None
			self.__subShape = None
		elif key and not self.__sub:
			# add sub
			CtrlNamer = naming.Name(type=naming.Type.control, side=self.__side,
									description=self.__des+'Sub', index=self.__index)

			# get lock hide attrs from control
			lockHide = []
			for attr in attributes.Attr.all:
				if not attributes.attr_in_channelBox(self.__name, attr):
					lockHide.append(attr)

			self.__sub = transforms.create(CtrlNamer.name, parent=self.__name,
										   pos=self.__name, lockHide=lockHide)

			# connect output
			attributes.connect_attrs(attributes.Attr.all+['rotateOrder'],
									 attributes.Attr.all+['rotateOrder'],
									 driver=self.__sub, driven=self.__output)
			
			# sub vis
			attributes.add_attrs(self.__name, 'subControlVis', attributeType='long',
								 range=[0,1], defaultValue=0, keyable=False,
								 channelBox=True)
			cmds.connect_attr(self.__name+'.subControlVis', self.__sub+'.v', force=True)

			# unlock rotate order
			attributes.unlock_attrs(self.__sub, 'rotateOrder', channelBox=True)

			# shape
			self.match_sub_ctrl_shape()
			CtrlNamer.type = naming.Type.control
			self.__subShape = CtrlNamer.name

	def match_sub_ctrl_shape(self):
		if self.__sub:
			ctrlShapeInfo = curves.get_curve_info(self.__ctrlShape)
			color = cmds.getAttr(self.__ctrlShape+'.overrideColor')
			__add_ctrl_shape(self.__sub, shapeInfo=ctrlShapeInfo, size=0.9, 
							 color=color, colorOverride=True)

#=================#
#    FUNCTION     #
#=================#
def create(description, **kwargs):
	'''
	create control

	hierarchy:
	-zero
	--drive
	---space
	----offset_001
	-----offset_002
	------offset_...
	-------control
	--------sub control
	--------output

	Args:
		description(str): control's name's description

	Kwargs:
		side(str)['middle']: control's side
		index(int)[None]: control's index
		sub(bool)[False]: if control has sub control
		offsets(int)[1]: control's offset groups number
		parent(str)[None]: where to parent the control
		pos(str/list): match control's position to given node/transform value
					   str: match translate and rotate to the given node
					   [str/None, str/None]: match translate/rotate to the given node
					   [[x,y,z], [x,y,z]]: match translate/rotate to given values
		rotateOrder(int)[0]: control's initial rotate order
		shape(str)['cube']: control's shape
		size(float/list)[1]: control shape's size
		color(string/int)[None]: control shape's color, follow side preset if None
		colorSub(string/int)[None]: sub control shape's color, follow control's color if None
		lockHide(list)[]: lock and hide control's attributes

	Returns:
		Control(obj): Control object
	'''

	# get vars
	side = variables.kwargs('side', naming.Side.middle, kwargs, shortName='s')
	index = variables.kwargs('index', None, kwargs, shortName='i')
	sub = variables.kwargs('sub', False, kwargs)
	offsets = variables.kwargs('offsets', 1, kwargs, shortName='ofst')
	parent = variables.kwargs('parent', None, kwargs, shortName='p')
	pos = variables.kwargs('pos', None, kwargs)
	rotateOrder = variables.kwargs('rotateOrder', 0, kwargs, shortName='ro')
	shape = variables.kwargs('shape', 'cube', kwargs)
	size = variables.kwargs('size', 1, kwargs)
	color = variables.kwargs('color', None, kwargs, shortName='col')
	colorSub = variables.kwargs('colorSub', None, kwargs, shortName='colSub')
	lockHide = variables.kwargs('lockHide', attributes.Attr.scaleVis, kwargs, shortName='lh')

	Namer = naming.Namer(type=naming.Type.control, side=side,
						 description=description, index=index)

	# build hierarchy
	transformNodes = []
	for trans in ['zero', 'drive', 'space', 'control',
				  'output']:
		Namer.type = getattr(naming.Type, trans)
		transform = transforms.create(Namer.name, parent=parent)
		transformNodes.append(transform)
		parent=transform
	
	ctrl = transformNodes[3]
	ctrlList = [ctrl]
	# offset
	Namer.type=naming.Type.offset
	parent=transformNodes[2]
	for i in range(offsets):
		Namer.suffix=i+1
		offset = transforms.create(Namer.name, parent=parent)
		parent = offset

	# parent control to parent
	cmds.parent(ctrl, parent)


	# sub control
	if sub:
		Namer.type = naming.Type.control
		Namer.description = Namer.description+'Sub'
		Namer.index = index
		Namer.suffix = None

		sub = transforms.create(sub, parent=ctrl)
		ctrlList.append(sub)

		# connect output
		attributes.connect_attrs(attributes.Attr.all+['rotateOrder'],
								 attributes.Attr.all+['rotateOrder'],
								 driver=sub, driven=transformNodes[4])
		
		# sub vis
		attributes.add_attrs(ctrl, 'subControlVis', attributeType='long',
							 range=[0,1], defaultValue=0, keyable=False,
							 channelBox=True)
		cmds.connect_attr(ctrl+'.subControlVis', sub+'.v', force=True)

	# lock hide
	attributes.lock_hide_attrs(ctrlList, lockHide)

	# unlock rotate order
	attributes.unlock_attrs(ctrlList, 'rotateOrder', channelBox=True)

	# add output attrs
	attributes.add_attrs(ctrl, ['matrixLocal', 'matrixWorld'], attributeType='matrix')

	cmds.connectAttr(transformNodes[-1]+'.worldMatrix[0]', ctrl+'.matrixWorld')
	nodeUtils.mult_matrix([transformNodes[-1]+'.worldMatrix[0]', 
						   transformNodes[0]+'.worldInverseMatrix[0]'], 
						   attrs=ctrl+'.matrixLocal', side=side, 
						   description=description+'LocalMatrix', index=index)

	# set pos
	# match pos
	if pos:
		if isinstance(pos, basestring):
			cmds.matchTransform(zero, pos, pos=True, rot=True)
		else:
			if isinstance(pos[0], basestring):
				cmds.matchTransform(zero, pos[0], pos=True, rot=False)
			else:
				cmds.xform(zero, t=pos[0], ws=True)
			if isinstance(pos[1], basestring):
				cmds.matchTransform(zero, pos[1], pos=False, rot=True)
			else:
				cmds.xform(zero, rot=pos[1], ws=True)

	# add shape
	for c, col, scale in zip(ctrlList, [color, colorSub], [size, size*0.9]):
		__add_ctrl_shape(c, shape=shape, size=scale, color=col)

	return Control(ctrl)

def transform_ctrl_shape(ctrlShapes, **kwargs):
	'''
	offset controls shape nodes

	Args:
		ctrlShapes(str/list): controls shape nodes
	Kwargs:
		translate(float/list): translate
		rotate(float/list): rotate
		scale(float/list): scale
		pivot(str)['transform']: transform/shape, define the offset pivot
	'''
	# vars
	translate = variables.kwargs('translate', [0,0,0], kwargs, shortName='t')
	rotate = variables.kwargs('rotate', [0,0,0], kwargs, shortName='r')
	scale = variables.kwargs('scale', [1,1,1], kwargs, shortName='s')
	pivot = variables.kwargs('pivot', 'transform', kwargs)

	if isinstance(ctrlShapes, basestring):
		ctrlShapes = [ctrlShapes]
	if not isinstance(scale, list):
		scale = [scale, scale, scale]

	for shape in ctrlShapes:
		if cmds.objExists(shape):
			ctrlShapeInfo = curves.get_curve_info(shape)
			cvPnts = ctrlShapeInfo['controlVertices']

			matrixOffset = apiUtils.compose_matrix(translate=translate,
												   rotate=rotate,
												   scale=scale)
			# get pivot matrix
			if pivot == 'shape':
				maxPos, minPos, centerPos = transforms.bounding_box_info(cvPnts)
				matrixPivot = apiUtils.compose_matrix(translate=centerPos)
			else:
				matrixPivot = apiUtils.compose_matrix()
			inversePivot = mathUtils.inverse_matrix(matrixPivot)
			# move each point
			for i, pnt in enumerate(cvPnts):
				matrixPnt = apiUtils.compose_matrix(translate=pnt)

				# mult matrix
				matrixPos = mathUtils.mult_matrix([matrixPnt, inversePivot, 
												   matrixOffset, matrixPivot])
				
				# get pos
				pos = apiUtils.decompose_matrix(matrixPos)[0]

				cvPnts[i] = pos

			# set pos
			curves.set_curve_points(shape, cvPnts)

		else:
			Logger.warning('{} does not exist'.format(shape))

#=================#
#  SUB FUNCTION   #
#=================#
def __add_ctrl_shape(ctrl, **kwargs):
	shape = kwargs.get('shape', 'cube')
	size = kwargs.get('size', 1)
	color = kwargs.get('color', None)
	colorOverride = kwargs.get('colorOverride', False)
	transform = kwargs.get('transform', None)
	shapeInfo = kwargs.get('shapeInfo', None)

	if not shapeInfo:
		shapeInfo = SHAPE_CONFIG[shape]

	if transform and cmds.objExists(ctrl):
		for trans in transform:
			s = cmds.listRelatives(trans, s=True)
			if not ctrl in s:
				cmds.parent(ctrl, trans, shape=True, addObject=True)
		return

	crvTrans, crvShape = curves.create_curve('TEMP_CRV', shapeInfo['controlVertices'], 
							shapeInfo['knots'], degree=shapeInfo['degree'], form=shapeInfo['form'])

	if not transform:
		Namer = naming.Namer(ctrl)
		Namer.type = naming.Type.controlShape
		if cmds.objExists(Namer.name):
			cmds.delete(Namer.name)
		crvShape = cmds.rename(crvShape, Namer.name)
		transform = [ctrl]

		# set color
		if not colorOverride or not color:
			sideCol = SIDE_CONFIG[Namer.side]
			color = COLOR_CONFIG[sideCol]
		else:
			if isinstance(color, basestring):
				color = COLOR_CONFIG[color]
		cmds.setAttr(crvShape+'.overrideEnabled', 1)
		cmds.setAttr(crvShape+'.overrideColor', color)
		
		# size
		transform_ctrl_shape(crvShape, scale=size)

	else:
		crvShape = cmds.rename(crvShape, ctrl)
		attributes.set_attrs(crvShape+'.v', 0, force=True)

	# assign shape
	for trans in transform:
		cmds.parent(crvShape, trans, shape=True, addObject=True)
		cmds.delete('TEMP_CRV')
	return crvShape
		

