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

class IkSplineSolverComponent(ikSolverComponent.IkSolverComponent):
	"""
	IkSplineSolverComponent

	create base ik spline solver rig component

	"""
	def __init__(self, *args,**kwargs):
		super(IkSplineSolverComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.modules.base.ikSplineSolverComponent'

		kwargsDefault = {'blueprintCurve': {'value': '', 'type': 'basestring'}}
		self._registerAttributes(kwargsDefault)

	def _createRigComponent(self):
		super(IkSCsolverComponent, self)._createRigComponent()

		# create joints
		ikJnts = self.createJntsFromBpJnts(self._blueprintJoints, type = 'jnt', suffix = 'Ik', parent = self._jointsGrp)
		
		# generate curve
		crv = naming.Naming(type = 'curve', side = self._side, part = '{}IkSpline'.format(self._part), index = self._index).name
		if not self._blueprintCurve:
			crv = curves.createCurveOnNodes(crv, ikJnts, iDegree = 3, sParent = None)
			logger.WARN('Blueprint curve is not given, create curve base on joints')
		else:
			crv = cmds.duplicate(self._blueprintJoints, name = crv)[0]

		clsHndList = curves.clusterCurve(crv, bRelatives = True)
		
		# rebuild curve
		cvNum = curves.getCurveCvNum(crv)
		cmds.rebuildCurve(crv, ch = 1, rebuildType = 0, degree = 3, s = cvNum - 1, keepRange = 0, rpo = True)
		
		# set up ik and match joints to the curve
		ikHandle = naming.Naming(type = 'ikHandle', side = self._side, sPart = '{}IkSpline'.format(self._part), iIndex = self._index).name
		cmds.ikHandle(sj = ikJnts[0], ee = ikJnts[-1], sol = 'ikSplineSolver', ccv = False, scv = False, curve = crv, name = ikHandle)
		cmds.makeIdentity(ikJnts[0], apply = True, t = 1, r = 1, s = 1)

		# parent nodes
		cmds.parent(curve, clsHndList, self._nodesHide)
		cmds.parent(ikHandle, self._nodesLocal)

		# controls
		ikControls = []
		for i, clsHnd in enumerate(clsHndList):
			Control = controls.create('{}Ik'.format(self._part), side = NamingCtrl.side, index = NamingCtrl.index, 
				stacks = self._stacks, parent = self._controlsGrp, lockHideAttrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
			cmds.delete(cmds.pointConstraint(clsHnd, Control.zero, mo = False))
			constraints.matrixConnect(Control.name, Control.matrixWorldAttr, clsHnd, offset = True, skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'])
			ikControls.append(Control.name)

		# twist
		cmds.setAttr('{}.dTwistControlEnable'.format(ikHandle), 1)
		cmds.setAttr('{}.dWorldUpType'.format(ikHandle), 4)

		for i, ctrl in enumerate([ikControls[0], ikControls[-1]]):
			Control = controls.Control(ctrl)
			matrixLocal = transforms.getLocalMatrix([ikJnts[0], ikJnts[-1]][i], Control.output)
			multMatrix = cmds.createNode('multMatrix', name = naming.Naming(type = 'multMatrix', side = self._side, 
										 part = '{}Twist{}'.format(self._part, ['Bot', 'Top'][i]), index = self._index).name)
			cmds.setAttr('{}.matrixIn[0]'.format(multMatrix), matrixLocal)
			cmds.connectAttr(Control.matrixWorldPlug, '{}.matrixIn[1]'.format(multMatrix))
			cmds.connectAttr('{}.matrixSum',format(multMatrix), '{}.{}'.format(ikHandle, ['dWorldUpMatrix', 'dWorldUpMatrixEnd'][i]))

		# pass info
		self._joints += ikJnts
		self._controls += ikControls
		self._ikHandles = [ikHandle]
		self._ikControls = self._controls