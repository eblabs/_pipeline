#=================#
# IMPORT PACKAGES #
#=================#

## import maya packages
import maya.cmds as cmds

## import ast
import ast

## import utils
import naming
import attributes
import variables
#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#

#=================#
#    FUNCTION     #
#=================#
def node(**kwargs):
	'''
	Create maya node

	Kwargs:
		name(str): node's name, will create node base on type
		type(str): node's type (if name given, will follow name)
		side(str): node's side (if name given, will follow name)
		description(str): node's description (if name given, will follow name)
		index(int): node's index (if name given, will follow name)
		suffix(int): node's suffix (if name given, will follow name)

		useExist(bool)[False]: if node already exists, using exist node
							   Will Error out if node exists and set thie to False
		autoSuffix(bool)[False]: Automatically suffix node from 1

		setAttrs(dict): set attrs when creating the node

	Returns:
		name(str): node's name
	'''
	# get vars
	_name = variables.kwargs('name', None, kwargs, shortName='n')
	_type = variables.kwargs('type', None, kwargs, shortName='t')
	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_suffix = variables.kwargs('suffix', None, kwargs, shortName='sfx')

	_useExist = variables.kwargs('useExist', False, kwargs)
	_autoSuffix = variables.kwargs('autoSuffix', False, kwargs)

	_setAttrs = variables.kwargs('setAttrs', {}, kwargs)

	if _name:
		Namer = naming.Namer(_name)
	else:
		Namer = naming.Namer(type=_type, side=_side,
							 description=_des, index=_index,
							 suffix=_suffix)

	# check if node exist
	if cmds.objExists(Namer.name):
		if not _useExist:
			Logger.error('{} node: {} already exists in the scene').format(Namer.type, Namer.name)
		else:
			node = Namer.name
	else:
		# check if auto suffix
		if _autoSuffix:
			nodeExisting = cmds.ls(Namer.name+'_???')
			Namer.suffix = len(nodeExisting)+1

		node = cmds.createNode(Namer.type, name=Namer.name)
	
	for attr, val in _setAttrs.iteritems():
		cmds.setAttr('{}.{}'.format(node, attr), val)

	return node

def equation(expression, **kwargs):
	'''
	Create node connection network base on the expression
	only works for 1D input

	Symbols:
		+:  add
		-:  sub
		*:  mult
		/:  divide
	   **:  power
		~:  reverse

	Example:
		equation('(pCube1.tx + pCube2.tx)/2')

	Args:
		expression(str): given equation to make the connection

	Kwargs:
		side(str): nodes' side
		description(str): nodes' description
		index(int): nodes' index
		attrs(str/list): connect the equation to given attrs
		force(bool)[True]: force the connection

	Return:
		outputAttr(str): output attribute from the equation node network
	'''

	# get vars
	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_attrs = variables.kwargs('attrs', [], kwargs)
	_force = variables.kwargs('force', True, kwargs, shortName='f')

	# node equation
	outputAttr = NodeEquation.equation(expression, side=_side,
									   description=_des, index=_index)

	# connect attrs
	if _attrs:
		attributes.connect_attrs(outputAttr, _attrs, force=_force)

	return outputAttr

