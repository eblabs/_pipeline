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
import rigSys.core.rigComponent as rigComponent
# -- import end ----

class IkRPsolverComponent(rigComponent.RigComponent):
	"""
	IkRPsolverComponent

	create base ik rp solver rig component

	"""
	def __init__(self, *args,**kwargs):
		super(IkRPsolverComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.modules.base.ikRPsolverComponent'
		if args:
			self._rigComponent = args[0]
			self._getRigComponentInfo()

	def create(self):
		super(IkRPsolverComponent, self).create()

		# create joints
		ikJnts = self.createJntsFromBpJnts(self._bpJnts, type = 'jnt', suffix = 'Ik', parent = self._jointsGrp)
		
		# create controls
		ikControls = []

		for bpCtrl in self._bpCtrls:
			NamingCtrl = naming.Naming(bpCtrl)
			ro = cmds.getAttr('{}.ro'.format(bpCtrl))
			Control = controls.create(NamingCtrl.part, side = NamingCtrl.side, index = NamingCtrl.index, 
				stacks = self._stacks, parent = self._controlsGrp, posParent = bpCtrl, rotateOrder = ro)
			ikControls.append(Control.name)

		# set ik solver
		ikHandle = naming.Naming(type = 'ikHandle', side = self._side, sPart = '%sIk' %self._part, iIndex = self._index).name
		cmds.ikHandle(sj = ikJnts[0], ee = ikJnts[-1], sol = 'ikRPsolver', name = ikHandle)

		# add transfrom group to control ik (pv and ik ctrl)
		nodes = []
		for ctrl in ikControls[1:]:
			Control = controls.Control(ctrl)
			NamingNode = naming.Naming(type = 'null', side = Control.side, part = Control.part, index = Control.index).name
			node = transforms.createTransformNode(NamingNode.name, parent = self._nodesLocal, posParent = ctrl,
												  lockHide=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
			constraints.matrixConnect(Control.name, matrixWorldAttr, node, force = True, quatToEuler = False)
			nodes.append(node)

		# parent ik to node
		cmds.parent(ikHandle, nodes[-1])

		# pole vector constraint
		cmds.poleVectorConstraint(nodes[0], ikHandle)

		# connect root jnt with controller
		constraints.matrixConnect(ikControls[0], matrixWorldAttr, ikJnts[0], force = True, skipRotate = ['x', 'y', 'z'], 
						  		  skipScale = ['x', 'y', 'z'])

		# connect tip jnt rotation with controller
		Control = controls.Control(ikControls[-1])

		multMatrix = naming.Naming(type = 'multMatrix', side = Control.side, part = '{}JntRot'.format(Control.part), index = Control.index).name
		cmds.createNode('multMatrix', name = multMatrix)

		matrixLocalJoint = transforms.getLocalMatrix(ikJnts[-1], Control.output)
		matrixLocalControl = transforms.getLocalMatrix(Control.output, ikJnts[-2])

		orient = joints.getJointOrient(ikJnts[-1])
		MMatrixOrient = apiUtils.composeMMatrix(rotate = orient)
		matrixOrientInverse = apiUtils.convertMMatrixToList(MMatrixOrient.inverse())

		attributes.setAttrs(['matrixIn[0]', 'matrixIn[2]', 'matrixIn[3]'], 
							[matrixLocalJoint, matrixLocalControl, matrixOrientInverse], 
							node = multMatrix, type = 'matrix')

		cmds.connectAttr(Control.matrixLocalPlug, '{}.matrixIn[1]'.format(multMatrix))
		constraints.matrixConnect(multMatrix, 'matrixSum', ikJnts[-1], force = True, skipTranslate = ['x', 'y', 'z'], 
						  		  skipScale = ['x', 'y', 'z'])

		# lock hide attrs
		for ctrl in ikControls[:-1]:
			Control = controls.Control(ctrl)
			Control.lockHideAttrs(['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

		# pass info
		self._joints += ikJnts
		self._controls += ikControls

		# write component info
		self._writeRigComponentType()
		self._writeJointsInfo()
		self._writeControlsInfo()