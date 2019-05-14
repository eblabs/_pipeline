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
	"""docstring for Control"""
	def __init__(self, ctrl):
		super(Control, self).__init__()
		self.__get_control_info(ctrl)

	def __get_control_into(ctrl):
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


#=================#
#    FUNCTION     #
#=================#
def create(description, **kwargs):
	'''
	create control

	hierarchy:
	-zero
	--driver
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
	for trans in ['zero', 'driver', 'space', 'control',
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
	print lockHide
	attributes.lock_hide_attrs(ctrlList, lockHide)

	# unlock rotate order
	attributes.unlock_attrs(ctrlList, 'rotateOrder', channelBox=True)

	# add output attrs
	attributes.add_attrs(ctrl, ['matrixLocal', 'matrixWorld'], attributeType='matrix')

	cmds.connectAttr(transformNodes[-1]+'.worldMatrix[0]', ctrl+'.matrixWorld')
	nodeUtils.mult_matrix([transformNodes[-1]+'.worldMatrix[0]', 
						   transformNodes[0]+'.worldInverseMatrix[0]'], 
						   attrs=ctrl+'.matrixWorld', side=side, 
						   description=description+'WorldMatrix', index=index)

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
			Logger.warn('{} does not exist'.format(shape))

#=================#
#  SUB FUNCTION   #
#=================#
def __add_ctrl_shape(ctrl, **kwargs):
	shape = kwargs.get('shape', 'cube')
	size = kwargs.get('size', 1)
	color = kwargs.get('color', None)
	colorOverride = kwargs.get('colorOverride', False)
	transform = kwargs.get('transform', None)

	shapeInfo = SHAPE_CONFIG[shape]

	if transform and cmds.objExists(ctrl):
		return
	if cmds.objExists(ctrl) and cmds.listRelatives(ctrl, s=True):
		return

	crvTrans, crvShape = curves.create_curve('TEMP_CRV', shapeInfo['controlVertices'], 
							shapeInfo['knots'], degree=shapeInfo['degree'], form=shapeInfo['form'])

	if not transform:
		print ctrl
		Namer = naming.Namer(ctrl)
		Namer.type = naming.Type.controlShape
		crvShape = cmds.rename(crvShape, Namer.name)
		transform = [ctrl]

		# set color
		if not colorOverride or not color:
			sideCol = SIDE_CONFIG[Namer.side]
			color = COLOR_CONFIG[sideCol]
		else:
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
		