def plus_minus_average(inputAttrs, **kwargs):
	'''
	connect attrs with plusMinusArverage node
	
	Args:
		inputAttrs(list): given attrs, will connect in order
					      can be 1D/2D/3D inputs
					      2D/3D attrs must be in list
					      ('node.t' will not work, 
					      	have to be ['node.tx', 'node.ty', 'node.tz'])
	Kwargs:
		side(str): node's side
		description(str): node's description
		index(int): node's index
		suffix(int): node's suffix
		operation(int)[1]: plusMinusAvarge node's operation
						1. add
						2. sub
						3. average
		attrs(str/list): connect the node to given attrs
		force(bool)[True]: force the connection
 	Returns:
 		outputAttr(list): output attribute from the node
	'''
	# get vars
	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_suffix = variables.kwargs('suffix', None, kwargs, shortName='sfx')
	_op = variables.kwargs('operation', 1, kwargs, shortName='op')
	_attrs = variables.kwargs('attrs', [], kwargs)
	_force = variables.kwargs('force', True, kwargs, shortName='f')

	# create node
	pmav = node(type=naming.Type.plusMinusAvarge, side=_side,
				description=_des, index=_index, suffix=_suffix,
				setAttrs={'operation': _op})

	# check input attr type(1D/2D/3D)
	if not isinstance(inputAttrs[0], list) and not isinstance(inputAttrs[0], tuple):
		# 1D
		for i, inputAttr in enumerate(inputAttrs):
			if isinstance(inputAttr, basestring):
				cmds.connectAttr(inputAttr, '{}.input1D[{}]'.format(pmav, i)) 
			else:
				cmds.setAttr('{}.input1D[{}]'.format(pmav, i), inputAttr)
		outputAttr = [pmav+'.output1D']
	else:
		# 2D/3D
		num = len(inputAttrs[0])
		for i, inputAttr in enumerate(inputAttrs):
			for inputAttrInfo in zip(inputAttr, ['x', 'y', 'z']):
				if isinstance(inputAttrInfo[0], basestring):
					cmds.connectAttr(inputAttrInfo[0],
									 '{}.input{}D[{}].input{}D{}'.format(pmav, num, i,
									 							num, inputAttrInfo[1]))
				else:
					cmds.setAttr('{}.input{}D[{}].input{}D{}'.format(pmav, num, i,
											num, inputAttrInfo[1]), inputAttrInfo[0])
		if num==2:
			outputAttr = [pmav+'.output2Dx', pmav+'.output2Dy']
		else:
			outputAttr = [pmav+'.output3Dx', pmav+'.output3Dy', pmav+'.output3Dz']

	# connect attr
	if _attrs:
		if isinstance(_attrs, basestring):
				_attrs = [_attrs]
		elif isinstance(_attrs[0], basestring):
			_attrs = [_attrs]
		for attr in _attrs:
			for attrInfo in zip(outputAttr, attr):
				attributes.connect_attrs(attrInfo[0], attrInfo[1], force=_force)

	# return output attr
	return outputAttr

def multiply_divide(inputAttr1, inputAttr2, **kwargs):
	'''
	connect attrs with multiplyDivide node

	Args:
		inputAttr1(str/list): input attr 1
						      maximum 3 attrs (['tx', 'ty', 'tz'])
		inputAttr2(str/list): input attr 2
						      maximum 3 attrs (['tx', 'ty', 'tz'])
	Kwargs:
		side(str): node's side
		description(str): node's description
		index(int): node's index
		suffix(int): node's suffix
		operation(int)[1]: multiplyDivide node's operation
						1. mult
						2. divide
						3. power
		attrs(str/list): connect the node to given attrs
		force(bool)[True]: force the connection
 	Returns:
 		outputAttr(str/list): output attribute from the node
	'''
	# get vars

	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_suffix = variables.kwargs('suffix', None, kwargs, shortName='sfx')
	_op = variables.kwargs('operation', 1, kwargs, shortName='op')
	_attrs = variables.kwargs('attrs', [], kwargs)
	_force = variables.kwargs('force', True, kwargs, shortName='f')

	outputAttr = _create_node_multi_attrs([],[inputAttr1, inputAttr2],
										  [], ['input1', 'input2'],
										  ['X', 'Y', 'Z'], 'output',
										  type=naming.Type.multiplyDivide,
										  side=_side, description=_des, 
										  setAttrs={'operation': _op},
										  attrs=_attrs, force=_force)
	# return output attr
	return outputAttr

def condition(firstTerm, secondTerm, ifTrue, ifFalse, **kwargs):
	'''
	connect attrs with condition node

	Args:
		firstTerm(str/float): first term
		secondTerm(str/float): secondTerm
		ifTrue(str/float/list): color if True
		ifFalse(str/float/list): color if False

	Kwargs:
		side(str): node's side
		description(str): node's description
		index(int): node's index
		suffix(int): node's suffix
		operation(int/str)[0]: condition node's operation
								0['=='] equal
								1['!='] not equal
								2['>']  greater than
								3['>='] greater or equal
								4['<']  less than
								5['<='] less or equal
		attrs(str/list): connect the node to given attrs
		force(bool)[True]: force the connection
 	Returns:
 		outputAttr(str/list): output attribute from the node
	'''

	# get vars
	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_suffix = variables.kwargs('suffix', None, kwargs, shortName='sfx')
	_op = variables.kwargs('operation', 0, kwargs, shortName='op')
	_attrs = variables.kwargs('attrs', [], kwargs)
	_force = variables.kwargs('force', True, kwargs, shortName='f')

	# get operation
	if isinstance(_op, basestring):
		_op_list = ['==', '!=', '>', '>=', '<', '<=']
		_op = _op_list.index(_op)

	outputAttr = _create_node_multi_attrs([firstTerm, secondTerm],
										  [ifTrue, ifFalse],
										  ['firstTerm', 'secondTerm'], 
										  ['colorIfTrue', 'colorIfFalse'],
										  ['R', 'G', 'B'], 'outColor',
										  type=naming.Type.condition,
										  side=_side, description=_des, 
										  setAttrs={'operation': _op},
										  attrs=_attrs, force=_force)

	# return output attr
	return outputAttr

