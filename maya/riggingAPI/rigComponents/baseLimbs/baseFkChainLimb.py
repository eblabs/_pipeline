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

import riggingAPI.rigComponents.baseLimb.baseJointsLimb as baseJointsLimb
## import rig utils
import riggingAPI.rigComponents.rigUtils.createDriveJoints as createDriveJoints
import riggingAPI.rigComponents.rigUtils.addTwistJoints as addTwistJoints

class baseFkChainLimb(baseJointsLimb.baseJointsLimb):
	"""docstring for baseFkChainLimb"""
	def __init__(self, *args, **kwargs):
		super(baseFkChainLimb, self).__init__(*args, **kwargs)

	def createComponent(self):
		super(baseFkChainLimb, self).createComponent()

		lJnts, lBindJnts = createDriveJoints.createDriveJoints(self._lBpJnts, sParent = self._sComponentDrvJoints, sSuffix = 'Fk', bBind = self._bBind, sBindParent = self._sComponentBindJoints)

		## controls
		sParent_ctrl = self._sComponentControls
		lCtrls = []
		for sJnt in lJnts[:-1]:
			# naming info
			oJntName = naming.oName(sJnt)

			iRotateOrder = cmds.getAttr('%s.ro' %sJnt)
			oCtrl = controls.create(oJntName.sPart, sSide = oJntName.sSide, iIndex = oJntName.iIndex, iStacks = self._iStacks, bSub = True, sParent = sParent_ctrl, sPos = sJnt, iRotateOrder = iRotateOrder, sShape = 'square', fSize = 8, lLockHideAttrs = self._lLockHideAttrs)
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
		self._writeGeneralComponentInfo('baseFkChainLimb', lJnts, lCtrls, lBindJnts)
		## output matrix
		if self._bInfo:
			self._writeOutputMatrixInfo(lJnts)

		## add twist joints
		addTwistJoints.twistJointsForLimb(self._iTwistJntNum, self._lSkipTwist, lJnts, self._lBpJnts, bBind = self._bBind, sNode = self._sComponentMaster, bInfo = self._bInfo)

		## get component info
		self._getComponentInfo(self._sComponentMaster)



