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
import common.naming.namingDict as namingDict
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import common.nodes as nodes
import rigging.joints as joints
import rigging.controls.controls as controls
import rigging.constraints as constraints
# ---- import end ----

# -- import component
import baseBehavior
# ---- import end ----

class SingleChainAimBehavior(baseBehavior.BaseBehavior):
	"""SingleChainAimBehavior template"""
	def __init__(self, **kwargs):
		super(SingleChainAimBehavior, self).__init__(**kwargs)
		self._jointSuffix = kwargs.get('jointSuffix', 'AimSC')

	def create(self):
		super(SingleChainAimBehavior, self).create()

		# create aim controls
		NamingCtrl = naming.Naming(self._joints[0])

		ControlRoot = controls.create(NamingCtrl.part + 'Root', side = NamingCtrl.side, 
				index = NamingCtrl.index, stacks = self._stacks, parent = self._controlsGrp,
				posParent = self._joints[0], lockHide = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

		MMatrixLocal = transforms.getLocalMatrix(self._joints[-1], self._joints[0], returnType = 'MMatrix')
		transformInfo = apiUtils.decomposeMMatrix(MMatrixLocal)
		targetPos = transforms.getWorldTransformOnParent(translate = [transformInfo[0][0], 0, 0], parent = self._joints[0])
		ControlTarget = controls.create(NamingCtrl.part + 'Target', side = NamingCtrl.side, 
				index = NamingCtrl.index, stacks = self._stacks, parent = self._controlsGrp,  
				posParent = targetPos, lockHide = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

		self._controls += [ControlRoot.name, ControlTarget.name]

		# aimConstraint
		cmds.addAttr(ControlRoot.name, ln = 'twist', at = 'float', dv = 0, keyable = True)
		
		multMatrixTwist = nodes.create(type = 'multMatrix', side = NamingCtrl.side,
							part = '{}Twist'.format(NamingCtrl.part), index = NamingCtrl.index)
		composeMatrixTwist = nodes.create(type = 'composeMatrix', side = NamingCtrl.side,
							part = '{}Twist'.format(NamingCtrl.part), index = NamingCtrl.index)
		matrixUp = cmds.getAttr(ControlRoot.matrixWorldPlug)
		
		cmds.connectAttr('{}.twist'.format(ControlRoot.name), '{}.inputRotateX'.format(composeMatrixTwist))
		cmds.connectAttr('{}.outputMatrix'.format(composeMatrixTwist), '{}.matrixIn[0]'.format(multMatrixTwist))
		cmds.setAttr('{}.matrixIn[1]'.format(multMatrixTwist), matrixUp, type = 'matrix')

		cmds.addAttr(ControlRoot.name, ln = 'matrixUpVector', at = 'matrix')
		cmds.connectAttr('{}.matrixSum'.format(multMatrixTwist), '{}.matrixUpVector'.format(ControlRoot.name))

		constraints.matrixAimConstraint(ControlTarget.matrixWorldPlug, self._joints[0], worldUpType = 'objectrotation', 
									worldUpMatrix = '{}.matrixUpVector'.format(ControlRoot.name), local = True)

		# connet root
		constraints.matrixConnect(ControlRoot.name, ControlRoot.matrixWorldAttr, self._joints[0], force = True, skipRotate = ['x', 'y', 'z'], 
						  		  skipScale = ['x', 'y', 'z'])