def clamp(inputAttr, maxAttr, minAttr, **kwargs):
	'''
	connect attrs with clamp node

	Args:
		inputAttr(str/float/list): clamp's input
		maxAttr(str/float/list): clamp's max
		minAttr(str/float/list): clamp's min

	Kwargs:
		side(str): node's side
		description(str): node's description
		index(int): node's index
		suffix(int): node's suffix
		attrs(str/list): connect the node to given attrs
		force(bool)[True]: force the connection
 	Returns:
 		outputAttr(list): output attribute from the node
	'''

	# get vars
	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_suffix = variables.kwargs('suffix', None, kwargs, shortName='sfx')
	_attrs = variables.kwargs('attrs', [], kwargs)
	_force = variables.kwargs('force', True, kwargs, shortName='f')

	outputAttr = _create_node_multi_attrs([],[inputAttr, maxAttr, minAttr],
										  [], ['input', 'max', 'min'],
										  ['R', 'G', 'B'], 'output',
										  type=naming.Type.clamp,
										  side=_side, description=_des, 
										  attrs=_attrs, force=_force)

	# return output attr
	return outputAttr

def blend(blender, inputAttr1, inputAttr2, **kwargs):
	'''
	connect attrs with blendColor node

	Args:
		blend(str/float): blendColor's blender
		inputAttr1(str/float/list): blendColor's color1
		inputAttr2(str/float/list): blendColor's color2

	Kwargs:
		side(str): node's side
		description(str): node's description
		index(int): node's index
		suffix(int): node's suffix
		attrs(str/list): connect the node to given attrs
		force(bool)[True]: force the connection
 	Returns:
 		outputAttr(list): output attribute from the node
	'''

	# get vars
	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_suffix = variables.kwargs('suffix', None, kwargs, shortName='sfx')
	_attrs = variables.kwargs('attrs', [], kwargs)
	_force = variables.kwargs('force', True, kwargs, shortName='f')

	outputAttr = _create_node_multi_attrs([blender],[inputAttr1, inputAttr2],
										  ['blender'], ['color1', 'color2'],
										  ['R', 'G', 'B'], 'output',
										  type=naming.Type.blendColor,
										  side=_side, description=_des, 
										  attrs=_attrs, force=_force)

	# return output attr
	return outputAttr

def remap(inputValue, inputRange, outputRange, **kwargs):
	'''
	connect attrs with remapValue node

	Args:
		inputValue(str/float): remapValue's input
		inputRange(list): remapValue's input min/max
		outputRange(list): remapValue's output min/max

	Kwargs:
		side(str): node's side
		description(str): node's description
		index(int): node's index
		suffix(int): node's suffix
		setAttrs(dict): set node's attrs
		attrs(str/list): connect the node to given attrs
		force(bool)[True]: force the connection
 	Returns:
 		outputAttr(str): output attribute from the node
	'''

	# get vars
	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_suffix = variables.kwargs('suffix', None, kwargs, shortName='sfx')
	_setAttrs = variables.kwargs('setAttrs', {}, kwargs)
	_attrs = variables.kwargs('attrs', [], kwargs)
	_force = variables.kwargs('force', True, kwargs, shortName='f')

	# create node
	remap = node(type=naming.Type.remapValue, side=_side, description=_des,
				 index=_index, suffix=_suffix, setAttrs=_setAttrs)

	# input connection
	if isinstance(inputValue, basestring):
		cmds.connectAttr(inputValue, remap+'.inputValue')

	for rangeValue in zip([inputRange, outputRange], ['input', 'output']):
		for val in zip(rangeValue[0], ['min', 'max']):
			if isinstance(val[0], basestring):
				cmds.connectAttr(val[0], '{}.{}{}'.format(remap, rangeValue[1], val[1].title()))
			else:
				cmds.setAttr('{}.{}{}'.format(remap, rangeValue[1], val[1].title()), val[0])

	outputAttr = remap+'.outValue'

	if _attrs:
		attributes.connect_attrs(outputAttr, _attrs, force=_force)

	return outputAttr

