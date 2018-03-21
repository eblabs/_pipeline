#####################################################
# base ik rp solver limb
# this limb should do the ik rpSolver rig functions
#####################################################
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
import riggingAPI.constraints as constraints

import riggingAPI.rigComponents.baseLimbs.baseJointsLimb as baseJointsLimb
## import rig utils
import riggingAPI.rigComponents.rigUtils.createDriveJoints as createDriveJoints
import riggingAPI.rigComponents.rigUtils.addTwistJoints as addTwistJoints

## kwarg class
class kwargsGenerator(baseJointsLimb.kwargsGenerator):
	"""docstring for kwargsGenerator"""
	def __init__(self):
		super(kwargsGenerator, self).__init__()
		self.dKwargs = {'lBpCtrls': None}
		self.addKwargs()

class baseIkRPsolverLimb(baseJointsLimb.baseJointsLimb):
	"""docstring for baseIkRPsolverLimb"""
	def __init__(self, *args, **kwargs):
		super(baseIkRPsolverLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpCtrls = kwargs.get('lBpCtrls', None)

	def createComponent(self):
		super(baseIkRPsolverLimb, self).createComponent()


		sParent_ctrl = self._sComponentControls

		## put ik joint chain locally
		sGrp_ikJnts = transforms.createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sRPJointsLocal' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld)
		sParent_jntLocal = sGrp_ikJnts
		lJntsLocal = []

		lJntsLocal, lBindJnts = createDriveJoints.createDriveJoints(self._lBpJnts, sParent = sGrp_ikJnts, sSuffix = 'IkRPLocal', bBind = False)
		lJnts, lBindJnts = createDriveJoints.createDriveJoints(self._lBpJnts, sParent = self._sComponentDrvJoints, sSuffix = 'IkRP', bBind = self._bBind)

		for i, sJntLocal in enumerate(lJntsLocal):
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.translate%s' %(sJntLocal, sAxis), '%s.translate%s' %(lJnts[i], sAxis))
				cmds.connectAttr('%s.rotate%s' %(sJntLocal, sAxis), '%s.rotate%s' %(lJnts[i], sAxis))
				cmds.connectAttr('%s.scale%s' %(sJntLocal, sAxis), '%s.scale%s' %(lJnts[i], sAxis))

		## ctrls
		lCtrls = []
		for i, sBpCtrl in enumerate(self._lBpCtrls):
			oJntName = naming.oName(sBpCtrl)
			iRotateOrder = cmds.getAttr('%s.ro' %sBpCtrl)
			if i != 2:
				lLockHideAttrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
			else:
				lLockHideAttrs = self._lLockHideAttrs
			oCtrl = controls.create(oJntName.sPart, sSide = oJntName.sSide, iIndex = oJntName.iIndex, iStacks = self._iStacks, bSub = True, sParent = self._sComponentControls, sPos = sBpCtrl, iRotateOrder = iRotateOrder, sShape = 'cube', fSize = 8, lLockHideAttrs = lLockHideAttrs)
			lCtrls.append(oCtrl.sName)

		## ik handle
		sIkHnd = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sRPsolver' %self._sName, iIndex = self._iIndex).sName
		cmds.ikHandle(sj = lJntsLocal[0], ee = lJntsLocal[-1], sol = 'ikRPsolver', name = sIkHnd)

		#### offset group
		sGrpIk = transforms.createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sRPsolver' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld, sPos = lCtrls[-1])
		sGrpPv = transforms.createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sPV' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld, sPos = lCtrls[1])
		cmds.parent(sIkHnd, sGrpIk)

		#### pole vector constraint
		cmds.poleVectorConstraint(sGrpPv, sIkHnd)
		#### pole vector line
		sCrv, lClsHnds = curves.createCurveLine(naming.oName(sType = 'curve', sSide = self._sSide, sPart = '%sPvLineIk' %self._sName, iIndex = self._iIndex).sName, [lJnts[1], lCtrls[1]], bConstraint = False)
		cmds.parent(lClsHnds, sCrv, self._sComponentControls)

		## pass info to class
		self._lJnts = lJnts
		self._lCtrls = lCtrls
		self._lBindJnts = lBindJnts
		self._sGrpIk = sGrpIk
		self._sIkHnd = sIkHnd
		self._lJntsLocal = lJntsLocal
		if lBindJnts:
			self._lBindRootJnts = [lBindJnts[0]]
		else:
			self._lBindRootJnts = None

		## matrix connect
		constraints.matrixConnect(lCtrls[0], [lJntsLocal[0]], 'matrixOutputWorld',lSkipRotate = ['X', 'Y', 'Z'], lSkipScale = ['X', 'Y', 'Z'], bForce = True)
		constraints.matrixConnect(lCtrls[1], [sGrpPv, lClsHnds[1]], 'matrixOutputWorld',lSkipRotate = ['X', 'Y', 'Z'], lSkipScale = ['X', 'Y', 'Z'], bForce = True)
		constraints.matrixConnect(lCtrls[2], [sGrpIk], 'matrixOutputWorld', lSkipScale = ['X', 'Y', 'Z'], bForce = True)
		sMultMatrixPv = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sPvMatrix' %self._sName, iIndex = self._iIndex).sName)
		cmds.connectAttr('%s.matrix' %lJnts[1], '%s.matrixIn[0]' %sMultMatrixPv)
		cmds.connectAttr('%s.matrix' %lJnts[0], '%s.matrixIn[1]' %sMultMatrixPv)
		constraints.matrixConnect(sMultMatrixPv, [lClsHnds[0]], 'matrixSum', lSkipRotate = ['X', 'Y', 'Z'], lSkipScale = ['X', 'Y', 'Z'], bForce = True)

		## write component info
		self._writeGeneralComponentInfo('baseFkChainLimb', lJnts, lCtrls, lBindJnts, self._lBindRootJnts)

		## output matrix
		if self._bInfo:
			self._writeOutputMatrixInfo(lJnts)

		## add twist joints
		addTwistJoints.twistJointsForLimb(self._iTwistJntNum, self._lSkipTwist, lJnts, self._lBpJnts, bBind = self._bBind, sNode = self._sComponentMaster, bInfo = self._bInfo)

		self._getComponentInfo(self._sComponentMaster)