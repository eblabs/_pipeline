# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import lib.common.naming.naming as naming
import lib.common.transforms as transforms
import lib.common.attributes as attributes
import lib.common.apiUtils as apiUtils
import lib.common.nodeUtils as nodeUtils
import lib.rigging.joints as joints
import lib.rigging.controls.controls as controls
import lib.rigging.constraints as constraints
# ---- import end ----

# -- import component
import baseBehavior
# ---- import end ----

class TwistBehavior(baseBehavior.BaseBehavior):
	"""TwsitBehavior template"""
	def __init__(self, **kwargs):
		super(TwistBehavior, self).__init__(**kwargs)
		self._jointsNumber = kwargs.get('jointsNumber', 5)
		self._jointSuffix = kwargs.get('jointSuffix', 'Twist')
		self._controlShapes = kwargs.get('controlShapes', ['cube', 'rotate'])

	def create(self):
		# get twist info
		if self._jointsNumber < 3:
			self._jointsNumber = 3

		self._twistName = self._part + self._jointSuffix

		# create joints
		self._joints = joints.createInBetweenJoints(self._blueprintJoints[0], 
						self._blueprintJoints[-1], self._jointsNumber, 
						overrideName = self._twistName, parent = self._jointsGrp)

		jointsLocal = joints.createInBetweenJoints(self._blueprintJoints[0], 
						self._blueprintJoints[-1], self._jointsNumber, 
						overrideName = self._twistName + 'Local', parent = self._nodesHideGrp)

		for jnts in zip(self._joints, jointsLocal):
			for attr in ['translate', 'rotate', 'scale']:
				for axis in 'XYZ':
					cmds.connectAttr('{}.{}{}'.format(jnts[1], attr, axis),
									 '{}.{}{}'.format(jnts[0], attr, axis))

		# create controls for each joint
		twistCtrls = []
		twistCtrlObjs = []
		for i, jnt in enumerate(jointsLocal):
			Control = controls.create('{}{:03d}'.format(self._twistName, i), side = self._side, index = self._index,
									stacks = self._stacks, parent = self._controlsGrp, posParent = jnt, 
									lockHide = ['sx', 'sy', 'sz'], shape = self._controlShapes[1])

			# connect with joint
			multMatrix = nodeUtils.create(type = 'multMatrix', side = self._side,
										part = '{}Pos'.format(Control.part), index = self._index)
			if i > 0:
				attributes.connectAttrs([Control.matrixWorldPlug, '{}.worldInverseMatrix[0]'.format(jointsLocal[i - 1])],
										['matrixIn[0]', 'matrixIn[1]'], driven = multMatrix)
				constraints.matrixConnect(multMatrix, 'matrixSum', jnt, skipScale = ['x', 'y', 'z'])
			else:
				jntOrient = joints.getJointOrient(jnt)
				MMatrix = apiUtils.composeMMatrix(rotate = jntOrient)
				matrixList = apiUtils.convertMMatrixToList(MMatrix.inverse())
				cmds.connectAttr(Control.matrixWorldPlug, '{}.matrixIn[0]'.format(multMatrix))
				cmds.setAttr('{}.matrixIn[1]'.format(multMatrix), matrixList, type = 'matrix')
				constraints.matrixConnect(Control.name, Control.matrixWorldAttr, jnt, skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'])		
				constraints.matrixConnect(multMatrix, 'matrixSum', jnt, skipTranslate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'])

			twistCtrls.append(Control.name)
			twistCtrlObjs.append(Control)

		# create start end controls
		ControlList = []
		for i, jnt in enumerate([self._blueprintJoints[0], self._blueprintJoints[-1]]):
			ctrlPos = ['Start', 'End'][i]			
			Control = controls.create(self._twistName + ctrlPos, side = self._side, index = self._index,
									stacks = self._stacks, parent = self._controlsGrp, posParent = jnt, 
									lockHide = ['sx', 'sy', 'sz'], shape = self._controlShapes[0])

			#Control.lockHideAttrs('ro')
			ControlList.append(Control)
			self._controls.append(Control.name)

		# connect driver control with root and end twist control
		constraints.matrixConnect(ControlList[0].name, ControlList[0].matrixLocalAttr, twistCtrlObjs[0].passer,
							skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'], quatToEuler = False)
		constraints.matrixConnect(ControlList[-1].name, ControlList[-1].matrixLocalAttr, twistCtrlObjs[-1].passer,
							skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'], quatToEuler = False)

		# get decompose node for reuse

		decomposeStart = cmds.listConnections('{}.tx'.format(twistCtrlObjs[0].passer), s = True, 
														d = False, p = False)[0]
		decomposeEnd = cmds.listConnections('{}.tx'.format(twistCtrlObjs[-1].passer), s = True, 
														d = False, p = False)[0]

		# extract twist

		transforms.extractTwist(ControlList[0].name, nodeMatrix = ControlList[0].matrixLocalAttr, 
								attr='twistExctration', quatOverride = decomposeStart)
		transforms.extractTwist(ControlList[-1].name, nodeMatrix = ControlList[-1].matrixLocalAttr, 
								attr='twistExctration', quatOverride = decomposeEnd)

		cmds.connectAttr('{}.twistExctration'.format(ControlList[0].name), '{}.rx'.format(twistCtrlObjs[0].passer))
		cmds.connectAttr('{}.twistExctration'.format(ControlList[-1].name), '{}.rx'.format(twistCtrlObjs[-1].passer))

		# weight blend translate and twist, skip first and last joint
		weightDiv = 1.0/float(self._jointsNumber-1)

		for i, Obj in enumerate(twistCtrlObjs[1: self._jointsNumber-1]):
			weightVal = weightDiv * (i + 1)

			attributes.weightBlendAttr(Obj.passer, 'translate', 
									   ['{}.outputTranslate'.format(decomposeStart),
									    '{}.outputTranslate'.format(decomposeEnd)],
									   weightList = [1 - weightVal, weightVal], attrType = 'triple')

			attributes.weightBlendAttr(Obj.passer, 'rx', 
									   ['{}.twistExctration'.format(self._controls[0]),
									    '{}.twistExctration'.format(self._controls[1])],
									   weightList = [1 - weightVal, weightVal], attrType = 'single')

		# pass info
		self._controls += twistCtrls