def add_matrix(inputMatrix, **kwargs):
	'''
	connect attrs with add matrix node

	Args:
		inputMatrix(list): list of input matrix
						   each can be attribute/list

	Kwargs:
		side(str): node's side
		description(str): node's description
		index(int): node's index
		suffix(int): node's suffix
		attrs(str/list): connect the node to given attrs
		force(bool)[True]: force the connection
 	Returns:
 		outputAttr: output attribute from the node
	'''

	# get vars
	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_suffix = variables.kwargs('suffix', None, kwargs, shortName='sfx')
	_attrs = variables.kwargs('attrs', [], kwargs)
	_force = variables.kwargs('force', True, kwargs, shortName='f')

	# create node
	addMatrix = node(type=naming.Type.addMatrix, side=_side,
					 description=_des, index=_index, suffix=_suffix)

	# input attrs
	for i, matrix in enumerate(inputMatrix):
		if isinstance(matrix, basestring):
			cmds.connectAttr(matrix, '{}.matrixIn[{}]'.format(addMatrix, i))
		else:
			cmds.setAttr('{}.matrixIn[{}]'.format(addMatrix, i), matrix, type='matrix')

	outputAttr = addMatrix+'.matrixSum'

	if _attrs:
		attributes.connect_attrs(outputAttr, _attrs, force=_force)

	# return output attr
	return outputAttr

def mult_matrix(inputMatrix, **kwargs):
	'''
	connect attrs with mult matrix node

	Args:
		inputMatrix(list): list of input matrix
						   each can be attribute/list

	Kwargs:
		side(str): node's side
		description(str): node's description
		index(int): node's index
		suffix(int): node's suffix
		attrs(str/list): connect the node to given attrs
		force(bool)[True]: force the connection
 	Returns:
 		outputAttr: output attribute from the node
	'''

	# get vars
	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_suffix = variables.kwargs('suffix', None, kwargs, shortName='sfx')
	_attrs = variables.kwargs('attrs', [], kwargs)
	_force = variables.kwargs('force', True, kwargs, shortName='f')

	# create node
	multMatrix = node(type=naming.Type.multMatrix, side=_side,
					 description=_des, index=_index, suffix=_suffix)

	# input attrs
	for i, matrix in enumerate(inputMatrix):
		if isinstance(matrix, basestring):
			cmds.connectAttr(matrix, '{}.matrixIn[{}]'.format(multMatrix, i))
		else:
			cmds.setAttr('{}.matrixIn[{}]'.format(multMatrix, i), matrix, type='matrix')

	outputAttr = multMatrix+'.matrixSum'

	if _attrs:
		attributes.connect_attrs(outputAttr, _attrs, force=_force)

	# return output attr
	return outputAttr

def inverse_matrix(inputMatrix, **kwargs):
	'''
	connect attrs with inverse matrix node

	Args:
		inputMatrix(str): input matrix attr

	Kwargs:
		side(str): node's side
		description(str): node's description
		index(int): node's index
		suffix(int): node's suffix
		attrs(str/list): connect the node to given attrs
		force(bool)[True]: force the connection
 	Returns:
 		outputAttr: output attribute from the node
	'''

	# get vars
	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_suffix = variables.kwargs('suffix', None, kwargs, shortName='sfx')
	_attrs = variables.kwargs('attrs', [], kwargs)
	_force = variables.kwargs('force', True, kwargs, shortName='f')

	# create node
	invMatrix = node(type=naming.Type.inverseMatrix, side=_side,
					 description=_des, index=_index, suffix=_suffix)

	# input attrs
	cmds.connectAttr(inputMatrix, invMatrix+'.inputMatrix')

	outputAttr = invMatrix+'.outputMatrix'

	if _attrs:
		attributes.connect_attrs(outputAttr, _attrs, force=_force)

	# return output attr
	return outputAttr

