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
import lib.common.naming.namingDict as namingDict
import lib.common.transforms as transforms
import lib.common.attributes as attributes
import lib.common.apiUtils as apiUtils
import lib.common.nodes as nodes
import lib.rigging.joints as joints
reload(joints)
reload(transforms)
reload(attributes)
import lib.rigging.controls.controls as controls
import lib.rigging.constraints as constraints
# ---- import end ----

# -- import component
import baseBehavior
reload(baseBehavior)
# ---- import end ----

class TwistBehavior(baseBehavior.BaseBehavior):
	"""TwsitBehavior template"""
	def __init__(self, **kwargs):
		super(TwistBehavior, self).__init__(**kwargs)
		self._jointsNumber = kwargs.get('jointsNumber', 5)
		self._jointSuffix = kwargs.get('jointSuffix', 'Twist')

	def create(self):
		# get twist info
		if self._jointsNumber < 3:
			self._jointsNumber = 3

		self._twistName = self._part + self._jointSuffix

		# create joints
		self._joints = joints.createInBetweenJoints(self._blueprintJoints[0], 
						self._blueprintJoints[-1], self._jointsNumber, 
						overrideName = self._twistName, parent = self._jointsGrp)

		# create start end controls
		ControlList = []
		multMatrixList = []
		for i, jnt in enumerate([self._blueprintJoints[0], self._blueprintJoints[-1]]):
			ctrlPos = ['Start', 'End'][i]			
			Control = controls.create(self._twistName + ctrlPos, side = self._side, index = self._index,
									stacks = self._stacks, parent = self._controlsGrp, posParent = jnt, 
									lockHide = ['sx', 'sy', 'sz'])
			multMatrix = nodes.create(type = 'multMatrix', side = self._side, 
									part = '{}TwistTrans'.format(Control.part), index = self._index)
			pos = cmds.xform(Control.zero, q = True, t = True, ws = True)
			MMatrix = apiUtils.composeMMatrix(translate = pos)
			matrixList = apiUtils.convertMMatrixToList(MMatrix)
			cmds.connectAttr(Control.matrixLocalPlug, '{}.matrixIn[0]'.format(multMatrix))
			cmds.setAttr('{}.matrixIn[1]'.format(multMatrix), matrixList, type = 'matrix')
			multMatrixList.append(multMatrix)

			#Control.lockHideAttrs('ro')
			ControlList.append(Control)
			self._controls.append(Control.name)

		# connect start control with root joint
		constraints.matrixConnect(ControlList[0].name, ControlList[0].matrixLocalAttr, self._joints[0], 
						skipTranslate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'], 
						force = True, quatToEuler = False)
		constraints.matrixConnect(multMatrixList[0], 'matrixSum', self._joints[0], 
						skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'], force = True)

		# get decompose node for reuse

		decomposeTranslateStart = cmds.listConnections('{}.tx'.format(self._joints[0]), s = True, 
														d = False, p = False)[0]
		decomposeRotStart = cmds.listConnections('{}.rx'.format(self._joints[0]), s = True, 
													d = False, p = False, scn = True)[0]

		# extract twist

		transforms.extractTwist(ControlList[0].name, nodeMatrix = ControlList[0].matrixLocalAttr, 
								attr='twistExctration', quatOverride = decomposeRotStart)

		transforms.extractTwist(ControlList[1].name, nodeMatrix = ControlList[1].matrixLocalAttr, attr='twistExctration')

		# decompose translate end
		decomposeTranslateEnd = nodes.create(type = 'decomposeMatrix', side = self._side, 
								part = '{}Translate'.format(ControlList[1].part), index = self._index)

		attributes.connectAttrs('{}.matrixSum'.format(multMatrixList[1]),
								'{}.inputMatrix'.format(decomposeTranslateEnd))

		# weight blend translate and twist, skip first and last joint
		weight = 1.0/float(self._jointsNumber-1)

		attributes.weightBlendAttr(self._joints[1:], 'translate', 
								   ['{}.outputTranslate'.format(decomposeTranslateStart),
								    '{}.outputTranslate'.format(decomposeTranslateEnd)],
								   weightList = [-1*weight, weight], attrType = 'triple')

		attributes.weightBlendAttr(self._joints[1:], 'rx', 
								   ['{}.twistExctration'.format(self._controls[0]),
								    '{}.twistExctration'.format(self._controls[1])],
								   weightList = [-1*weight, weight], attrType = 'single')