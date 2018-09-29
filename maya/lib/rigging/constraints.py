# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import common.naming.naming as naming
import common.attributes as attributes
import common.apiUtils as apiUtils
import common.nodes as nodes
import common.hierarchy as hierarchy
# ---- import end ----

# matrix connect
def matrixConnect(driver, attr, drivens, offset = False, skipTranslate=None, skipRotate=None, skipScale=None, force=True, quatToEuler=True):
	'''
	matrix connect

	create multMatrix and decompose matrix node to connect the node

	driver(string)
	attr(string)
	drivens(string/list)
	offset(string): will maintain offset base on the given node, default is False
	skipTranslate(list)
	skipRotate(list)
	skipScale(list)
	force(bool)
	quatToEuler(bool)
	'''
	# get name
	NamingDecompose = naming.Naming(driver)
	NamingDecompose.type = 'decomposeMatrix'
	NamingOffset = naming.Naming(driver)
	NamingOffset.part = '{}Offset'.format(NamingOffset.part)

	if isinstance(drivens, basestring):
		drivens = [drivens]

	if offset:
		offsetList = cmds.getAttr('{}.worldMatrix[0]'.format(offset))
		MMatrixOffset = apiUtils.convertListToMMatrix(offsetList)
		
	for d in driven:
		decomposeMatrix = NamingDecompose.name

		if offset:
			drivenList = cmds.getAttr('{}.worldMatrix[0]'.format(d))
			# check if need offset
			if drivenList != offsetList:
				MMatrixDriven = apiUtils.convertListToMMatrix(drivenList)
				matrixLocal = apiUtils.convertMMatrixToList(MMatrixDriven * MMatrixOffset.inverse())
				
				multMatrixOffsetList = cmds.ls('{}_*'.format(NamingOffset.name))
				multMatrixOffset = nodes.create(type = 'multMatrix', 
												side = NamingOffset.side,
												part = NamingOffset.part,
												index = NamingOffset.index,
												suffix = len(multMatrixOffsetList) + 1)

				cmds.setAttr('{}.matrixIn[0]'.format(multMatrixOffset), matrixLocal, type = 'matrix')
				cmds.connectAttr('{}.{}'.format(driver, attr), '{}.matrixIn[1]'.format(multMatrixOffset))

				decomposeMatrixList = cmds.ls('{}_*'.format(NamingOffset.name))
				decomposeMatrix = nodes.create(type = 'decomposeMatrix', 
											   side = NamingOffset.side,
											   part = NamingOffset.part,
											   index = NamingOffset.index,
											   suffix = len(decomposeMatrixList) + 1)

				cmds.connectAttr('{}.matrixSum'.format(multMatrixOffset), '{}.inputMatrix'.format(decomposeMatrix))

			else:
				if not cmds.objExists(decomposeMatrix):
					decomposeMatrix = nodes.create(name = decomposeMatrix)
					cmds.connectAttr('{}.{}'.format(driver, attr), '{}.inputMatrix'.format(decomposeMatrix))
		else:
			if not cmds.objExists(decomposeMatrix):
				decomposeMatrix = nodes.create(name = decomposeMatrix)
				cmds.connectAttr('{}.{}'.format(driver, attr), '{}.inputMatrix'.format(decomposeMatrix))
		
		decomposeRot = decomposeMatrix

		if not skipRoate or len(skipRotate) < 3:
			if quatToEuler:
				NamingRot = naming.Naming(decomposeMatrix)
				NamingRot.type = 'quatToEuler'
				decomposeRot = NamingRot.name

				if not cmds.objExists(decomposeRot):
					decomposeRot = nodes.create(name = decomposeRot)
					cmds.connectAttr('{}.outputQuat'.format(decomposeMatrix), 
									 '{}.inputQuat'.format(decomposeRot))
					cmds.connectAttr('{}.ro'.format(d), '{}.inputRotateOrder'.format(decomposeRot))

		for axis in ['x', 'y', 'z']:
			if axis not in skipTranslate:
				attributes.connectAttrs('outputTranslate{}'.format(axis.upper()), 
										'translate{}'.format(axis.upper()), 
										driver = decomposeMatrix, 
										driven = d, force=True)

			if axis not in skipRotate:
				attributes.connectAttrs('outputRotate{}'.format(axis.upper()), 
										'rotate{}'.format(axis.upper()), 
										driver = decomposeRot, 
										driven = d, force=True)
			
			if axis not in skipScale:
				attributes.connectAttrs('outputScale{}'.format(axis.upper()), 
										'scale{}'.format(axis.upper()), 
										driver = decomposeMatrix, 
										driven = d, force=True)