def compose_matrix(translate, rotate, scale=[1,1,1], **kwargs):
	'''
	connect attrs with compose matrix node

	Args:
		translate(list): input translate
						 each can be attribute/float
		rotate(list): input rotate
					  each can be attribute/float

	Kwargs:
		scale(list)[1,1,1]: input scale
							each can be attribute/float
		rotateOrder(int)[0]: input rotate order
		side(str): node's side
		description(str): node's description
		index(int): node's index
		suffix(int): node's suffix
		attrs(str/list): connect the node to given attrs
		force(bool)[True]: force the connection
 	Returns:
 		outputAttr: output attribute from the node
	'''
	# get vars
	rotateOrder = variables.kwargs('rotateOrder', 0, kwargs, shortName='ro')
	_side = variables.kwargs('side', None, kwargs, shortName='s')
	_des = variables.kwargs('description', None, kwargs, shortName='des')
	_index = variables.kwargs('index', None, kwargs, shortName='i')
	_suffix = variables.kwargs('suffix', None, kwargs, shortName='sfx')
	_attrs = variables.kwargs('attrs', [], kwargs)
	_force = variables.kwargs('force', True, kwargs, shortName='f')

	# node
	compose = node(type=naming.Type.composeMatrix, side=_side,
				   description=_des, index=_index, suffix=_suffix)
	for inputAttrInfo in zip([translate, rotate, scale], ['translate', 'rotate', 'scale']):
		for inputVal in zip(inputAttrInfo[0], ['X','Y','Z']):
			if isinstance(inputVal[0], basestring):
				cmds.connectAttr(inputVal[0], 
								 '{}.input{}{}'.format(compose, inputAttrInfo[1].title(), inputVal[1]))
			else:
				cmds.setAttr('{}.input{}{}'.format(compose, inputAttrInfo[1].title(), inputVal[1]),
							 inputVal[0])
	if isinstance(rotateOrder, basestring):
		cmds.connectAttr(rotateOrder, compose+'.inputRotateOrder')
	else:
		cmds.setAttr(compose+'.inputRotateOrder', rotateOrder)

	outputAttr = compose+'.outputMatrix'

	if _attrs:
		attributes.connect_attrs(outputAttr, _attrs, force=_force)

	#return outputAttr
	return outputAttr

def twist_extract(inputMatrix, **kwargs):
	'''
	extract twist value from input matrix

	Args:
		inputMatrix(str)
	Kwargs:
		attrs(str/list): connect twist value to attrs
		force(bool)[True]: force the connection
	Returns:
		outputAttr(str): output attr
	'''
	attrs = variables.kwargs('attrs', [], kwargs)
	force = variables.kwargs('force', True, kwargs, shortName='f')

	driver = inputMatrix.split('.')[0]

	Namer = naming.Namer(driver)

	Namer.type = naming.Type.decomposeMatrix
	Namer.description = Namer.description+'TwsitExtract'

	decomposeMatrix = node(name=Namer.name)
	cmds.connectAttr(inputMatrix, decomposeMatrix+'.inputMatrix')

	Namer.type = naming.Type.quatToEuler
	quatToEuler = node(name=Namer.name)

	cmds.connectAttr(decomposeMatrix+'.outputQuatX', 
					 quatToEuler+'.inputQuatX')
	cmds.connectAttr(decomposeMatrix+'.outputQuatW', 
					 quatToEuler+'.inputQuatW')

	if attrs:
		attributes.connect_attrs(quatToEuler+'.outputRotateX', 
								 attrs, force=force)
	
	return quatToEuler+'.outputRotateX'

