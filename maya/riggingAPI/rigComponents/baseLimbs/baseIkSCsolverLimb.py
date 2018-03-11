#####################################################
# base ik sc solver limb
# this limb should do the ik scSolver rig functions
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

import riggingAPI.rigComponents.baseLimb.baseJointsLimb as baseJointsLimb
## import rig utils
import riggingAPI.rigComponents.rigUtils.createDriveJoints as createDriveJoints
import riggingAPI.rigComponents.rigUtils.addTwistJoints as addTwistJoints

class baseIkSCsolverLimb(baseJointsLimb.baseJointsLimb):
	"""docstring for baseIkSCsolverLimb"""
	def __init__(self, *args, **kwargs):
		super(baseIkSCsolverLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
	
	def createComponent(self):
		super(baseIkSCsolverLimb, self).createComponent()

		sParent_jnt = self._sComponentDrvJoints
		sParent_ctrl = self._sComponentControls
		sParent_bind = self._sComponentBindJoints
		lJnts = []
		lCtrls = []
		lBindJnts = []

		## put ik joint chain locally
		sGrp_ikJnts = transforms.createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sSCJointsLocal' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld)
		sParent_jntLocal = sGrp_ikJnts
		lJntsLocal = []

		lJntsLocal, lBindJnts = createDriveJoints.createDriveJoints(self._lBpJnts, sParent = sGrp_ikJnts, sSuffix = 'IkSCLocal', bBind = False)
		lJnts, lBindJnts = createDriveJoints.createDriveJoints(self._lBpJnts, sParent = self._sComponentDrvJoints, sSuffix = 'IkSC', bBind = self._bBind, sBindParent = self._sComponentBindJoints)

		for i, sJnt in enumerate(self._lJntsLocal):
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.translate%s' %(sJntLocal, sAxis), '%s.translate%s' %(lJnts[i], sAxis))
				cmds.connectAttr('%s.rotate%s' %(sJntLocal, sAxis), '%s.rotate%s' %(lJnts[i], sAxis))
				cmds.connectAttr('%s.scale%s' %(sJntLocal, sAxis), '%s.scale%s' %(lJnts[i], sAxis))

		## ik handles
		sIkHnd = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sSCsolver' %self._sName, iIndex = self._iIndex).sName
		cmds.ikHandle(sj = lJntsLocal[0], ee = lJntsLocal[-1], sol = 'ikSCsolver', name = sIkHnd)

		## controls
		oCtrlRoot = controls.create('%sRoot' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, sParent = self._sComponentControls, sPos = lJnts[0], sShape = 'cube', fSize = 8, lLockHideAttrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
		lCtrls.append(oCtrlRoot.sName)
		oCtrlAim = controls.create('%sAim' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, sParent = self._sComponentControls, sPos = lJnts[-1], sShape = 'cube', fSize = 8, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		lCtrls.append(oCtrlAim.sName)

		#### offset group
		sGrpIk = createTransformNode(naming.oName(sType = 'group', sSide = oJntNameParent.sSide, sPart = oJntNameParent.sPart, iIndex = oJntNameParent.iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld, sPos = oCtrlAim.sName)
		cmds.parent(sIkHnd, sGrpIk)

		#### matrix connect
		constraints.matrixConnect(oCtrlAim.sName, [sGrpIk], 'matrixOutputWorld', lSkipScale = ['X', 'Y', 'Z'], bForce = True)
		constraints.matrixConnect(oCtrlRoot.sName, [lJnts[0]], 'matrixOutputWorld',lSkipRotate = ['X', 'Y', 'Z'], lSkipScale = ['X', 'Y', 'Z'], bForce = True)

		## pass info to class
		self._lJnts = lJnts
		self._lCtrls = lCtrls
		self._lBindJnts = lBindJnts
		self._sGrpIk = sGrpIk
		self._sIkHnd = sIkHnd
		self._lJntslocal = lJntsLocal

		## write component info
		self._writeGeneralComponentInfo('baseIkSCsolcerLimb', lJnts, lCtrls, lBindJnts)

		## output matrix
		if self._bInfo:
			self._writeOutputMatrixInfo(lJnts)

		## add twist joints
		addTwistJoints.twistJointsForLimb(self._iTwistJntNum, self._lSkipTwist, lJnts, self._lBpJnts, bBind = self._bBind, sNode = self._sComponentMaster, bInfo = self._bInfo)

		self._getComponentInfo(self._sComponentMaster)