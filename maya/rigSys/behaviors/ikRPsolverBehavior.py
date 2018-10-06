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
import lib.common.naming.naming as naming
import lib.common.naming.namingDict as namingDict
import lib.common.transforms as transforms
import lib.common.attributes as attributes
import lib.common.apiUtils as apiUtils
import lib.common.nodes as nodes
import lib.rigging.joints as joints
import lib.rigging.controls.controls as controls
import lib.rigging.constraints as constraints
import lib.modeling.curves as curves
# ---- import end ----

# ---- import components ----
import baseBehavior
# ---- import end ----

class IkRPsolverBehavior(baseBehavior.BaseBehavior):
	"""IkRPsolverBehavior template"""
	def __init__(self, **kwargs):
		super(IkRPsolverBehavior, self).__init__(**kwargs)
		self._ikHandles = []
		self._ikSolver = kwargs.get('ikSolver', 'ikRPsolver')
		self._blueprintControl = kwargs.get('blueprintControl', '')
		self._poleVectorDistance = kwargs.get('poleVectorDistance', 1)
		if self._ikSolver == 'ikRPsolver':
			self._jointSuffix = kwargs.get('jointSuffix', 'IkRP')
		elif self._ikSolver == 'ikSpringSolver':
			self._jointSuffix = kwargs.get('jointSuffix', 'IkSpring')
			mel.eval('ikSpringSolver')

	def create(self):
		super(IkRPsolverBehavior, self).create()

		# controls
		for i, bpCtrl in enumerate([self._blueprintJoints[0], self._blueprintJoints[1], self._blueprintControl]):
			NamingCtrl = naming.Naming(bpCtrl)
			partSuffix = ['Pos', 'Pv', ''][i]
			Control = controls.create(NamingCtrl.part + partSuffix + self._jointSuffix, side = NamingCtrl.side, 
				index = NamingCtrl.index, stacks = self._stacks, parent = self._controlsGrp, 
				posParent = bpCtrl, lockHide = ['sx', 'sy', 'sz'])
			self._controls.append(Control.name)

		# set ik solver
		ikHandle = naming.Naming(type = 'ikHandle', side = self._side, part = self._part + self._jointSuffix, index = self._index).name
		cmds.ikHandle(sj = self._joints[0], ee = self._joints[-1], sol = self._ikSolver, name = ikHandle)

		# check if flip for spring solver, seems like a maya bug
		if self._ikSolver == 'ikSpringSolver':
			cmds.refresh() # refresh maya to get correct joint value
			rx = cmds.getAttr('{}.rx'.format(self._joints[0]))
			if rx > 90 or rx < -90:
				# normally is 180 or -180
				for axis in 'XYZ':
					pos = cmds.getAttr('{}.poleVector{}'.format(ikHandle, axis))
					cmds.setAttr('{}.poleVector{}'.format(ikHandle, axis), -pos)

		# set pos for pv
		pvVec = []
		for axis in 'XYZ':
			pos = cmds.getAttr('{}.poleVector{}'.format(ikHandle, axis))
			pvVec.append(pos)
		posRoot = cmds.xform(self._joints[1], q = True, t = True, ws = True)
		posPv = apiUtils.getPointFromVector(posRoot, pvVec, distance = 3 * self._poleVectorDistance)

		ControlPv = controls.Control(self._controls[1])
		transforms.setNodePos(ControlPv.zero, posParent = [posPv, [0,0,0]])

		# add transfrom group to control ik (pv and ik ctrl)
		for ctrl in self._controls[1:]:
			Control = controls.Control(ctrl)
			NamingNode = naming.Naming(type = 'null', side = Control.side, part = Control.part, index = Control.index)
			node = transforms.createTransformNode(NamingNode.name, parent = self._nodesLocalGrp, posParent = ctrl,
												  lockHide=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
			constraints.matrixConnect(Control.name, Control.matrixWorldAttr, node, force = True, quatToEuler = False)
			self._nodesLocal.append(node)

		# parent ik to node
		cmds.parent(ikHandle, self._nodesLocal[-1])

		# pole vector constraint
		cmds.poleVectorConstraint(self._nodesLocal[0], ikHandle)

		# pole vector line
		crvLine = naming.Naming(type = 'crvLine', side = self._side, part = self._part + self._jointSuffix, index = self._index).name

		crvLine, clsHndList = curves.createCurveLine(crvLine, [self._controls[1], self._joints[1]])
		cmds.parent(crvLine, clsHndList, self._controlsGrp)

		# connect pole vector line
		constraints.matrixConnect(ControlPv.name, ControlPv.matrixWorldAttr, clsHndList[0], skipTranslate=None, 
								  skipRotate=['x', 'y', 'z'], skipScale=['x', 'y', 'z'])

		multMatrixPv = nodes.create(type = 'multMatrix', side = self._side, part = '{}PvCrvLine'.format(self._part + self._jointSuffix), index = self._index)
		attributes.connectAttrs(['{}.matrix'.format(self._joints[1]), '{}.matrix'.format(self._joints[0])],
								['matrixIn[0]', 'matrixIn[1]'], driven = multMatrixPv)
		constraints.matrixConnect(multMatrixPv, 'matrixSum', clsHndList[1], skipTranslate=None, 
								  skipRotate=['x', 'y', 'z'], skipScale=['x', 'y', 'z'])

		# connect root jnt with controller
		ControlRoot = controls.Control(self._controls[0])
		constraints.matrixConnect(ControlRoot.name, ControlRoot.matrixWorldAttr, self._joints[0], force = True, skipRotate = ['x', 'y', 'z'], 
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
			rvs = nodes.create(type = 'reverse', side = self._side, 
							   part = '{}AngleBias'.format(self._part + self._jointSuffix), 
							   index = self._index)
			cmds.connectAttr('{}.angleBias'.format(self._controls[-1]), '{}.inputX'.format(rvs))
			cmds.connectAttr('{}.outputX'.format(rvs), '{}.springAngleBias[1].springAngleBias_FloatValue'.format(ikHandle))

		# pass info
		self._ikHandles.append(ikHandle)
		self._crvLine = crvLine