#=================#
#  SUB FUNCTION   #
#=================#
def _create_node_multi_attrs(inputAttrSingle, inputAttrMult, nodeAttrSingle, 
			 				 nodeAttrMult, nodeSubAttrs, outputAttr, **kwargs):
	'''
	create node with multi attrs (like RGB/XYZ), connect with attrs

	'''
	# get vars
	_type = kwargs.get('type', None)
	_side = kwargs.get('side', None)
	_des = kwargs.get('description', None)
	_index = kwargs.get('index', None)
	_suffix = kwargs.get('suffix', None)
	_setAttrs = kwargs.get('setAttrs', {})
	_attrs = kwargs.get('attrs', [])
	_force = kwargs.get('force', True)

	# create node
	_node = node(type=_type, side=_side, description=_des, 
				 index=_index, suffix=_suffix, setAttrs=_setAttrs)

	# connect input
	for inputAttrInfo in zip(inputAttrSingle, nodeAttrSingle):
		if isinstance(inputAttrInfo[0], basestring):
			cmds.connectAttr(inputAttrInfo[0], '{}.{}'.format(_node, inputAttrInfo[1]))
		else:
			cmds.setAttr('{}.{}'.format(_node, inputAttrInfo[1]), inputAttrInfo[0])

	inputAttrList = []
	inputAttrNum = []
	for inputVal in inputAttrMult:
		if not isinstance(inputVal, list) and not isinstance(inputVal, tuple):
			inputVal = [inputVal]
		inputAttrList.append(inputVal)
		inputAttrNum.append(len(inputVal))
	
	for inputAttrInfo in zip(inputAttrList, nodeAttrMult):
		for inputVal in zip(inputAttrInfo[0], nodeSubAttrs):
			if isinstance(inputVal[0], basestring):
				cmds.connectAttr(inputVal[0], 
								 '{}.{}{}'.format(_node, inputAttrInfo[1], inputVal[1]))
			else:
				cmds.setAttr('{}.{}{}'.format(_node, inputAttrInfo[1], inputVal[1]),
							 inputVal[0])

	outputNum = min(inputAttrNum)

	outputAttrList=[]
	for attrInfo in zip(range(outputNum), nodeSubAttrs):
		outputAttrList.append('{}.{}{}'.format(_node, outputAttr, attrInfo[1]))

	# connect output
	if _attrs:
		if isinstance(_attrs, basestring):
			_attrs = [_attrs]
		elif isinstance(_attrs[0], basestring):
			_attrs = [_attrs]
		for attr in _attrs:
			for attrInfo in zip(outputAttr, attr):
				attributes.connect_attrs(attrInfo[0], attrInfo[1], force=_force)

	# return output attr
	return outputAttrList
# operation functions
def _add(left, right, **kwargs):
	'''
	conenct left and right attr with addDoubleLinear node

	'''
	side = kwargs.get('side', None)
	des = kwargs.get('description', None)
	index = kwargs.get('index', None)

	strBool_l = isinstance(left, basestring)
	strBool_r = isinstance(right, basestring)

	if strBool_l or strBool_r:
		addNode = node(type=naming.Type.addDoubleLinear,
					   side=side, description=des, index=index,
					   autoSuffix=True)
		for attrInfo in zip([left, right], 
							[strBool_l, strBool_r],
							['input1', 'input2']):
			if attrInfo[1]:
				cmds.connectAttr(attrInfo[0], '{}.{}'.format(addNode, attrInfo[2]))
			else:
				cmds.setAttr('{}.{}'.format(addNode, attrInfo[2]), attrInfo[0])
		
		return addNode+'.output'
	else:
		return left+right

def _mult(left, right, **kwargs):
	'''
	conenct left and right attr with multDoubleLinear node

	'''
	side = kwargs.get('side', None)
	des = kwargs.get('description', None)
	index = kwargs.get('index', None)

	strBool_l = isinstance(left, basestring)
	strBool_r = isinstance(right, basestring)

	if strBool_l or strBool_r:
		multNode = node(type=naming.Type.multDoubleLinear,
					   side=side, description=des, index=index,
					   autoSuffix=True)
		for attrInfo in zip([left, right], 
							[strBool_l, strBool_r],
							['input1', 'input2']):
			if attrInfo[1]:
				cmds.connectAttr(attrInfo[0], '{}.{}'.format(multNode, attrInfo[2]))
			else:
				cmds.setAttr('{}.{}'.format(multNode, attrInfo[2]), attrInfo[0])
		
		return multNode+'.output'
	else:
		return left+right

def _sub(left, right, **kwargs):
	'''
	conenct left and right attr doing left-right equation node

	'''
	side = kwargs.get('side', None)
	des = kwargs.get('description', None)
	index = kwargs.get('index', None)

	strBool_l = isinstance(left, basestring)
	strBool_r = isinstance(right, basestring)

	if strBool_l or strBool_r:
		addNode = node(type=naming.Type.addDoubleLinear,
					   side=side, description=des, index=index,
					   autoSuffix=True)
		if strBool_r:
			multNode = node(type=naming.Type.multDoubleLinear,
					   side=side, des=description, index=index,
					   autoSuffix=True, setAttrs={'input2':-1})
			cmds.connectAttr(right, multNode+'.input1')
			cmds.connectAttr(multNode+'.output', addNode+'.input2')
		else:
			cmds.setAttr(addNode+'.input2', right)
		if strBool_l:
			cmds.connectAttr(left, addNode+'.input1')
		else:
			cmds.setAttr(addNode+'.input1', left)

		return addNode+'.output'
	else:
		return left-right

