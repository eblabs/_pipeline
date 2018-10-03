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
import common.hierarchy as hierarchy
import common.nodes as nodes
import rigging.controls.controls as controls
import rigging.constraints as constraints
# ---- import end ----

# -- import component
import ikRPsolverPlusComponent as ikRPsolverPlusComponent
import behaviors.ikRPsolverBehavior as ikRPsolverBehavior
# -- import end ----

class IkSpringSolverPlusComponent(ikRPsolverPlusComponent.IkRPsolverPlusComponent):
	"""
	IkSpringSolverPlusComponent

	create ik spring solver drive ik rp solver plus
	mainly used for quad leg

	"""
	def __init__(self, *args,**kwargs):
		super(IkSpringSolverPlusComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.components.advance.ikSpringSolverPlusComponent'

	def _registerDefaultKwargs(self):
		super(IkSpringSolverPlusComponent, self)._registerDefaultKwargs()
		kwargs = {'blueprintSpringPVControl': {'value': '', 'type': basestring}}
		self._kwargs.update(kwargs)
	def _createComponent(self):
		bpJntsSpring = self._blueprintJoints[:4]

		super(IkSpringSolverPlusComponent, self)._createComponent()

		# create ik spring solver chain
		bpCtrls = [self._blueprintControls[0],
				   self._blueprintSpringPVControl,
				   self._blueprintControls[-1]]

		kwargs = {'side': self._side,
				  'part': self._part,
				  'index': self._index,
				  'blueprintJoints': bpJntsSpring,
				  'stacks': self._stacks,
				  'blueprintControls': bpCtrls,
				  'ikSolver': 'ikSpringSolver',

				  'controlsGrp': self._controlsGrp,
				  'jointsGrp': self._jointsGrp,
				  'nodesLocalGrp': self._nodesLocalGrp,
				  'nodesHideGrp': self._nodesHideGrp,
				  'nodesShowGrp': self._nodesShowGrp}

		IkSpringSolverBehavior = ikRPsolverBehavior.IkRPsolverBehavior(**kwargs)
		IkSpringSolverBehavior.create()

		# parent spring controls under ik controls (except pv)
		controlList = [[IkSpringSolverBehavior._controls[0], self._ikControls[0]],
					   [IkSpringSolverBehavior._controls[-1], self._ikControls[-1]]]

		cmds.addAttr(self._ikControls[-1], ln = 'twistExtra', at = 'float', keyable = True)

		cmds.connectAttr('{}.twist'.format(self._ikControls[-1]), 
					'{}.twist'.format(IkSpringSolverBehavior._ikHandles[0]), f = True)
		cmds.connectAttr('{}.twistExtra'.format(self._ikControls[-1]),
					'{}.twist'.format(self._ikHandles[0]), f = True)

		for ctrls in controlList:
			ControlSpring = controls.Control(ctrls[0])
			ControlRp = controls.Control(ctrls[1])

			constraints.matrixConnect(ControlRp.name, ControlRp.matrixWorldAttr,
									  ControlSpring.zero, skipScale = ['x', 'y', 'z'])
			cmds.setAttr('{}.v'.format(ControlSpring.zero), 0)

			attributes.copyConnectAttrs(ctrls[1], ctrls[0])

		# control ik pv
		ControlRp = controls.Control(self._controls[1])
		multMatrix = nodes.create(type = 'multMatrix', side = ControlRp.side,
								  part = ControlRp.part + 'IkSpringDrive',
								  index = ControlRp.index)
		matrixLocal = transforms.getLocalMatrix(ControlRp.name, 
									IkSpringSolverBehavior._joints[1])
		cmds.setAttr('{}.matrixIn[0]'.format(multMatrix), matrixLocal, type = 'matrix')
		cmds.connectAttr('{}.matrix'.format(IkSpringSolverBehavior._joints[1]), 
						'{}.matrixIn[1]'.format(multMatrix))
		cmds.connectAttr('{}.matrix'.format(IkSpringSolverBehavior._joints[0]), 
						'{}.matrixIn[2]'.format(multMatrix))
		constraints.matrixConnect(multMatrix, 'matrixSum', ControlRp.zero, 
					skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'], force=True)

		attributes.addAttrs(IkSpringSolverBehavior._controls[1], 'extraPvControlVis', 
				attributeType='long', minValue=0, maxValue=1, defaultValue=0, 
				keyable=False, channelBox=True)

		attributes.connectAttrs('extraPvControlVis', 
								['{}.v'.format(ControlRp.zero), '{}.v'.format(self._crvLine)], 
								driver = IkSpringSolverBehavior._controls[1],)

		## create aim constraint to make ball roll control follow spring joints
		if self._reverseJoints:
			NamingNode = naming.Naming(self._reverseJoints[-1])
			NamingNode.type = 'grp'
			NamingNode.part = NamingNode.part + 'Aim'
			aimGrp = transforms.createTransformNode(NamingNode.name, parent = self._nodesLocalGrp, posParent = self._reverseJoints[-1])
			
			NamingNode.type = 'null'
			aimNode = transforms.createTransformNode(NamingNode.name, parent = aimGrp, posParent = self._reverseJoints[-1])

			txJnt = cmds.getAttr('{}.tx'.format(IkSpringSolverBehavior._joints[-2]))
			if txJnt >= 0:
				aimVec = [1, 0, 0]
			else:
				aimVec = [-1, 0, 0]

			NamingNode.type = 'multMatrix'
			multMatrixInput = nodes.create(name = NamingNode.name)
			cmds.connectAttr('{}.worldMatrix[0]'.format(IkSpringSolverBehavior._joints[-2]), '{}.matrixIn[0]'.format(multMatrixInput))
			cmds.connectAttr('{}.worldInverseMatrix[0]'.format(self._jointsGrp), '{}.matrixIn[1]'.format(multMatrixInput))

			NamingNode.part = NamingNode.part + 'Pos'
			multMatrixPos = nodes.create(name = NamingNode.name)
			cmds.connectAttr('{}.worldMatrix[0]'.format(IkSpringSolverBehavior._joints[-1]), '{}.matrixIn[0]'.format(multMatrixPos))
			cmds.connectAttr('{}.worldInverseMatrix[0]'.format(self._jointsGrp), '{}.matrixIn[1]'.format(multMatrixPos))

			constraints.matrixConnect(multMatrixPos, 'matrixSum', aimGrp, skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'], force=True)

			constraints.matrixAimConstraint('{}.matrixSum'.format(multMatrixInput), [aimNode], parent = aimNode, worldUpType='objectrotation', worldUpMatrix='{}.matrixSum'.format(multMatrixInput), aimVector=aimVec, upVector=[0,1,0])

			ControlBall = controls.Control(self._reverseControls[-1])
			for axis in 'xyz':
				cmds.connectAttr('{}.r{}'.format(aimNode, axis), '{}.r{}'.format(ControlBall.passer, axis))

		self._controls += IkSpringSolverBehavior._controls
		self._ikControls += IkSpringSolverBehavior._controls
		self._ikHandles += IkSpringSolverBehavior._ikHandles