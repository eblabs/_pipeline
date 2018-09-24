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

class IkRPsolverComponent(ikSolverComponent.IkSolverComponent):
	"""
	IkRPsolverComponent

	create base ik rp solver rig component

	"""
	def __init__(self, *args,**kwargs):
		super(IkRPsolverComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.modules.base.ikRPsolverComponent'

		kwargsDefault = {'blueprintControls': {'value': [],
						 					   'type': list},
						 'ikSolver': {'value': 'ikRPsolver',
						 			  'type': basestring}}
		self._registerAttributes(kwargsDefault)

	def _createComponent(self):
		super(IkRPsolverComponent, self)._createComponent()

		if self._ikSolver == 'ikRPsolver':
			suffix = 'IKRP'
		elif self._ikSolver == 'ikSpringSolver':
			mel.eval('ikSpringSolver')
			suffix = 'IKSpring'

		# create joints
		ikJnts = self.createJntsFromBpJnts(self._blueprintJoints, type = 'jnt', suffix = suffix, parent = self._jointsGrp)
		
		# create controls
		ikControls = []

		for bpCtrl in self._blueprintControls:
			NamingCtrl = naming.Naming(bpCtrl)
			ro = cmds.getAttr('{}.ro'.format(bpCtrl))
			Control = controls.create(NamingCtrl.part, side = NamingCtrl.side, index = NamingCtrl.index, 
				stacks = self._stacks, parent = self._controlsGrp, posParent = bpCtrl, rotateOrder = ro,
				lockHide = ['sx', 'sy', 'sz'])
			ikControls.append(Control.name)

		# set ik solver
		ikHandle = naming.Naming(type = 'ikHandle', side = self._side, sPart = self._part + suffix, iIndex = self._index).name
		cmds.ikHandle(sj = ikJnts[0], ee = ikJnts[-1], sol = self._ikSolver, name = ikHandle)

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

		# pole vector line
		crvLine = naming.Naming(type = 'crvLine', side = self._side, part = self._part, index = self._index).name
		crvLine, clsHndList = curves.createCurveLine(crvLine, [ikControls[1], ikJnts[1]])
		cmds.parent(crvLine, self._controlsGrp)

		# connect pole vector line
		ControlPv = controls.Control(ikControls[1])
		constraints.matrixConnect(ControlPv.name, ControlPv.matrixWorldAttr, clsHndList[0], skipTranslate=None, 
								  skipRotate=['x', 'y', 'z'], skipScale=['x', 'y', 'z'])

		multMatrixPv = naming.Naming(type = 'multMatrix', side = self._side, part = '{}PvCrvLine'.format(self._part), index = self._index).name
		attributes.connectAttrs(['{}.matrix'.format(ikJnts[1]), '{}.matrix'.format(ikJnts[0])],
								['matrixIn[0]', 'matrixIn[1]'], driven = multMatrixPv)
		constraints.matrixConnect(multMatrixPv, 'matrixSum', clsHndList[1], skipTranslate=None, 
								  skipRotate=['x', 'y', 'z'], skipScale=['x', 'y', 'z'])

		# connect root jnt with controller
		constraints.matrixConnect(ikControls[0], matrixWorldAttr, ikJnts[0], force = True, skipRotate = ['x', 'y', 'z'], 
						  		  skipScale = ['x', 'y', 'z'])

		# connect twist attr
		cmds.addAttr(ikControls[-1], ln = 'twist', at = 'float', dv = 0, keyable = True)
		cmds.connectAttr('{}.twist'.format(ikControls[-1]), '{}.twist'.format(ikHandle))

		# lock hide attrs
		for ctrl in ikControls[:-1]:
			Control = controls.Control(ctrl)
			Control.lockHideAttrs(['rx', 'ry', 'rz'])

		# angle bias if ik spring solver
		if self._ikSolver == 'ikSpringSolver':
			cmds.addAttr(ikControls[-1], ln = 'angleBias', min = 0, max = 1, dv = 0.5, at = 'float', keyable = True)
			cmds.connectAttr('{}.angleBias'.format(ikControls[-1]), '{}.springAngleBias[0].springAngleBias_FloatValue'.format(ikHandle))
			rvs = cmds.createNode('reverse', name = naming.Naming(type = 'reverse', side = self._sSide, 
									part = '{}IkSpringAngleBias'.format(self._part), index = self._index).name)
			cmds.connectAttr('{}.angleBias'.format(ikControls[-1]), '{}.inputX'.format(rvs))
			cmds.connectAttr('{}.outputX'.format(rvs), '{}.springAngleBias[1].springAngleBias_FloatValue'.format(ikHandle))

		# pass info
		self._joints += ikJnts
		self._controls += ikControls
		self._ikHandles = [ikHandle]
		self._ikControls = self._controls

	def _writeRigComponentInfo(self):
		super(IkRPsolverPlusComponent, self)._writeRigComponentInfo()

		# ikHandle type
		self._addStringAttr('ikSolver', self._ikSolver)

	def _getRigComponentInfo(self):
		super(IkRPsolverPlusComponent, self)._getRigComponentInfo()

		# get reverse controls
		self._ikSolver = cmds.getAttr('{}.ikSolver'.format(self._rigComponent))