# constraint blend
def constraintBlend(inputMatrixList, driven, weightList=[], translate=True, rotate=True, scale=True, parent=None):
	NamingNode = naming.Naming(driven)
	constraintType = ['pointConstraint', 'orientConstraint', 'scaleConstraint']
	attrType = ['Translate', 'Rotate', 'Scale']
	if not isinstance(weightList, list):
		weightList = weightList * len(inputMatrixList)
	if not parent:
		parent = driven

	attrs = []
	constraints = []
	for i, attr in enumerate([translate, rotate, scale]):
		if attr:
			con = nodes.create(type = constraintType[i],
									   side = NamingNode.side,
									   part = NamingNode.part,
									   index = NamingNode.index)
			hierarchy.parent(con, parent)
			attrs.append(attrType[i])
			constraints.append(con)
	
	# set orientConstraint interp type
	if rotate:
		index = attrs.index('Rotate')
		cmds.setAttr('{}.interpType'.format(constraints[index]), 2)

	for i, inputPlug in enumerate(inputMatrixList):
		inputNode = inputPlug.split('.')[0]
		NamingInput = naming.Naming(inputNode)
		decomposeMatrix = nodes.create(type = 'decomposeMatrix', 
									   side = NamingInput.side,
									   part = NamingInput.part,
									   index = NamingInput.index)
		attributes.connectAttrs(inputPlug, '{}.inputMatrix'.format(decomposeMatrix))

		for j, con in enumerate(constraints):
			attr = attrs[j]
			for axis in 'XYZ':
				cmds.connectAttr('{}.output{}{}'.format(decomposeMatrix, attr, axis), 
							'{}.target[{}].target{}{}'.format(con, i, attr, axis))
			if isinstance(weightList[j], basestring):
				cmds.connectAttr(weightList[j], '{}.target[{}].targetWeight'.format(con, i))
			else:
				cmds.setAttr('{}.target[{}].targetWeight'.format(con, i), weightList[j])

	for i, con in enumerate(constraints):
		attr = attrs[j]
		for axis in 'XYZ':
			cmds.connectAttr('{}.constraint{}{}'.format(con, attr, axis), 
							'{}.{}{}'.format(driven, attr.lower(), axis))

# matrix aim constraint
def matrixAimConstraint(inputMatrix, drivens, parent=None, worldUpType='objectrotation', worldUpMatrix=None, aimVector=[1,0,0], upVector=[0,1,0]):
	if worldUpType == 'objectrotation':
		worldUpType = 2
	elif worldUpType == 'objectUp':
		worldUpType = 1

	if isinstance(drivens):
		drivens = [drivens]

	for driven in drivens:
		NamingNode = naming.Naming(driven)
		NamingNode.type = 'aimConstraint'
		aimConstraint = nodes.create(name = NamingNode.name)
		hierarchy.parent(aimConstraint, parent)

		NamingNode.type = 'decomposeMatrix'
		NamingNode.part = NamingNode.part + 'Aim'
		decomposeMatrix = nodes.create(name = NamingNode.name)
		cmds.connectAttr(inputMatrix, '{}.inputMatrix'.format(decomposeMatrix))

		for i, axis in enumerate('XYZ'):
			cmds.setAttr('{}.aimVector{}'.format(aimConstraint), aimVector[i])
			cmds.setAttr('{}.upVector{}'.format(aimConstraint), upVector[i])
			cmds.connectAttr('{}.translate{}'.format(driven, axis), '{}.constraintTranslate{}'.format(aimConstraint, axis))
			cmds.connectAttr('{}.outputTranslate{}'.format(decomposeMatrix, axis), '{}.target[0].targetTranslate{}'.format(aimConstraint, axis))

		cmds.connectAttr('{}.parentInverseMatrix[0]'.format(driven), '{}.constraintParentInverseMatrix'.format(aimConstraint))
		cmds.connectAttr(worldUpMatrix, '{}.worldUpMatrix'.format(aimConstraint))
		cmds.connectAttr('{}.worldUpType'.format(aimConstraint), worldUpType)

		for axis in 'XYZ':
			cmds.connectAttr('{}.constraintRotate{}'.format(aimConstraint, axis), '{}.rotate{}'.format(driven, axis))

