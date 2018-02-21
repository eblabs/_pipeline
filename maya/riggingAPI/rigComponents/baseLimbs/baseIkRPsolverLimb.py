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

import riggingAPI.rigComponents.baseComponent as baseComponent

class baseIkRPsolverLimb(baseComponent.baseComponent):
	"""docstring for baseIkRPsolverLimb"""
	def __init__(self, *args, **kwargs):
		super(baseIkRPsolverLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpJnts = kwargs.get('lBpJnts', None)
			self._iStacks = kwargs.get('iStacks', 1)
			self._lLockHideAttrs = kwargs.get('lLockHideAttrs', ['sx', 'sy', 'sz', 'v'])
			self._bBind = kwargs.get('bBind', False)
			self._lBpCtrls = kwargs.get('lBpCtrls', None)

	def createComponent(self):
		super(baseIkRPsolverLimb, self).createComponent()

		sParent_jnt = self._sComponentDrvJoints
		sParent_ctrl = self._sComponentControls
		sParent_bind = self._sComponentBindJoints
		lJnts = []
		lCtrls = []
		lBindJnts = []

		## put ik joint chain locally
		sGrp_ikJnts = transforms.createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sRPJointsLocal' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld)
		sParent_jntLocal = sGrp_ikJnts
		lJntsLocal = []

		for i, sBpJnt in enumerate(self._lBpJnts):
			## jnt
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			oJntName.sPart = '%sIkRP' %oJntName.sPart
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			sParent_jnt = sJnt
			lJnts.append(sJnt)

			sJntLocal = joints.createJntOnExistingNode(sJnt, 'IkRP', 'IkRPLocal', sParent = sParent_jntLocal)
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

		## ctrls
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
		sGrpIk = createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sRPsolver' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld, sPos = lCtrls[-1])
		sGrpPv = createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sPV' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld, sPos = lCtrls[1])
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

		## matrix connect
		constraints.matrixConnect(lCtrls[0], [lJnts[0]], 'matrixOutputWorld',lSkipRotate = ['X', 'Y', 'Z'], lSkipScale = ['X', 'Y', 'Z'], bForce = True)
		constraints.matrixConnect(lCtrls[1], [sGrpPv, lClsHnds[1]], 'matrixOutputWorld',lSkipRotate = ['X', 'Y', 'Z'], lSkipScale = ['X', 'Y', 'Z'], bForce = True)
		constraints.matrixConnect(lCtrls[2], [sGrpIk], 'matrixOutputWorld', lSkipScale = ['X', 'Y', 'Z'], bForce = True)
		sMultMatrixPv = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sPvMatrix' %self._sName, iIndex = self._iIndex).sName)
		cmds.connectAttr('%s.matrix' %lJnts[1], '%s.matrixIn[0]' %sMultMatrixPv)
		cmds.connectAttr('%s.matrix' %lJnts[0], '%s.matrixIn[1]' %sMultMatrixPv)
		constraints.matrixConnect(sMultMatrixPv, [lClsHnds[0]], 'matrixSum', lSkipRotate = ['X', 'Y', 'Z'], lSkipScale = ['X', 'Y', 'Z'], bForce = True)

		## write component info
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, 'baseIkRPsolcerLimb', type = 'string', lock = True)
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