#################################################
# base fk chain limb
# this limb should do the fk chain rig functions
#################################################
## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import riggingAPI.joints as joints
import riggingAPI.controls as controls
import riggingAPI.constraints as constraints

import riggingAPI.rigComponents.baseComponent as baseComponent

class baseFkChainLimb(baseComponent.baseComponent):
	"""docstring for baseFkChainLimb"""
	def __init__(self, *args, **kwargs):
		super(baseFkChainLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpJnts = kwargs.get('lBpJnts', None)
			self._iStacks = kwargs.get('iStacks', 1)
			self._lLockHideAttrs = kwargs.get('lLockHideAttrs', ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'])
			self._bBind = kwargs.get('bBind', False)

	def createComponent(self):
		super(baseFkChainLimb, self).createComponent()

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
			oJntName.sPart = '%sFk' %oJntName.sPart
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			sParent_jnt = sJnt
			lJnts.append(sJnt)

			## bind jnt
			if self._bBind:
				oJntBindName = naming.oName(sBpJnt)
				oJntBindName.sType = 'bindJoint'
				sBindJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntBindName.sName, sParent = sParent_bind)
				sParent_bind = sBindJnt
				lBindJnts.append(sBindJnt)
				for sAxis in ['X', 'Y', 'Z']:
					cmds.connectAttr('%s.translate%s' %(sJnt, sAxis), '%s.translate%s' %(sBindJnt, sAxis))
					cmds.connectAttr('%s.rotate%s' %(sJnt, sAxis), '%s.rotate%s' %(sBindJnt, sAxis))
					cmds.connectAttr('%s.scale%s' %(sJnt, sAxis), '%s.scale%s' %(sBindJnt, sAxis))

			## controls
			if i < len(self._lBpJnts) - 1:
				iRotateOrder = cmds.getAttr('%s.ro' %sJnt)
				oCtrl = controls.create('%sFk' %oJntName.sPart, sSide = oJntName.sSide, iIndex = oJntName.iIndex, iStacks = self._iStacks, bSub = True, sParent = sParent_ctrl, sPos = sJnt, iRotateOrder = iRotateOrder, sShape = 'square', fSize = 8, lLockHideAttrs = self._lLockHideAttrs)
				sParent_ctrl = oCtrl.sOutput
				lCtrls.append(oCtrl.sName)

				## connect ctrl to joint
				sMultMatrix = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oJntName.sSide, sPart = '%sFkConstraint' %oJntName.sPart, iIndex = oJntName.iIndex).sName)
				cmds.connectAttr('%s.matrixOutputLocal' %oCtrl.sName, '%s.matrixIn[0]' %sMultMatrix)
				lTranslate = cmds.getAttr('%s.translate' %sJnt)[0]
				mMatrix = apiUtils.createMMatrixFromTransformInfo(lTranslate = [lTranslate[0], lTranslate[1], lTranslate[2]])
				lMatrix = apiUtils.convertMMatrixToList(mMatrix)
				cmds.setAttr('%s.matrixIn[1]' %sMultMatrix, lMatrix, type = 'matrix')

				constraints.matrixConnect(sMultMatrix, [sJnt], 'matrixSum', lSkipScale = ['X', 'Y', 'Z'], bForce = True)

		## pass info to class
		self._lJnts = lJnts
		self._lCtrls = lCtrls
		self._lBindJnts = lBindJnts

		## write component info
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, 'baseFkChainLimb', type = 'string', lock = True)
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
		if self._bInfo:
			self._writeOutputMatrixInfo(lJnts)

		self._getComponentInfo(self._sComponentMaster)