def _divide(left, right, **kwargs):
	'''
	conenct left and right attr with multiplyDivide node
	set operation to divide

	'''
	side = kwargs.get('side', None)
	des = kwargs.get('description', None)
	index = kwargs.get('index', None)

	strBool_l = isinstance(left, basestring)
	strBool_r = isinstance(right, basestring)

	if strBool_l or strBool_r:
		divNode = node(type=naming.Type.multiplyDivide,
						side=side, description=des, index=index,
						autoSuffix=True, setAttrs={'operation':2})
		for attrInfo in zip([left, right], 
							[strBool_l, strBool_r],
							['input1X', 'input2X']):
			if attrInfo[1]:
				cmds.connectAttr(attrInfo[0], '{}.{}'.format(divNode, attrInfo[2]))
			else:
				cmds.setAttr('{}.{}'.format(divNode, attrInfo[2]), attrInfo[0])
		
		return divNode+'.outputX'
	else:
		return left/float(right)

def _pow(left, right, **kwargs):
	'''
	conenct left and right attr with multiplyDivide node
	set operation to power

	'''
	side = kwargs.get('side', None)
	des = kwargs.get('description', None)
	index = kwargs.get('index', None)

	strBool_l = isinstance(left, basestring)
	strBool_r = isinstance(right, basestring)

	if strBool_l or strBool_r:
		powNode = node(type=naming.Type.multiplyDivide,
						side=side, description=des, index=index,
						autoSuffix=True, setAttrs={'operation':3})
		for attrInfo in zip([left, right], 
							[strBool_l, strBool_r],
							['input1X', 'input2X']):
			if attrInfo[1]:
				cmds.connectAttr(attrInfo[0], '{}.{}'.format(powNode, attrInfo[2]))
			else:
				cmds.setAttr('{}.{}'.format(powNode, attrInfo[2]), attrInfo[0])
		
		return powNode+'.outputX'
	else:
		return left**right

def _reverse(operand, **kwargs):
	'''
	conenct operand attr with reverse node

	'''
	side = kwargs.get('side', None)
	des = kwargs.get('description', None)
	index = kwargs.get('index', None)

	rvsNode = node(type=naming.Type.reverse,
				   side=side, description=des, index=index,
				   autoSuffix=True)        
	cmds.connectAttr(operand, rvsNode+'.inputX')

	return rvsNode+'.outputX'

def _uSub(operand, **kwargs):
	'''
	conenct operand attr with multDoubleLinear node
	set input2 to -1

	'''
	side = kwargs.get('side', None)
	des = kwargs.get('description', None)
	index = kwargs.get('index', None)

	strBool = isinstance(operand, basestring)
	if strBool:
		multNode = node(type=naming.Type.multDoubleLinear,
						side=side, description=des, index=index,
						autoSuffix=True, setAttrs={'input2':-1})
		
		cmds.connectAttr(operand, multNode+'.input1')

		return multNode+'.output'
	else:
		return -operand

#=================#
#    SUB CLASS    #
#=================#

# operation
_BINOP_MAP = {
	ast.Add: _add,
	ast.Sub: _sub,
	ast.Mult: _mult,
	ast.Div: _divide,
	ast.Pow: _pow}

_UNARYOP_MAP = {
	ast.USub : _uSub,
	ast.Invert : _reverse}

class NodeEquation(ast.NodeVisitor):

	def visit_BinOp(self, node):
		left = self.visit(node.left)
		right = self.visit(node.right)
		return _BINOP_MAP[type(node.op)](left, right,
										 side=self.side,
										 description=self.des,
										 index=self.index)

	def visit_UnaryOp(self, node):
		operand = self.visit(node.operand)
		return _UNARYOP_MAP[type(node.op)](operand,
										   side=self.side,
										   description=self.des,
										   index=self.index)

	def visit_Num(self, node):
		return node.n

	def visit_Expr(self, node):
		return self.visit(node.value)

	def visit_Attribute(self, node):
		return '{}.{}'.format(node.value.id, node.attr)

	@classmethod
	def equation(cls, expression, **kwargs):
		cls.side = kwargs.get('side', None)
		cls.des = kwargs.get('description', None)
		cls.index = kwargs.get('index', None)

		tree = ast.parse(expression)
		calc = cls()
		return calc.visit(tree.body[0])