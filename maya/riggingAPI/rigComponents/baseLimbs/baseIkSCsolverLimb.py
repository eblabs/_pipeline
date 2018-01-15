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

class baseIkSCsolcerLimb(baseComponent.baseComponent):
	"""docstring for baseIkSCsolcerLimb"""
	def __init__(self, *args, **kwargs):
		super(baseIkSCsolcerLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpJnts = kwargs.get('lBpJnts', None)
			self._iStacks = kwargs.get('iStacks', 1)
			self._lLockHideAttrs = kwargs.get('lLockHideAttrs', ['sx', 'sy', 'sz', 'v'])
			self._bBind = kwargs.get('bBind', False)
	
	def createComponent(self):
		super(baseIkRPsolcerLimb, self).createComponent()

		sParent_jnt = self._sComponentDrvJoints
		sParent_ctrl = self._sComponentControls
		sParent_bind = self._sComponentBindJoints
		lJnts = []
		lCtrls = []
		lBindJnts = []

		for i, sBpJnt in enumerate(self._lBpJnts):
			## jnt
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			oJntName.sPart = '%sIkSC' %oJntName.sPart
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			sParent_jnt = sJnt
			lJnts.append(sJnt)

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

		## ctrls
		oCtrlRoot = controls.create('%sRoot' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, sParent = self._sComponentControls, sPos = self._lBpJnts[0], sShape = 'cube', fSize = 8, lLockHideAttrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
		oCtrlAim = controls.create('%sAim' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, sParent = self._sComponentControls, sPos = self._lBpJnts[0], sShape = 'cube', fSize = 8, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		lCtrls.append(oCtrlRoot.sName)
		lCtrls.append(oCtrlAim.sName)

		## ik handle
		sIkHnd = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sSCsolver' %self._sName, iIndex = self._iIndex).sName
		cmds.ikHandle(sj = lJnts[0], ee = lJnts[-1], sol = 'ikSCsolver', name = sIkHnd)

		#### offset group
		sGrpIk = createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sSCsolver' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesLocal, sPos = lCtrls[-1])
		cmds.parent(sIkHnd, sGrpIk)

		## matrix connect
		constraints.matrixConnect(lCtrls[0], [lJnts[0]], 'matrixOutputWorld',lSkipRotate = ['X', 'Y', 'Z'], lSkipScale = ['X', 'Y', 'Z'], bForce = True)
		constraints.matrixConnect(lCtrls[1], [sGrpPv], 'matrixOutputWorld', lSkipScale = ['X', 'Y', 'Z'], bForce = True)
		
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