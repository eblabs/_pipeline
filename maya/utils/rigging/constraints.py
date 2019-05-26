#=================#
# IMPORT PACKAGES #
#=================#

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.naming as naming
import utils.common.attributes as attributes
import utils.common.variables as variables
import utils.common.nodeUtils as nodeUtils
import utils.common.mathUtils as mathUtils
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

def matrix_connect(inputMatrix, nodes, **kwargs):
	'''
	connect input matrix to given nodes

	Args:
		inputMatrix(str): input matrix attribute
		nodes(str/list): given nodes
	Kwargs:
		offset(bool)[False]: maintain offset
		skip(list): skip channels
		force(bool)[True]: force connect
	'''
	offset = variables.kwargs('offset', '', kwargs)
	skip = variables.kwargs('skip', [], kwargs)
	force = variables.kwargs('force', True, kwargs, shortName='f')

	driver = inputMatrix.split('.')[0]
	attrName = cmds.ls(inputMatrix)[0].split('.')[-1]
	
	NameDriver = naming.Namer(driver)
	NameDriver.type = naming.Type.decomposeMatrix
	NameDriver.description = NameDriver.description + attrName[0].upper() + attrName[1:]

	desOffset = NameDriver.description+'Offset'

	if isinstance(nodes, basestring):
		nodes = [nodes]

	if offset:
		matrixOffset = cmds.getAttr(offset+'.worldMatrix[0]')

	driverAttrs = []
	drivenAttrs = []
	for attr in attributes.Attr.transform:
		attrShort = attr[0]+attr[-1].lower()
		if attr not in skip and attrShort not in skip:
			driverAttrs.append('output{}{}'.format(attr[0].upper(), attr[1:]))
			drivenAttrs.append(attr)

	if not offset:
		decomposeMatrix = nodeUtils.node(name=NameDriver.name, useExist=True)
		cmds.connectAttr(inputMatrix, decomposeMatrix+'.inputMatrix')
		for n in nodes:
			attributes.connect_attrs(driverAttrs, drivenAttrs,
									 driver=decomposeMatrix, driven=n, force=force)
	else:
		# get latest suffix
		multMatrixOffset = naming.Namer(type=naming.Type.multMatrix,
										side=NameDriver.side,
										description=desOffset,
										index=NameDriver.index).name
		multMatrixOffset = cmds.ls(multMatrixOffset+'_???')
		if multMatrixOffset:
			multMatrixOffset.sort()
			NameOffset = naming.Namer(multMatrixOffset[-1])
			if NameOffset.suffix:
				suffix = NameOffset.suffix
			elif NameOffset.index:
				suffix = NameOffset.index
		else:
			suffix = 0
		for i, n in enumerate(nodes):
			offsetMatrix = cmds.getAttr(n+'.worldMatrix[0]')
			offsetMatrixInv = mathUtils.inverse_matrix(offsetMatrix)
			multMatrix = nodeUtils.mult_matrix([inputMatrix, offsetMatrixInv],
											   side=NameDriver.side,
											   description=desOffset,
											   index=NameDriver.index,
											   suffix=suffix+i+1)
			decomposeMatrix = nodeUtils.node(type=naming.Type.decomposeMatrix,
											 side=NameDriver.side,
											 description=desOffset,
											 index=NameDriver.index,
											 suffix=suffix+i+1)
			cmds.connectAttr(multMatrix+'.matrixSum', decomposeMatrix+'.inputMatrix')
			attributes.connect_attrs(driverAttrs, drivenAttrs,
									 driver=decomposeMatrix, driven=n, force=force)

