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
import common.attributes
import common.apiUtils
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
	NamingOffset.type = 'multMatrix'
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
				NamingOffset.suffix = len(multMatrixOffsetList) + 1
				multMatrixOffset = cmds.createNode('multMatrix', name = NamingOffset.name)
				NamingOffset.suffix = None

				cmds.setAttr('{}.matrixIn[0]'.format(multMatrixOffset), matrixLocal, type = 'matrix')
				cmds.connectAttr('{}.{}'.format(driver, attr), '{}.matrixIn[1]'.format(multMatrixOffset))

				NamingOffset.type = 'decomposeMatrix'
				decomposeMatrixList = cmds.ls('{}_*'.format(NamingOffset.name))
				NamingOffset.suffix = len(decomposeMatrixList) + 1
				decomposeMatrix = cmds.createNode('decomposeMatrix', name = NamingOffset.name)
				NamingOffset.type = 'multMatrix'
				NamingOffset.suffix = None

				cmds.connectAttr('{}.matrixSum'.format(multMatrixOffset), '{}.inputMatrix'.format(decomposeMatrix))

			else:
				if not cmds.objExists(decomposeMatrix):
					decomposeMatrix = cmds.createNode('decomposeMatrix', name = decomposeMatrix)
					cmds.connectAttr('{}.{}'.format(driver, attr), '{}.inputMatrix'.format(decomposeMatrix))
		else:
			if not cmds.objExists(decomposeMatrix):
				decomposeMatrix = cmds.createNode('decomposeMatrix', name = decomposeMatrix)
				cmds.connectAttr('{}.{}'.format(driver, attr), '{}.inputMatrix'.format(decomposeMatrix))
		
		decomposeRot = decomposeMatrix

		if not skipRoate or len(skipRotate) < 3:
			if quatToEuler:
				NamingRot = naming.Naming(decomposeMatrix)
				NamingRot.type = 'quatToEuler'
				decomposeRot = NamingRot.name

				if not cmds.objExists(decomposeRot):
					decomposeRot = cmds.createNode('quatToEuler', name = decomposeRot)
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