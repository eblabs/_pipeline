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
		self._twistName = kwargs.get('twistName', '')
		self._jointSuffix = kwargs.get('jointSuffix', 'Twist')

	def create(self):
		# get twist info
		if self._jointsNumber < 3:
			self._jointsNumber = 3

		NamingNode = naming.Naming(self._blueprintJoints[0])
		if not self._twistName:
			self._twistName = NamingNode.part
		self._twistName += self._jointSuffix

		dis = cmds.getAttr('{}.tx'.format(self._blueprintJoints[-1]))
		weightDiv = float(1)/float(self._jointsNumber - 1)
		disDiv = dis * weightDiv

		CtrlObjList = []

		# create joints
		for i in range(self._jointsNumber):
			NamingJnt = naming.Naming(type = 'joint', side = NamingNode.side,
								part = '{}{:03d}'.format(self._twistName, i+1),
								index = NamingNode.index)
			transformInfo = transforms.getWorldTransformOnParent(translate = [disDiv*i,0,0], parent = self._blueprintJoints[0])
			jnt = joints.create(NamingJnt.name, parent = self._jointsGrp, posParent = transformInfo)
			self._joints.append(jnt)

			Control = controls.create(NamingJnt.part, side = NamingJnt.side, index = NamingJnt.index,
								stacks = self._stacks, parent = self._controlsGrp, posParent = jnt, 
								lockHide = ['tx', 'ty', 'tz', 'ry', 'rz', 'sx', 'sy', 'sz'])

			Control.lockHideAttrs('ro')

			self._controls.append(Control.name)
			CtrlObjList.append(Control)

			## connect ctrl to joint
			constraints.matrixConnect(Control.name, Control.matrixLocalAttr, jnt, skipTranslate = ['x', 'y', 'z'], 
						  skipScale = ['x', 'y', 'z'], force = True, quatToEuler = False)
			constraints.matrixConnect(Control.name, Control.matrixWorldAttr, jnt, skipRotate = ['x', 'y', 'z'], 
						  skipScale = ['x', 'y', 'z'], force = True)

		# create start end controls
		ControlStart = controls.create(self._twistName + 'Start', side = NamingNode.side, index = NamingNode.index,
								stacks = self._stacks, parent = self._controlsGrp, posParent = self._blueprintJoints[0], 
								lockHide = ['tx', 'ty', 'tz', 'ry', 'rz', 'sx', 'sy', 'sz'])
		ControlStart.lockHideAttrs('ro')

		ControlEnd = controls.create(self._twistName + 'End', side = NamingNode.side, index = NamingNode.index,
								stacks = self._stacks, parent = self._controlsGrp, posParent = self._blueprintJoints[-1], 
								lockHide = ['tx', 'ty', 'tz', 'ry', 'rz', 'sx', 'sy', 'sz'])
		ControlEnd.lockHideAttrs('ro')

		# extract twist
		transforms.extractTwist(ControlStart.name, nodeMatrix = ControlStart.matrixLocalAttr, attr='twistExctration')
		transforms.extractTwist(ControlEnd.name, nodeMatrix = ControlEnd.matrixLocalAttr, attr='twistExctration')

		# decompose translate
		decomposeStart = nodes.create(type = 'decomposeMatrix', side = NamingNode.side, 
							part = '{}Translate'.format(ControlStart.part), index = NamingNode.index)
		decomposeEnd = nodes.create(type = 'decomposeMatrix', side = NamingNode.side, 
							part = '{}Translate'.format(ControlEnd.part), index = NamingNode.index)

		attributes.connectAttrs([ControlStart.matrixWorldPlug, ControlEnd.matrixWorldPlug],
								['{}.inputMatrix'.format(decomposeStart),
								 '{}.inputMatrix'.format(decomposeEnd)])


		for i, Ctrl in enumerate(CtrlObjList):			
			weightEnd = weightDiv*i
			weightStart = 1 - weightEnd
			attributes.weightBlendAttr(Ctrl.passer, 'rx', 
					driverAttrs = ['{}.twistExctration'.format(ControlStart.name),
								   '{}.twistExctration'.format(ControlEnd.name)], 
					weightList = [weightStart, weightEnd])
			for axis in 'XYZ':
				attributes.weightBlendAttr(Ctrl.zero, 'translate{}'.format(axis), 
					driverAttrs = ['{}.outputTranslate{}'.format(decomposeStart, axis),
								   '{}.outputTranslate{}'.format(decomposeEnd, axis)], 
					weightList = [weightStart, weightEnd])

		self._controls.insert(0, ControlStart.name)
		self._controls.insert(1, ControlEnd.name)