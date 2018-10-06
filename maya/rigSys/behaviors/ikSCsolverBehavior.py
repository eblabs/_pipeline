# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds
import maya.mel as mel
# -- import lib
import common.naming.naming as naming
import common.naming.namingDict as namingDict
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import rigging.joints as joints
import rigging.controls.controls as controls
import rigging.constraints as constraints
# ---- import end ----

# ---- import components ----
import baseBehavior
# ---- import end ----

class IkSCsolverBehavior(baseBehavior.BaseBehavior):
	"""IkSCsolverBehavior template"""
	def __init__(self, **kwargs):
		super(IkSCsolverBehavior, self).__init__(**kwargs)
		self._ikHandles = []
		self._jointSuffix = kwargs.get('jointSuffix', 'IkSC')

	def create(self):
		super(IkSCsolverBehavior, self).create()

		# create controls
		for i, bpCtrl in enumerate([self._joints[0], self._joints[-1]]):
			NamingCtrl = naming.Naming(self._joints[0])
			Control = controls.create(NamingCtrl.part + ['Root', 'Aim'][i], side = NamingCtrl.side, 
				index = NamingCtrl.index, stacks = self._stacks, parent = self._controlsGrp, posPoint = bpCtrl, 
				posOrient = self._joints[0], lockHide = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
			self._controls.append(Control.name)

		# set ik solver
		ikHandle = naming.Naming(type = 'ikHandle', side = self._side, sPart = self._part + self._jointSuffix, iIndex = self._index).name
		cmds.ikHandle(sj = self._joints[0], ee = self._joints[-1], sol = 'ikSCsolver', name = ikHandle)

		# add transfrom group to control ik
		Control = controls.Control(self._controls[-1])
		NamingNode = naming.Naming(type = 'null', side = Control.side, part = Control.part, index = Control.index)
		node = transforms.createTransformNode(NamingNode.name, parent = self._nodesLocalGrp, posParent = self._controls[-1],
												lockHide=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
		constraints.matrixConnect(Control.name, Control.matrixWorldAttr, node, force = True, quatToEuler = False)

		self._nodesLocal = [node]

		# parent ik to node
		cmds.parent(ikHandle, node)

		# connect root jnt with controller
		ControlRoot = controls.Control(self._controls[0])
		constraints.matrixConnect(ControlRoot.name, ControlRoot.matrixWorldAttr, self._joints[0], force = True, skipRotate = ['x', 'y', 'z'], 
						  		  skipScale = ['x', 'y', 'z'])

		# lock hide attrs
		Control = controls.Control(self._controls[-1])
		Control.unlockAttrs(['rx'])

		# pass info
		self._ikHandles.append(ikHandle)