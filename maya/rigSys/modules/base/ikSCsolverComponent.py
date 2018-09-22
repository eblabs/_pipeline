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
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import rigging.control.controls as controls
import rigging.constraints as constraints
# ---- import end ----

# -- import component
import rigSys.core.ikSolverComponent as ikSolverComponent
# -- import end ----

class IkSCsolverComponent(ikSolverComponent.IkSolverComponent):
	"""
	IkSCsolverComponent

	create base ik sc solver rig component

	"""
	def __init__(self, *args,**kwargs):
		super(IkSCsolverComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.modules.base.ikSCsolverComponent'

		kwargsDefault = {'blueprintControls': {'value': [],
						 					   'type': 'list'}}
		self._registerAttributes(kwargsDefault)

	def _createRigComponent(self):
		super(IkSCsolverComponent, self)._createRigComponent()

		# create joints
		ikJnts = self.createJntsFromBpJnts(self._blueprintJoints, type = 'jnt', suffix = 'Ik', parent = self._jointsGrp)
		
		# create controls
		ikControls = []

		for i, bpCtrl in enumerate([self._blueprintJoints[0], self._blueprintJoints[-1]]):
			NamingCtrl = naming.Naming(bpCtrl)
			ro = cmds.getAttr('{}.ro'.format(bpCtrl))
			Control = controls.create('{}Ik{}'.format(NamingCtrl.part, ['Root', 'Aim'][i]), side = NamingCtrl.side, index = NamingCtrl.index, 
				stacks = self._stacks, parent = self._controlsGrp, posPoint = bpCtrl, posOrient = self._blueprintJoints[0], rotateOrder = ro,
				lockHide = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
			ikControls.append(Control.name)

		# set ik solver
		ikHandle = naming.Naming(type = 'ikHandle', side = self._side, sPart = '{}Ik'.format(self._part), iIndex = self._index).name
		cmds.ikHandle(sj = ikJnts[0], ee = ikJnts[-1], sol = 'ikSCsolver', name = ikHandle)

		# add transfrom group to control ik
		Control = controls.Control(ikControls[-1])
		NamingNode = naming.Naming(type = 'null', side = Control.side, part = Control.part, index = Control.index).name
		node = transforms.createTransformNode(NamingNode.name, parent = self._nodesLocal, posParent = ikControls[-1],
												lockHide=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
		constraints.matrixConnect(Control.name, matrixWorldAttr, node, force = True, quatToEuler = False)

		# parent ik to node
		cmds.parent(ikHandle, node)

		# connect root jnt with controller
		constraints.matrixConnect(ikControls[0], matrixWorldAttr, ikJnts[0], force = True, skipRotate = ['x', 'y', 'z'], 
						  		  skipScale = ['x', 'y', 'z'])

		# lock hide attrs
		Control = controls.Control(ikControls[-1])
		Control.unlockAttrs(['rx'])

		# pass info
		self._joints += ikJnts
		self._controls += ikControls
		self._ikHandles = [ikHandle]
		self._ikControls = self._controls