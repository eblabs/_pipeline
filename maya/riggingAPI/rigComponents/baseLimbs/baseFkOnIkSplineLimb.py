########################################################
# base fk on ik spline limb
# limb functions
#     -- spline ik tweaker
#     -- top and bot bend control, with translate
#     -- fk bend control
#     -- individual bend control
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
import riggingAPI.constraints as constraints

import baseIkSplineSolverLimb

class baseFkOnIkSplineLimb(baseIkSplineSolverLimb.baseIkSplineSolverLimb):
	"""docstring for baseFkOnIkSplineLimb"""
	def __init__(self, *args, **kwargs):
		super(baseFkOnIkSplineLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._iRotateOrder = kwargs.get('iRotateOrder', 0)

	def createComponent(self):
		super(baseFkOnIkSplineLimb, self).createComponent()
		
		iRotateOrder = self._iRotateOrder
		## get reverse rotateOrder
		lRotateOrderRvs = [5, 3, 4, 1, 2, 0]
		iRotateOrderRvs = lRotateOrderRvs[iRotateOrder]
		#### chest pelvis bend
		###### chest pelvis ctrl
		sGrp_topRvs = transforms.createTransformNode(naming.oName(sType = 'null', sSide = self._sSide, sPart = '%sTopBendRvs' %self._sName, iIndex = self._iIndex).sName, iRotateOrder = iRotateOrderRvs, sParent = self._sComponentControls)
		sGrp_botRvs = transforms.createTransformNode(naming.oName(sType = 'null', sSide = self._sSide, sPart = '%sBotBendRvs' %self._sName, iIndex = self._iIndex).sName, iRotateOrder = iRotateOrderRvs, sParent = self._sComponentControls)
		
		oCtrlTop = controls.create('%sTop' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = sGrp_chestRvs, sShape = 'cube', fSize = 4, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		oCtrlBot = controls.create('%sBot' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = sGrp_pelvisRvs, sShape = 'cube', fSize = 4, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])

		###### matrix connect, add multiply attrs
		lRotatePlug = []
		for i, sCtrl in enumerate([oCtrlTop.sName, oCtrlBot.sName]):
			attributes.addDivider([sCtrl], 'RotMult')
			for j in range(1, len(self._lCtrls) - 1):
				cmds.addAttr(sCtrl, ln = 'rotMult%02d' %j, at = 'float', min = 0, max = 1, dv = 1, keyable = True)

			sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = self._sSide, sPart = '%s%sBend' %(self._sName, ['Chest', 'Pelvis'][i])).sName)
			sQuatToEuler = cmds.createNode('quatToEuler', name = naming.oName(sType = 'quatToEuler', sSide = self._sSide, sPart = '%s%sBend' %(self._sName, ['Chest', 'Pelvis'][i])).sName)
			cmds.connectAttr('%s.matrixOutputLocal' %sCtrl, '%s.inputMatrix' %sDecomposeMatrix)
			cmds.connectAttr('%s.outputQuat' %sDecomposeMatrix, '%s.inputQuat' %sQuatToEuler)
			cmds.connectAttr('%s.ro' %sCtrl, '%s.inputRotateOrder' %sQuatToEuler)
			sMult = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%s%sBend' %(self._sName, ['Chest', 'Pelvis'][i])).sName)
			cmds.setAttr('%s.operation' %sMult, 2)
			sMultRvs = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%s%sBendRvs' %(self._sName, ['Chest', 'Pelvis'][i])).sName)
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.outputRotate%s' %(sQuatToEuler, sAxis), '%s.input1%s' %(sMult, sAxis))
				cmds.setAttr('%s.input2%s' %(sMult, sAxis), len(self._lCtrls) - 2)
				cmds.connectAttr('%s.outputRotate%s' %(sQuatToEuler, sAxis), '%s.input1%s' %(sMultRvs, sAxis))
				cmds.setAttr('%s.input2%s' %(sMultRvs, sAxis), -1)
				cmds.connectAttrs('%s.output%s' %(sMultRvs, sAxis), '%s.rotate%s' %([sGrp_chestRvs, sGrp_pelvisRvs][i], sAxis))
			lRotatePlug.append(sMult)

		###### create null group for each cluster (no pelvis end joint, no chest end joint)
		sParent_ctrl = self._sComponentControls
		lGrpBend_top = []
		lGrpBend_bot = []
		for i, sCtrl in enumerate(self._lCtrls[1:len(self._lCtrls)-1]):
			sGrp_top = transforms.createTransformNode(naming.oName(sType = 'null', sSide = self._sSide, sPart = '%sChestBend' %self._sName, iIndex = i + 1).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'], iRotateOrder = iRotateOrder, sPos = sCtrl, sParent = self._sComponentControls)
			sGrp_bot = transforms.createTransformNode(naming.oName(sType = 'null', sSide = self._sSide, sPart = '%sPelvisBend' %self._sName, iIndex = len(self._lCtrls) - i - 2).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'], iRotateOrder = iRotateOrder, sPos = sCtrl, sParent = self._sComponentControls)
			lGrpBend_top.append(sGrp_top)
			lGrpBend_bot.append(sGrp_bot)

			sMultRot_chest = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%sChestBendMult' %self._sName, iIndex = i + 1).sName)
			sMultRot_pelvis = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%sPelvisBendMult' %self._sName, iIndex = len(self._lCtrls) - i - 2).sName)

			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.output%s' %(lRotatePlug[0], sAxis), '%s.input1%s' %(sGrp_chest, sMultRot_chest))
				cmds.connectAttr('%s.output%s' %(lRotatePlug[1], sAxis), '%s.input1%s' %(sGrp_pelvis, sMultRot_pelvis))
				cmds.connectAttr('%s.rotMult%02d' %(oCtrlChest.sName, i + 1), '%s.input2%s' %(sGrp_chest, sMultRot_chest))
				cmds.connectAttr('%s.rotMult%02d' %(oCtrlPelvis.sName, len(self._lCtrls) - i - 2), '%s.input2%s' %(sGrp_pelvis, sMultRot_pelvis))
				cmds.connectAttr('%s.output%s' %(sMultRot_chest, sAxis), '%s.rotate%s' %(sGrp_chest, sAxis))
				cmds.connectAttr('%s.output%s' %(sMultRot_pelvis, sAxis), '%s.rotate%s' %(sGrp_pelvis, sAxis))

		lGrpBend_pelvis.reverse()

		for i in range(len(sGrpParent_chest[1:])):
			for j, sGrp in enumerate([lGrpBend_chest[i], lGrpBend_pelvis[i]]):
				sParent = [lGrpBend_chest, lGrpBend_pelvis][j][i - 1]
				cmds.parent(sGrp, sParent)

				## add world matrix
				cmds.addAttr(sGrp, ln = 'matrixOutputWorld', at = 'matrix')

				oNameGrp = naming.oName(sGrp)
				oNameGrp.sType = 'multMatrix'
				oNameGrp.sPart = '%sMatrixOutputWorld' %oNameGrp.sPart
				sMultMatrix = cmds.createNode('multMatrix', name = oNameGrp.sName)
				cmsd.connectAttr('%s.matrix' %sGrp, '%s.matrixIn[0]' %sMultMatrix)
				if i > 1:
					cmds.connectAttr('%s.matrixOutputWorld' %sParent, '%s.matrixIn[1]' %sMultMatrix)
				else:
					cmds.connectAttr('%s.matrix' %sParent, '%s.matrixIn[1]' %sMultMatrix)
				cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.matrixOutputWorld' %sGrp)

		cmds.delete(cmds.pointConstraint(self._lCtrls[1], sGrp_pelvisRvs, mo = False))
		cmds.delete(cmds.pointConstraint(self._lCtrls[-2], sGrp_chestRvs, mo = False))
		cmds.parent(sGrp_pelvisRvs, lGrpBend_pelvis[-1])
		cmds.parent(sGrp_chestRvs, lGrpBend_chest[-1])

		#### connect chest and pelvis controls to clusters
		## chest and pelvis cluster
		sMultMatrixWorld_chest = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sChestMatrixWorld' %self._sName, iIndex = self._iIndex).sName)
		sMultMatrixWorld_pelvis = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sPelvisMatrixWorld' %self._sName, iIndex = self._iIndex).sName)

		for i, sCtrl in enumerate([oCtrlChest.sName, oCtrlPelvis.sName]):
			sGrpRvs = [sGrp_chestRvs, sGrp_pelvisRvs][i]
			sMultMatrix = [sMultMatrixWorld_chest, sMultMatrixWorld_pelvis][i]
			sGrpParent = [lGrpBend_chest[-1], lGrpBend_pelvis[-1]]
			sCtrlCls = [self._lCtrls[-2], self._lCtrls[1]][i]
			oCtrlCls = controls.oControl(sCtrlCls)
			cmds.connectAttr('%s.matrixOutputLocal' %sCtrl, '%s.matrixIn[0]' %sMultMatrix)
			cmds.connectAttr('%s.matrix' %sGrpRvs, '%s.matrixIn[1]' %sMultMatrix)
			cmds.connectAttr('%s.matrixOutputWorld' %sGrpParent, '%s.matrixIn[2]' %sMultMatrix)
			sMultMatrixCls = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixOutput' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.matrixIn[0]' %sMultMatrixCls)
			lInverseMatrix = cmds.getAttr('%s.inverseMatrix' %oCtrlCls.sZero)
			cmds.setAttr('%s.matrixIn[1]' %sMultMatrixCls, lInverseMatrix, type = 'matrix')
			constraints.matrixConnect(sMultMatrixCls, [oCtrlCls.sPasser], 'matrixSum', lSkipTranslate = [], lSkipRotate = [], lSkipScale = ['x', 'y', 'z'], bForce = True)

			sCtrlClsEnd = [self._lCtrls[-1], self._lCtrls[0]][i]
			oCtrlClsEnd = controls.oControl(sCtrlClsEnd)

			sMultMatrixClsEnd = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrlClsEnd.sSide, sPart = '%sMatrixOutput' %oCtrlClsEnd.sPart, iIndex = oCtrlClsEnd.iIndex).sName)
			lMatrix = apiUtils.getLocalMatrixInNode(oCtrlClsEnd.sPasser, sCtrl, sNodeAttr = 'worldMatrix[0]', sParentAttr = 'worldMatrix[0]')
			lInverseMatrix = cmds.getAttr('%s.inverseMatrix' %oCtrlClsEnd.sZero)
			cmds.setAttr('%s.matrixIn[0]' %sMultMatrixClsEnd, lMatrix, type = 'matrix')
			cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.matrixIn[1]' %sMultMatrixClsEnd)
			cmds.setAttr('%s.matrixIn[2]' %sMultMatrixClsEnd, lInverseMatrix, type = 'matrix')
			constraints.matrixConnect(sMultMatrixClsEnd, [oCtrlClsEnd.sPasser], 'matrixSum', lSkipTranslate = [], lSkipRotate = [], lSkipScale = ['x', 'y', 'z'], bForce = True)

		##### mid cls connect
		iNum = len(self._lCtrls[2:]) - 1
		## chest pelvis world translate - grp bend world translate
		lMinusTranslate = []
		for i, sMatrix in enumerate([sMultMatrixWorld_chest, sMultMatrixWorld_pelvis]):
			oCtrl = [oCtrlChest, oCtrlPelvis][i]
			sGrpBend = [lGrpBend_chest[-1], lGrpBend_pelvis[-1]][i]
			sDecomposeMatrix_ctrl = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = oCtrl.sSide, sPart = '%sMatrixCtrlTranslateWorld' %oCtrl.sPart, iIndex = oCtrl.iIndex).sName)
			sDecomposeMatrix_grp = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = oCtrl.sSide, sPart = '%sMatrixGrpTranslateWorld' %oCtrl.sPart, iIndex = oCtrl.iIndex).sName)
			cmds.connectAttr('%s.matrixSum' %sMatrix, '%s.inputMatrix' %sDecomposeMatrix_ctrl)
			cmds.connectAttr('%s.matrixOutputWorld' %sGrpBend, '%s.inputMatrix' %sDecomposeMatrix_grp)
			sMinus = cmds.createNode('plusMinusAverage', name = naming.oName(sType = 'plusMinusAverage', sSide = oCtrl.sSide, sPart = '%sMatrixTranslateWorld' %oCtrl.sPart, iIndex = oCtrl.iIndex).sName)
			cmds.setAttr('%s.operation' %sMinus, 2)
			cmds.connectAttr('%s.outputTranslate' %sDecomposeMatrix_ctrl, '%s.input3D[0]' %sMinus)
			cmds.connectAttr('%s.outputTranslate' %sDecomposeMatrix_grp, '%s.input3D[1]' %sMinus)
			lMinusTranslate.append(sMinus)

		for i, sCtrlCls in enumerate(self._lCtrls[1:iNum + 1]):
			sGrpBend_chest = lGrpBend_chest[i + 1]
			sGrpBend_pelvis = lGrpBend_pelvis[-i - 2]
			oCtrlCls = controls.oControl(sCtrlCls)
			sAddMatrix = cmds.createNode('addMatrix', name = naming.oName(sType = 'addMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.matrixOutputWorld' %sGrpBend_chest, '%s.matrixIn[0]' %sAddMatrix)
			cmds.connectAttr('%s.matrixOutputWorld' %sGrpBend_pelvis, '%s.matrixIn[1]' %sAddMatrix)
			sMultMatrixCls = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.matrixSum' %sAddMatrix, '%s.matrixIn[0]' %sMultMatrixCls)			
			lInverseMatrix = cmds.getAttr('%s.inverseMatrix' %oCtrlCls.sZero)
			cmds.setAttr('%s.matrixIn[0]' %sMultMatrixCls, lInverseMatrix, type = 'matrix')

			sMultChest = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = oCtrlCls.sSide, sPart = '%sChestTranslate' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			sMultPelvis = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = oCtrlCls.sSide, sPart = '%sPelvisTranslate' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			fWeight = (i + 1) / float(iNum)
			for sAxis in ['X', 'Y', 'Z']:
				cmds.setAttr('%s.input2%s' %(sMultChest, sAxis), 1 - fWeight)
				cmds.setAttr('%s.input2%s' %(sMultPelvis, sAxis), fWeight)
			cmds.connectAttr('%s.output3D' %lMinusTranslate[0], '%s.input1' %sMultChest)
			cmds.connectAttr('%s.output3D' %lMinusTranslate[1], '%s.input1' %sMultPelvis)
			sPlus = cmds.createNode('plusMinusAverage', name = naming.oName(sType = 'plusMinusAverage', sSide = oCtrlCls.sSide, sPart = '%sTranslateOutput' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.output' %sMultChest, '%s.input3D[0]' %sPlus)
			cmds.connectAttr('%s.output' %sMultPelvis, '%s.input3D[1]' %sPlus)
			sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.matrixSum' %sAddMatrix, '%s.matrixIn[0]' %sDecomposeMatrix)
			cmds.connectAttr('%s.outputTranslate' %sDecomposeMatrix, '%s.input3D[2]' %sPlus)

			sQuatToEuler = cmds.createNode('quatToEuler', name = naming.oName(sType = 'quatToEuler', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.outputQuat' %sDecomposeMatrix, '%s.inputQuat' %sQuatToEuler)
			cmds.connectAttr('%s.ro' %oCtrlCls.sPasser, '%s.inputRotateOrder' %sQuatToEuler)

			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.output3D%s' %(sPlus, sAxis.lower()), '%s.translate%s' %(oCtrlCls.sPasser, sAxis))
				cmds.connectAttr('%s.outputRotate%s' %(sQuatToEuler, sAxis), '%s.rotate%s' %(oCtrlCls.sPasser, sAxis))

		#### twist matrix connect
		sMultMatrixTwist_chest = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sMatrixTwistChest' %self._sPart, iIndex = self._iIndex).sName)
		sMultMatrixTwist_pelvis = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sMatrixTwistPelvis' %self._sPart, iIndex = self._iIndex).sName)
		lMatrixTop = apiUtils.getLocalMatrixInNode(self._lJnts[-1], oCtrlChest.sName)
		lMatrixBot = apiUtils.getLocalMatrixInNode(self._lJnts[0], oCtrlPelvis.sName)
		cmds.setAttr('%s.matrixIn[0]' %sMultMatrixTwist_chest, lMatrixTop, type = 'matrix')
		cmds.setAttr('%s.matrixIn[0]' %sMultMatrixTwist_pelvis, lMatrixBot, type = 'matrix')
		cmds.connectAttr('%s.matrixSum' %sMultMatrixWorld_chest, '%s.matrixIn[1]' %sMultMatrixTwist_chest)
		cmds.connectAttr('%s.matrixSum' %sMultMatrixWorld_pelvis, '%s.matrixIn[1]' %sMultMatrixTwist_pelvis)

		cmds.setAttr('%s.dTwistControlEnable' %self._sIkHnd, 1)
		cmds.setAttr('%s.dWorldUpType' %self._sIkHnd, 4)
		attributes.connectAttrs(['%s.matrixSum' %sMultMatrixTwist_pelvis, '%s.matrixSum' %sMultMatrixTwist_chest], ['%s.dWorldUpMatrix' %self._sIkHnd, '%s.dWorldUpMatrixEnd' %self._sIkHnd], bForce = True)

		##  hide tweak controls
		for sCtrl in [self._lCtrls[0], self._lCtrls[1], self._lCtrls[-2], self._lCtrls[-1]]:
			oCtrl = controls.oControl(sCtrl)
			cmds.setAttr('%s.v' %oCtrl.sZero, 0, lock = True)

		sCtrlShape = naming.oName(sType = 'ctrl', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		addCtrlShape([oCtrlChest.sName, oCtrlPelvis.sName], sCtrlShape, bVis = False)
		cmds.addAttr(sCtrlShape, ln = 'tweakCtrlVis', at = 'long', min = 0, max = 1, keyable = False)
		cmds.setAttr('%s.tweakCtrlVis' %sCtrlShape, channelBox = True)
		for sCtrl in [self._lCtrls[2: len(self._lCtrls) - 2]]:
			oCtrl = controls.oControl(sCtrl)
			cmds.connectAttr('%s.tweakCtrlVis' %sCtrlShape, '%s.v' %oCtrl.sZero)

		## write component info
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, lock = False)
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, 'spineIkModule', type = 'string', lock = True)

		cmds.setAttr('%s.sControls' %self._sComponentMaster, lock = False)
		sControlsString = ''
		for sCtrl in ([oCtrlPelvis.sName, oCtrlChest.sName] + self._lCtrls[2:len(self._lCtrls) - 2]):
			sControlsString += '%s,' %sCtrl
		cmds.setAttr('%s.sControls' %self._sComponentMaster, sControlsString[:-1], type = 'string', lock = True)

		self._getComponentInfo(self._sComponentMaster)