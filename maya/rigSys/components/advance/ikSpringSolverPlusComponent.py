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
import rigging.control.controls as controls
import rigging.constraints as constraints
# ---- import end ----

# -- import component
import ikRPsolverPlusComponent as ikRPsolverPlusComponent
import rigSys.behaviors.ikRPsolverBehavior as ikRPsolverBehavior
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

		self._removeAttributes('ikSolver')

	def _createComponent(self):
		bpJntsSpring = self._blueprintJoints[:4]

		super(IkSpringSolverPlusComponent, self)._createComponent()

		# create ik spring solver chain
		kwargs = {'side': self._side,
				  'part': self._part,
				  'index': self._index,
				  'blueprintJoints': bpJntsSpring,
				  'stacks': self._stacks,
				  'blueprintControls': self._blueprintControls,
				  'ikSolver': 'ikSpringSolver',

				  'controlsGrp': self._controlsGrp,
				  'jointsGrp': self._jointsGrp,
				  'nodesLocalGrp': self._nodesLocalGrp,
				  'nodesHideGrp': self._nodesHideGrp,
				  'nodesShowGrp': self._nodesShowGrp}

		IkSpringSolverBehavior = ikRPsolverBehavior.IkRPsolverBehavior(**kwargs)
		IkSpringSolverBehavior.create()

		self._controls += IkSpringSolverBehavior._controls
		self._ikControls += IkSpringSolverBehavior._controls
		self._ikHandles += IkSpringSolverBehavior._ikHandles

		for controls in zip(IkSpringSolverBehavior._controls, self._ikControls):
			ControlSpring = controls.Control(controls[0])
			ControlRp = controls.Control(controls[1])

			cmds.parent(ControlRp.zero, ControlSpring.output)

			attributes.addAttrs(controls[0], 'ikRpControlVis', 
				attributeType='long', minValue=0, maxValue=1, defaultValue=0, 
				keyable=False, channelBox=True)
			cmds.connectAttr('{}.ikRpControlVis'.format(controls[0]), '{}.v'.format(ControlRp.zero))

			attributes.copyConnectAttrs(controls[0], controls[1])

		## create aim constraint to make ball roll control follow spring joints
		if self._reverseJoints:
			NamingNode = naming.Naming(self._reverseJoints[-1])
			NamingNode.type = 'grp'
			NamingNode.part = NamingNode.part + 'Aim'
			aimGrp = createTransformNode(NamingNode.name, parent = self._nodesLocalGrp, posParent = self._reverseJoints[-1])
			
			NamingNode.type = 'null'
			aimNode = createTransformNode(NamingNode.name, parent = aimGrp, posParent = self._reverseJoints[-1])

			txJnt = cmds.getAttr('{}.tx'.format(IkSpringSolverBehavior._joints[-2]))
			if txJnt >= 0:
				aimVec = [1, 0, 0]
			else:
				aimVec = [-1, 0, 0]

			NamingNode.type = 'multMatrix'
			multMatrixInput = nodes.create(NamingNode.name)
			cmds.connectAttr('{}.worldMatrix[0]'.format(IkSpringSolverBehavior._joints[-2]), '{}.matrixIn[0]'.format(multMatrixInput))
			cmds.connectAttr('{}.worldInverseMatrix[0]'.format(self._jointsGrp), '{}.matrixIn[1]'.format(multMatrixInput))

			NamingNode.part = NamingNode.part + 'Pos'
			multMatrixPos = nodes.create(NamingNode.name)
			cmds.connectAttr('{}.worldMatrix[0]'.format(IkSpringSolverBehavior._joints[-1]), '{}.matrixIn[0]'.format(multMatrixPos))
			cmds.connectAttr('{}.worldInverseMatrix[0]'.format(self._jointsGrp), '{}.matrixIn[1]'.format(multMatrixPos))

			constraints.matrixConnect(multMatrixPos, 'matrixSum', aimGrp, skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'], force=True)

			constraints.matrixAimConstraint(multMatrixInput, [aimNull], worldUpType='objectrotation', worldUpMatrix=multMatrixInput, aimVector=aimVector, upVector=[0,1,0])

			ControlBall = controls.Control(self._reverseControls[-1])
			for axis in 'xyz':
				cmds.connectAttr('{}.r{}'.format(aimNull, axis), '{}.r{}'.format(ControlBall.passer, axis))