def matrix_aim_constraint(inputMatrix, drivens, **kwargs):
	'''
	aim constraint using matrix connection

	Args:
		inputMatrix(str): input matrix attribute
		drivens(str/list): driven nodes
	Kwargs:
		parent(str): parent constraint node to, None will parent under driven node
		worldUpType(str)['objectrotation']
		worldUpMatrix(str)
		aimVector(list)[1,0,0]
		upVector(list)[0,1,0]
		local(bool)[False]: local will skip parent inverse matrix connection
	'''
	# get vars
	parent = variables.kwargs('parent', None, kwargs, shortName='p')
	worldUpType = variables.kwargs('worldUpType', 'objectrotation', kwargs)
	worldUpMatrix = variables.kwargs('worldUpMatrix', None, kwargs)
	aimVector = variables.kwargs('aimVector', [1,0,0], kwargs, shortName='aim')
	upVector = variables.kwargs('upVector', [0,1,0], kwargs, shortName='up')
	local = variables.kwargs('local', False, kwargs)

	# world up type
	if worldUpType == 'objectrotation':
		worldUpType = 2
	else:
		worldUpType = 1

	if isinstance(drivens, basestring):
		drivens = [drivens]

	driverNode = inputMatrix.split('.')[0]
	NamerAim = naming.Namer(driverNode)
	NamerAim.type = naming.Type.decomposeMatrix
	NamerAim.description = NamerAim.description+'Aim'

	for d in drivens:
		if cmds.objExists(d):
			Namer = naming.Namer(d)
			Namer.type = naming.Type.aimConstraint
			aimConstraint = nodeUtils.node(name=Namer.name)
			if not parent or not cmds.objExists(parent):
				parent = d
			cmds.parent(aimConstraint, parent)

			decomposeMatrix = nodeUtils.node(name=NamerAim.name, useExist=True)
			cmds.connectAttr(inputMatrix, decomposeMatrix+'.inputMatrix', f=True)

			for i, axis in enumerate('XYZ'):
				cmds.setAttr('{}.aimVector{}'.format(aimConstraint, axis), aimVector[i])
				cmds.setAttr('{}.upVector{}'.format(aimConstraint, axis), upVector[i])
				cmds.connectAttr('{}.translate{}'.format(d, axis), 
								 '{}.constraintTranslate{}'.format(aimConstraint, axis))
				cmds.connectAttr('{}.outputTranslate{}'.format(decomposeMatrix, axis), 
								 '{}.target[0].targetTranslate{}'.format(aimConstraint, axis))

			if cmds.objectType(d) == 'joint':
				for axis in 'XYZ':
					cmds.connectAttr('{}.jointOrient{}'.format(d, axis), 
									 '{}.constraintJointOrient{}'.format(aimConstraint, axis))

			if not local:
				cmds.connectAttr(d+'.parentInverseMatrix[0]', 
								 aimConstraint+'.constraintParentInverseMatrix')
			cmds.connectAttr(worldUpMatrix, aimConstraint+'.worldUpMatrix')
			cmds.setAttr(aimConstraint+'.worldUpType', worldUpType)
			cmds.setAttr(aimConstraint+'.target[0].targetParentMatrix', 
						 mathUtils.MATRIX_DEFAULT, type='matrix')

			for axis in 'XYZ':
				attributes.connect_attrs('{}.constraintRotate{}'.format(aimConstraint, axis), 
								 		 '{}.rotate{}'.format(d, axis))

def matrix_pole_vector_constraint(inputMatrix, ikHandle, joint, **kwargs):
	'''
	pole vector constraint using matrix connection

	Args:
		inputMatrix(str): input matrix attribute
		ikHandle(str): driven ikHandle
		joint(str): root joint of the ik chain
	Kwargs:
		parent(str): parent constraint node to, None will parent under driven node
		parentInverseMatrix(str)[None]: ikHandle's parent inverse matrix,
										None will use ikHandle's parentInverseMatrix attr
	'''
	# get vars
	parent = variables.kwargs('parent', None, kwargs, shortName='p')
	parentInverseMatrix = variables.kwargs('parentInverseMatrix', None, kwargs)
	
	# get name
	Namer = naming.Namer(ikHandle)
	decomposeMatrix = nodeUtils.node(type=naming.Type.decomposeMatrix,
									 side=Namer.side,
									 description=Namer.description+'Pv',
									 index=Namer.index)
	cmds.connectAttr(inputMatrix, decomposeMatrix+'.inputMatrix')

	# constraint
	pvCons = nodeUtils.node(type=naming.Type.poleVectorConstraint,
							side=Namer.side,
							description=Namer.description+'Pv',
							index=Namer.index)
	if not parent or not cmds.objExists(parent):
		parent = ikHandle
	cmds.parent(pvCons, parent)

	for outputAttr, inputAttr in zip([decomposeMatrix+'.outputTranslate',
									  joint+'.translate'],
									 ['target[0].targetTranslate',
									  'constraintRotatePivot']):
		for axis in 'XYZ':
			cmds.connectAttr(outputAttr+axis, '{}.{}{}'.format(pvCons, inputAttr, axis))
	if not parentInverseMatrix:
		parentInverseMatrix = ikHandle+'.parentInverseMatrix[0]'
	cmds.connectAttr(parentInverseMatrix, pvCons+'.constraintParentInverseMatrix')

	# output
	for axis in 'XYZ':
		cmds.connectAttr('{}.constraintTranslate{}'.format(pvCons, axis),
						 '{}.poleVector{}'.format(ikHandle, axis), f=True)

#=================#
#  SUB FUNCTION   #
#=================#