########################################################
# base ik spline solver limb
# this limb should do the ik spline solver rig functions
########################################################
## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import riggingAPI.joints as joints
import riggingAPI.controls as controls
import modelingAPI.curves as curves

import riggingAPI.rigComponents.baseLimbs.baseJointsLimb as baseJointsLimb
## import rig utils
import riggingAPI.rigComponents.rigUtils.createDriveJoints as createDriveJoints

## kwarg class
class kwargsGenerator(baseJointsLimb.kwargsGenerator):
	"""docstring for kwargsGenerator"""
	def __init__(self):
		super(kwargsGenerator, self).__init__()
		self.dKwargs = {'sCrv': None}
		self.addKwargs()

class baseIkSplineSolverLimb(baseJointsLimb.baseJointsLimb):
	"""docstring for baseIkSplineSolverLimb"""
	def __init__(self, *args, **kwargs):
		super(baseIkSplineSolverLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._sBpCrv = kwargs.get('sBpCrv', None)
			

	def createComponent(self):
		super(baseIkSplineSolverLimb, self).createComponent()

		sParent_jntLocal = self._sComponentRigNodesWorld	
		lJntsLocal = []
		lJntsBindName = []

		lJntsLocal, lBindJnts = createDriveJoints.createDriveJoints(self._lBpJnts, sParent = self._sComponentRigNodesWorld, sSuffix = 'IkSplineLocal', bBind = False)

		## generate curve
		sCurve = naming.oName(sType = 'curve', sSide = self._sSide, sPart = '%sSplineSolver' %self._sName, iIndex = self._iIndex).sName
		if not self._sBpCrv:
			sCurve = curves.createCurveOnNodes(sCurve, lJntsLocal, iDegree = 3, sParent = None)
		else:
			sCurve = cmds.duplicate(self._sBpCrv, name = sCurve)[0]
		lClsHnds = curves.clusterCurve(sCurve, bRelatives = True)
		#### rebuild curve
		iCvs = curves.getCurveCvNum(sCurve)
		cmds.rebuildCurve(sCurve, ch = 1, rebuildType = 0, degree = 3, s = iCvs - 3, keepRange = 0, rpo = True)
		#### set up ik
		sIkHnd = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sIkSplineSolver' %self._sName, iIndex = self._iIndex).sName
		cmds.ikHandle(sj = lJntsLocal[0], ee = lJntsLocal[-1], sol = 'ikSplineSolver', ccv = False, scv = False, curve = sCurve, name = sIkHnd)
		cmds.makeIdentity(lJntsLocal[0], apply = True, t = 1, r = 1, s = 1)

		## spline joint and bind jnt
		lJnts, lBindJnts = createDriveJoints.createDriveJoints(lJntsLocal, sParent = self._sComponentDrvJoints, sSuffix = '', sRemove = 'Local', bBind = self._bBind, lBindNameOverride = self._lBpJnts)

		for i, sJntLocal in enumerate(lJntsLocal):
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.translate%s' %(sJntLocal, sAxis), '%s.translate%s' %(lJnts[i], sAxis))
				cmds.connectAttr('%s.rotate%s' %(sJntLocal, sAxis), '%s.rotate%s' %(lJnts[i], sAxis))
				cmds.connectAttr('%s.scale%s' %(sJntLocal, sAxis), '%s.scale%s' %(lJnts[i], sAxis))
		## rig setup
		cmds.parent(sCurve, lClsHnds, sIkHnd, self._sComponentRigNodesWorld)

		#### controls
		lCtrls = []
		for i, sClsHnd in enumerate(lClsHnds):
			oCtrl = controls.create('%sSplineSolver' %self._sName, sSide = self._sSide, iIndex = i + 1, iStacks = self._iStacks, bSub = True, sParent = self._sComponentControls, sPos = sClsHnd, sShape = 'cube', fSize = 4, lLockHideAttrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
			sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = self._sSide, sPart = '%sSplineSolver' %self._sName, iIndex = i).sName)
			cmds.connectAttr('%s.matrixOutputLocal' %oCtrl.sName, '%s.inputMatrix' %sDecomposeMatrix)
			cmds.connectAttr('%s.outputTranslate' %sDecomposeMatrix, '%s.t' %sClsHnd)
			lCtrls.append(oCtrl.sName)

		## pass info to class
		self._lJnts = lJnts
		self._lCtrls = lCtrls
		self._lBindJnts = lBindJnts
		self._sIkHnd = sIkHnd
		if lBindJnts:
			self._lBindRootJnts = [lBindJnts[0]]
		else:
			self._lBindRootJnts = None

		## write component info
		self._writeGeneralComponentInfo('baseIkSplineSolverLimb', lJnts, lCtrls, lBindJnts, self._lBindRootJnts)
		## output matrix
		if self._bInfo:
			self._writeOutputMatrixInfo(lJnts)

		self._getComponentInfo(self._sComponentMaster)

