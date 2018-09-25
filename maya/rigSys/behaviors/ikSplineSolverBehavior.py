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
import baseBehavior

class IkSplineSolverBehavior(baseBehavior.BaseBehavior):
	"""IkSplineSolverBehavior template"""
	def __init__(self, **kwargs):
		super(IkSplineSolverBehavior, self).__init__(**kwargs)
		self._blueprintCurve = kwargs.get('blueprintCurve', '')
		self._jointSuffix = kwargs.get('jointSuffix', 'IkSpline')

	def create(self):
		super(IkSplineSolverBehavior, self).create()

		# generate curve
		self._curve = naming.Naming(type = 'curve', side = self._side, part = self._part + self._jointSuffix, index = self._index).name
		if not self._blueprintCurve:
			crv = curves.createCurveOnNodes(self._curve, self._joints, iDegree = 3, sParent = None)
			logger.WARN('Blueprint curve is not given, create curve base on joints')
		else:
			crv = cmds.duplicate(self._blueprintJoints, name = self._curve)[0]

		clsHndList = curves.clusterCurve(self._curve, bRelatives = True)
		
		# rebuild curve
		cvNum = curves.getCurveCvNum(self._curve)
		cmds.rebuildCurve(self._curve, ch = 1, rebuildType = 0, degree = 3, s = cvNum - 1, keepRange = 0, rpo = True)
		
		# set up ik and match joints to the curve
		self._ikHandle = naming.Naming(type = 'ikHandle', side = self._side, sPart = self._part + self._jointSuffix, iIndex = self._index).name
		cmds.ikHandle(sj = self._joints[0], ee = self._joints[-1], sol = 'ikSplineSolver', ccv = False, scv = False, curve = self._curve, name = self._ikHandle)
		cmds.makeIdentity(self._joints[0], apply = True, t = 1, r = 1, s = 1)

		# parent nodes
		cmds.parent(self._curve, clsHndList, self._nodesHideGrp)
		cmds.parent(self._ikHandle, self._nodesLocalGrp)

		# controls
		for i, clsHnd in enumerate(clsHndList):
			Control = controls.create(self._part + self._jointSuffix, side = NamingCtrl.side, index = NamingCtrl.index, 
				stacks = self._stacks, parent = self._controlsGrp, lockHideAttrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
			cmds.delete(cmds.pointConstraint(clsHnd, Control.zero, mo = False))
			constraints.matrixConnect(Control.name, Control.matrixWorldAttr, clsHnd, offset = True, skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'])
			self._controls.append(Control.name)

		# twist
		cmds.setAttr('{}.dTwistControlEnable'.format(self._ikHandle), 1)
		cmds.setAttr('{}.dWorldUpType'.format(self._ikHandle), 4)

		for i, ctrl in enumerate([self._controls[0], self._controls[-1]]):
			Control = controls.Control(ctrl)
			matrixLocal = transforms.getLocalMatrix([self._joints[0], self._joints[-1]][i], Control.output)
			multMatrix = cmds.createNode('multMatrix', name = naming.Naming(type = 'multMatrix', side = self._side, 
										 part = '{}Twist{}'.format(self._part + self._jointSuffix, ['Bot', 'Top'][i]), index = self._index).name)
			cmds.setAttr('{}.matrixIn[0]'.format(multMatrix), matrixLocal)
			cmds.connectAttr(Control.matrixWorldPlug, '{}.matrixIn[1]'.format(multMatrix))
			cmds.connectAttr('{}.matrixSum',format(multMatrix), '{}.{}'.format(self._ikHandle, ['dWorldUpMatrix', 'dWorldUpMatrixEnd'][i]))
