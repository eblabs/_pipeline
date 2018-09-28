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
import common.nodes as nodes
import rigging.joints as joints
import baseBehavior

class IkRPsolverBehavior(baseBehavior.BaseBehavior):
	"""IkRPsolverBehavior template"""
	_ikHandles = []
	def __init__(self, **kwargs):
		super(IkRPsolverBehavior, self).__init__(**kwargs)
		self._ikSolver = kwargs.get('ikSolver', 'ikRPsolver')
		self._blueprintControls = kwargs.get('blueprintControls', '')
		if self._ikSolver == 'ikRPsolver':
			self._jointSuffix = kwargs.get('jointSuffix', 'IkRP')
		elif self._ikSolver == 'ikSpringSolver':
			self._jointSuffix = kwargs.get('jointSuffix', 'IkSpring')
			mel.eval('ikSpringSolver')

	def create(self):
		super(IkRPsolverBehavior, self).create()

		# controls
		for bpCtrl in self._blueprintControls:
			NamingCtrl = naming.Naming(bpCtrl)
			Control = controls.create(NamingCtrl.part, side = NamingCtrl.side, 
				index = NamingCtrl.index, stacks = self._stacks, parent = self._controlsGrp, 
				posParent = bpCtrl, lockHide = ['sx', 'sy', 'sz'])
			self._controls.append(Control.name)

		# set ik solver
		ikHandle = naming.Naming(type = 'ikHandle', side = self._side, sPart = self._part + self._jointSuffix, iIndex = self._index).name
		cmds.ikHandle(sj = self._joints[0], ee = self._joints[-1], sol = self._ikSolver, name = ikHandle)

		# add transfrom group to control ik (pv and ik ctrl)
		for ctrl in ikControls[1:]:
			Control = controls.Control(ctrl)
			NamingNode = naming.Naming(type = 'null', side = Control.side, part = Control.part, index = Control.index).name
			node = transforms.createTransformNode(NamingNode.name, parent = self._nodesLocalGrp, posParent = ctrl,
												  lockHide=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
			constraints.matrixConnect(Control.name, matrixWorldAttr, node, force = True, quatToEuler = False)
			self._nodesLocal.append(node)

		# parent ik to node
		cmds.parent(ikHandle, self._nodesLocal[-1])

		# pole vector constraint
		cmds.poleVectorConstraint(self._nodesLocal[0], ikHandle)

		# pole vector line
		crvLine = naming.Naming(type = 'crvLine', side = self._side, part = self._part, index = self._index).name
		crvLine, clsHndList = curves.createCurveLine(crvLine, [self._controls[1], self._joints[1]])
		cmds.parent(crvLine, clsHndList, self._controlsGrp)

		# connect pole vector line
		ControlPv = controls.Control(self._controls[1])
		constraints.matrixConnect(ControlPv.name, ControlPv.matrixWorldAttr, clsHndList[0], skipTranslate=None, 
								  skipRotate=['x', 'y', 'z'], skipScale=['x', 'y', 'z'])

		multMatrixPv = naming.Naming(type = 'multMatrix', side = self._side, part = '{}PvCrvLine'.format(self._part + self._jointSuffix), index = self._index).name
		attributes.connectAttrs(['{}.matrix'.format(self._joints[1]), '{}.matrix'.format(self._joints[0])],
								['matrixIn[0]', 'matrixIn[1]'], driven = multMatrixPv)
		constraints.matrixConnect(multMatrixPv, 'matrixSum', clsHndList[1], skipTranslate=None, 
								  skipRotate=['x', 'y', 'z'], skipScale=['x', 'y', 'z'])

		# connect root jnt with controller
		constraints.matrixConnect(self._controls[0], matrixWorldAttr, self._joints[0], force = True, skipRotate = ['x', 'y', 'z'], 
						  		  skipScale = ['x', 'y', 'z'])

		# connect twist attr
		cmds.addAttr(self._controls[-1], ln = 'twist', at = 'float', dv = 0, keyable = True)
		cmds.connectAttr('{}.twist'.format(self._controls[-1]), '{}.twist'.format(ikHandle))

		# lock hide attrs
		for ctrl in self._controls[:-1]:
			Control = controls.Control(ctrl)
			Control.lockHideAttrs(['rx', 'ry', 'rz'])

		# angle bias if ik spring solver
		if self._ikSolver == 'ikSpringSolver':
			cmds.addAttr(self._controls[-1], ln = 'angleBias', min = 0, max = 1, dv = 0.5, at = 'float', keyable = True)
			cmds.connectAttr('{}.angleBias'.format(self._controls[-1]), '{}.springAngleBias[0].springAngleBias_FloatValue'.format(ikHandle))
			rvs = nodes.create(type = 'reverse', side = self._sSide, 
							   part = '{}AngleBias'.format(self._part + self._jointSuffix), 
							   index = self._index)
			cmds.connectAttr('{}.angleBias'.format(self._controls[-1]), '{}.inputX'.format(rvs))
			cmds.connectAttr('{}.outputX'.format(rvs), '{}.springAngleBias[1].springAngleBias_FloatValue'.format(ikHandle))

		# pass info
		self._ikHandles.append(ikHandle)
