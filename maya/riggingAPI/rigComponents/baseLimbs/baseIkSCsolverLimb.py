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

import riggingAPI.rigComponents.baseComponent as baseComponent

class baseIkSCsolverLimb(baseComponent.baseComponent):
	"""docstring for baseIkSCsolverLimb"""
	def __init__(self, *args, **kwargs):
		super(baseIkSCsolverLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpJnts = kwargs.get('lBpJnts', None)
			self._iStacks = kwargs.get('iStacks', 1)
			self._lLockHideAttrs = kwargs.get('lLockHideAttrs', ['sx', 'sy', 'sz', 'v'])
			self._bBind = kwargs.get('bBind', False)
	
	def createComponent(self):
		super(baseIkRPsolverLimb, self).createComponent()

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

		for i, sBpJnt in enumerate(self._lBpJnts):
			## jnt
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			oJntName.sPart = '%sIkSC' %oJntName.sPart
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			sParent_jnt = sJnt
			lJnts.append(sJnt)

			sJntLocal = joints.createJntOnExistingNode(sJnt, 'IkSC', 'IkSCLocal', sParent = sParent_jntLocal)
			sParent_jntLocal = sJntLocal
			lJntsLocal.append(sJntLocal)
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.translate%s' %(sJntLocal, sAxis), '%s.translate%s' %(sJnt, sAxis))
				cmds.connectAttr('%s.rotate%s' %(sJntLocal, sAxis), '%s.rotate%s' %(sJnt, sAxis))
				cmds.connectAttr('%s.scale%s' %(sJntLocal, sAxis), '%s.scale%s' %(sJnt, sAxis))

			## bind jnt
			if self._bBind:
				oJntName.sType = 'bindJoint'
				sBindJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_bind)
				sParent_bind = sBindJnt
				lBindJnts.append(sBindJnt)
				for sAxis in ['X', 'Y', 'Z']:
					cmds.connectAttr('%s.translate%s' %(sJnt, sAxis), '%s.translate%s' %(sBindJnt, sAxis))
					cmds.connectAttr('%s.rotate%s' %(sJnt, sAxis), '%s.rotate%s' %(sBindJnt, sAxis))
					cmds.connectAttr('%s.scale%s' %(sJnt, sAxis), '%s.scale%s' %(sBindJnt, sAxis))

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
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, 'baseIkSCsolcerLimb', type = 'string', lock = True)
		cmds.setAttr('%s.iJointCount' %self._sComponentMaster, len(lJnts), lock = True)
		sControlsString = ''
		for sCtrl in lCtrls:
			sControlsString += '%s,' %sCtrl
		cmds.setAttr('%s.sControls' %self._sComponentMaster, sControlsString[:-1], type = 'string', lock = True)
		if self._bBind:
			sBindString = ''
			for sBind in lBindJnts:
				sBindString += '%s,' %sBind
			cmds.setAttr('%s.sBindJoints' %self._sComponentMaster, sBindString[:-1], type = 'string', lock = True)

		## output matrix
		self._writeOutputMatrixInfo(lJnts, bHierarchy = True)

		self._getComponentInfo(self._sComponentMaster)