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
def matrixConnect(driver, attr, drivens, skipTranslate=None, skipRotate=None, skipScale=None, force=True, quatToEuler=True):
	'''
	matrix connect

	create multMatrix and decompose matrix node to connect the node

	driver(string)
	attr(string)
	drivens(string/list)
	skipTranslate(list)
	skipRotate(list)
	skipScale(list)
	force(bool)
	quatToEuler(bool)
	'''
	# get name
	NamingNode = naming.Naming(driver)

	if isinstance(drivens, basestring):
		drivens = [drivens]

	# create decompose matrix node
	NamingNode.type = 'decomposeMatrix'
	decomposeMatrix = cmds.createNode('decomposeMatrix', name = NamingNode.name)
	cmds.connectAttr('{}.{}'.format(driver, attr), '{}.inputMatrix'.format(decomposeMatrix))

	decomposeRot = decomposeMatrix

	if not skipRoate or len(skipRotate) < 3:
		if quatToEuler:
			NamingNode.type = 'quatToEuler'
			decomposeRot = cmds.createNode('quatToEuler', name = NamingNode.name)
			cmds.connectAttr('{}.outputQuat'.format(decomposeMatrix), 
							 '{}.inputQuat'.format(decomposeRot))
			cmds.connectAttr('{}.ro'.format(drivens[0]), '{}.inputRotateOrder'.format(decomposeRot))

	for d in drivens:
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