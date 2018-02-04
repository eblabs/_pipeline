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
			self._iFkCtrls = kwargs.get('iFkCtrls', 2)

	def createComponent(self):
		super(baseFkOnIkSplineLimb, self).createComponent()
		
		iRotateOrder = self._iRotateOrder
		## get reverse rotateOrder
		lRotateOrderRvs = [5, 3, 4, 1, 2, 0]
		iRotateOrderRvs = lRotateOrderRvs[iRotateOrder]

		## top and bot ik control
		sGrp_topRvsZero = transforms.createTransformNode(naming.oName(sType = 'zero', sSide = self._sSide, sPart = '%sTopBendRvs' %self._sName, iIndex = self._iIndex).sName, iRotateOrder = iRotateOrder, sParent = self._sComponentControls)
		sGrp_botRvsZero = transforms.createTransformNode(naming.oName(sType = 'zero', sSide = self._sSide, sPart = '%sBotBendRvs' %self._sName, iIndex = self._iIndex).sName, iRotateOrder = iRotateOrder, sParent = self._sComponentControls)
		
		sGrp_topRvs = transforms.createTransformNode(naming.oName(sType = 'null', sSide = self._sSide, sPart = '%sTopBendRvs' %self._sName, iIndex = self._iIndex).sName, iRotateOrder = iRotateOrderRvs, sParent = sGrp_topRvsZero)
		sGrp_botRvs = transforms.createTransformNode(naming.oName(sType = 'null', sSide = self._sSide, sPart = '%sBotBendRvs' %self._sName, iIndex = self._iIndex).sName, iRotateOrder = iRotateOrderRvs, sParent = sGrp_botRvsZero)
		
		oCtrlTop = controls.create('%sTopIk' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = sGrp_topRvs, sShape = 'cube', fSize = 4, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		oCtrlBot = controls.create('%sBotIk' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = sGrp_botRvs, sShape = 'cube', fSize = 4, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])

		oCtrlOffset_top = controls.create('%sTopIkOffset' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = oCtrlTop.sOutput, sShape = 'cube', fSize = 3, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		oCtrlOffset_bot = controls.create('%sBotIkOffset' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = oCtrlBot.sOutput, sShape = 'cube', fSize = 3, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])

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

		###### create individual bend control for each cluster (no top nor bot end cluster)
		sParent_ctrl = self._sComponentControls
		lGrpBend_top = []
		lGrpBend_bot = []
		for i, sCtrl in enumerate(self._lCtrls[1:len(self._lCtrls)-1]):
			oCtrl_top = controls.create('%sTopBend' %self._sName, sSide = self._sSide, iIndex = i + 1, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sPos = sCtrl, sParent = sParent_ctrl, sShape = 'cube', fSize = 4, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'] )
			oCtrl_bot = controls.create('%sBotBend' %self._sName, sSide = self._sSide, iIndex = len(self._lCtrls) - i - 2, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sPos = sCtrl, sParent = sParent_ctrl, sShape = 'cube', fSize = 4, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'] )
			
			lGrpBend_top.append(oCtrl_top)
			lGrpBend_bot.append(oCtrl_bot)

			sMultRot_top = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%sTopBendMult' %self._sName, iIndex = i + 1).sName)
			sMultRot_bot = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%sBotBendMult' %self._sName, iIndex = len(self._lCtrls) - i - 2).sName)

			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.output%s' %(lRotatePlug[0], sAxis), '%s.input1%s' %(sMultRot_top, sAxis))
				cmds.connectAttr('%s.output%s' %(lRotatePlug[1], sAxis), '%s.input1%s' %(sMultRot_bot, sAxis))
				cmds.connectAttr('%s.rotMult%02d' %(oCtrlTop.sName, i + 1), '%s.input2%s' %(sMultRot_top, sAxis))
				cmds.connectAttr('%s.rotMult%02d' %(oCtrlBot.sName, len(self._lCtrls) - i - 2), '%s.input2%s' %(sMultRot_bot, sAxis))
				cmds.connectAttr('%s.output%s' %(sMultRot_top, sAxis), '%s.rotate%s' %(oCtrl_top.lStacks[1], sAxis))
				cmds.connectAttr('%s.output%s' %(sMultRot_bot, sAxis), '%s.rotate%s' %(oCtrl_bot.lStacks[1], sAxis))

		lGrpBend_bot.reverse()

		for lCtrls in [lGrpBend_top, lGrpBend_bot]:
			for i, oCtrl in enumerate(lCtrls[1:]):
				oParent = lCtrls[i - 1]
				cmds.parent(oCtrl.sZero, oParent.sOutput)

				## add world matrix
				cmds.addAttr(oCtrl.sName, ln = 'matrixOutputBend', at = 'matrix')

				sMultMatrix = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrl.sSide, sPart = '%sMatrixOutputBend' %oCtrl.sPart, iIndex = oCtrl.iIndex).sName)
				cmsd.connectAttr('%s.matrixOutputWorld' %oCtrl.sName, '%s.matrixIn[0]' %sMultMatrix)
				if i > 1:
					cmds.connectAttr('%s.matrixOutputBend' %oParent.sName, '%s.matrixIn[1]' %sMultMatrix)
				else:
					cmds.connectAttr('%s.matrixOutputWorld' %oParent.sName, '%s.matrixIn[1]' %sMultMatrix)
				cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.matrixOutputBend' %oCtrl.sName)

		## connect bend matrix to top and bot ik bend ctrl
		for i, oCtrl in enumerate([oCtrlTop, oCtrlBot]):
			constraints.matrixConnect([lGrpBend_top[-1], lGrpBend_bot[-1]][i], [[sGrp_topRvsZero, sGrp_botRvsZero][i]], 'matrixOutputBend', lSkipScale = ['X', 'Y', 'Z'])

		## get top bot ik bend ctrl translate matrix
		sMultMatrix_top = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%stopMatrix' %self._sName, iIndex = self._iIndex).sName)
		sMultMatrix_bot = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sbotMatrix' %self._sName, iIndex = self._iIndex).sName)
		for i, oCtrl in enumerate([oCtrlTop, oCtrlBot]):
			sGrpRvs = [sGrp_topRvs, sGrp_botRvs][i]
			sMultMatrix = [sMultMatrix_top, sMultMatrix_bot][i]
			sGrpRvsZero = [sGrp_topRvsZero, sGrp_botRvsZero][i]
			sGrpBend = [lGrpBend_top[-1], lGrpBend_bot[-1]][i]
			cmds.connectAttr('%s.matrixOutputWorld' %oCtrl.sName, '%s.matrixIn[0]' %sMultMatrix)
			cmds.connectAttr('%s.matrix' %sGrpRvs, '%s.matrixIn[1]' %sMultMatrix)
			cmds.connectAttr('%s.matrixOutputBend' %sGrpBend, '%s.matrixIn[2]' %sMultMatrix)
			lInverseMatrix = cmds.getAttr('%s.inverseMatrix' %sGrpRvsZero)
			cmds.setAttr('%s.matrixIn[3]' %sMultMatrix, lInverseMatrix, type = 'matrix')

			oCtrlOffset = [oCtrlOffset_top, oCtrlOffset_bot][i]
			sCtrlCls = [self._lCtrls[-2], self._lCtrls[1]][i]
			oCtrlCls = controls.oControl(sCtrlCls)
			sMultMatrixCls = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixOutput' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			lMatrix = apiUtils.getLocalMatrixInNode(oCtrlCls.sPasser, oCtrlOffset.sName, sNodeAttr = 'worldMatrix[0]', sParentAttr = 'worldMatrix[0]')
			lInverseMatrix = cmds.getAttr('%s.inverseMatrix' %oCtrlCls.sZero)
			cmds.setAttr('%s.matrixIn[0]' %sMultMatrixCls, lMatrix, type = 'matrix')
			cmds.connectAttr('%s.matrixOutputWorld' %oCtrlOffset, '%s.matrixIn[0]' %sMultMatrixCls)
			cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.matrixIn[1]' %sMultMatrixCls)
			cmds.setAttr('%s.matrixIn[2]' %sMultMatrixCls, lInverseMatrix, type = 'matrix')
			constraints.matrixConnect(sMultMatrixCls, [oCtrlCls.sPasser], 'matrixSum', lSkipTranslate = [], lSkipRotate = [], lSkipScale = ['x', 'y', 'z'], bForce = True)

			sCtrlClsEnd = [self._lCtrls[-1], self._lCtrls[0]][i]
			oCtrlClsEnd = controls.oControl(sCtrlClsEnd)

			sMultMatrixClsEnd = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrlClsEnd.sSide, sPart = '%sMatrixOutput' %oCtrlClsEnd.sPart, iIndex = oCtrlClsEnd.iIndex).sName)
			lMatrix = apiUtils.getLocalMatrixInNode(oCtrlClsEnd.sPasser, oCtrlOffset.sName, sNodeAttr = 'worldMatrix[0]', sParentAttr = 'worldMatrix[0]')
			lInverseMatrix = cmds.getAttr('%s.inverseMatrix' %oCtrlClsEnd.sZero)
			cmds.setAttr('%s.matrixIn[0]' %sMultMatrixClsEnd, lMatrix, type = 'matrix')
			cmds.connectAttr('%s.matrixOutputWorld' %oCtrlOffset, '%s.matrixIn[0]' %sMultMatrixCls)
			cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.matrixIn[1]' %sMultMatrixCls)
			cmds.setAttr('%s.matrixIn[2]' %sMultMatrixClsEnd, lInverseMatrix, type = 'matrix')
			constraints.matrixConnect(sMultMatrixClsEnd, [oCtrlClsEnd.sPasser], 'matrixSum', lSkipTranslate = [], lSkipRotate = [], lSkipScale = ['x', 'y', 'z'], bForce = True)

		##### mid cls connect
		iNum = len(self._lCtrls[2:]) - 1

		#### get top bot local translate
		lMinusTranslate = []
		for i, sMatrix in enumerate([sMultMatrix_top, sMultMatrix_bot]):
			oNameMatrix = naming.oName(sMatrix)
			sGrpBend = [lGrpBend_top[-1], lGrpBend_bot[-1]][i]
			oNameGrp = naming.oName(sGrpBend)
			oNameMatrix.sType = 'decomposeMatrix'
			oNameGrp.sType = 'decomposeMatrix'
			sDecomposeMatrix_ctrl = cmds.createNode('decomposeMatrix', name = oNameMatrix.sName)
			sDecomposeMatrix_grp = cmds.createNode('decomposeMatrix', name = oNameGrp.sName)
			cmds.connectAttr('%s.matrixSum' %sMatrix, '%s.inputMatrix' %sDecomposeMatrix_ctrl)
			cmds.connectAttr('%s.matrixOutputBend' %sGrpBend, '%s.inputMatrix' %sDecomposeMatrix_grp)
			oNameMatrix.sType = 'plusMinusAverage'
			oNameMatrix.sPart = '%sLocalTranslate' %oNameMatrix.sPart
			sMinus = cmds.createNode('plusMinusAverage', name = oNameMatrix.sName)
			cmds.setAttr('%s.operation' %sMinus, 2)
			cmds.connectAttr('%s.outputTranslate' %sDecomposeMatrix_ctrl, '%s.input3D[0]' %sMinus)
			cmds.connectAttr('%s.outputTranslate' %sDecomposeMatrix_grp, '%s.input3D[1]' %sMinus)
			lMinusTranslate.append(sMinus)

		for i, sCtrlCls in enumerate(self._lCtrls[1:iNum + 1]):
			sGrpBend_top = lGrpBend_top[i + 1]
			sGrpBend_bot = lGrpBend_bot[-i - 2]
			oCtrlCls = controls.oControl(sCtrlCls)
			sAddMatrix = cmds.createNode('addMatrix', name = naming.oName(sType = 'addMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.matrixOutputBend' %sGrpBend_top, '%s.matrixIn[0]' %sAddMatrix)
			cmds.connectAttr('%s.matrixOutputBend' %sGrpBend_bot, '%s.matrixIn[1]' %sAddMatrix)
			sMultMatrixCls = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.matrixSum' %sAddMatrix, '%s.matrixIn[0]' %sMultMatrixCls)			
			lInverseMatrix = cmds.getAttr('%s.inverseMatrix' %oCtrlCls.sZero)
			cmds.setAttr('%s.matrixIn[1]' %sMultMatrixCls, lInverseMatrix, type = 'matrix')

			sMultTop = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = oCtrlCls.sSide, sPart = '%sTopTranslate' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			sMultBot = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = oCtrlCls.sSide, sPart = '%sBotTranslate' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			fWeight = (i + 1) / float(iNum)
			for sAxis in ['X', 'Y', 'Z']:
				cmds.setAttr('%s.input2%s' %(sMultTop, sAxis), 1 - fWeight)
				cmds.setAttr('%s.input2%s' %(sMultBot, sAxis), fWeight)
			cmds.connectAttr('%s.output3D' %lMinusTranslate[0], '%s.input1' %sMultTop)
			cmds.connectAttr('%s.output3D' %lMinusTranslate[1], '%s.input1' %sMultBot)
			sPlus = cmds.createNode('plusMinusAverage', name = naming.oName(sType = 'plusMinusAverage', sSide = oCtrlCls.sSide, sPart = '%sTranslateOutput' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.output' %sMultTop, '%s.input3D[0]' %sPlus)
			cmds.connectAttr('%s.output' %sMultBot, '%s.input3D[1]' %sPlus)
			sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.matrixSum' %sAddMatrix, '%s.matrixIn[0]' %sDecomposeMatrix)
			cmds.connectAttr('%s.outputTranslate' %sDecomposeMatrix, '%s.input3D[2]' %sPlus)

			sQuatToEuler = cmds.createNode('quatToEuler', name = naming.oName(sType = 'quatToEuler', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.outputQuat' %sDecomposeMatrix, '%s.inputQuat' %sQuatToEuler)
			cmds.connectAttr('%s.ro' %oCtrlCls.sPasser, '%s.inputRotateOrder' %sQuatToEuler)

			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.output3D%s' %(sPlus, sAxis.lower()), '%s.translate%s' %(oCtrlCls.sPasser, sAxis))
				cmds.connectAttr('%s.outputRotate%s' %(sQuatToEuler, sAxis), '%s.rotate%s' %(oCtrlCls.sPasser, sAxis))

		## fk controls
		lCtrlsFkTop = []
		lCtrlsFkBot = []
		for i, lGrpBend in enumerate([lGrpBend_top, lGrpBend_bot]):
			iNum = len(lGrpBend)
			iAvg = iNum/self._iFkCtrls
			iRemain = iNum%self._iFkCtrls
			sPos = ['Top', 'Bot'][i]
			sMultMatrixParent = None
			for j in range(self._iFkCtrls):
				oCtrlFk = controls.create('%s%sFk' %(self._sName, sPos), sSide = self._sSide, iIndex = j + 1, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = self._sComponentControls, sShape = 'cube', fSize = 4, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
				[lCtrlsFkTop, lCtrlsFkBot][i].append(oCtrlFk)
				sDecomposeMatrixFkRot = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = self._sSide, sPart = '%s%sFkRot' %(self._sName, sPos), iIndex = j + 1).sName)
				cmds.connectAttr('%s.matrixOutputLocal' %oCtrl.sName, '%s.inputMatrix' %sDecomposeMatrixFkRot)
				sQuatToEulerFkRot = cmds.createNode('quatToEuler', name = naming.oName(sType = 'quatToEuler', sSide = self._sSide, sPart = '%s%sFkRot' %(self._sName, sPos), iIndex = j + 1).sName)
				cmds.connectAttr('%s.outputQuat' %sDecomposeMatrixFkRot, '%s.inputQuat' %sQuatToEulerFkRot)
				sMultFkRot = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%s%sFkRot' %(self._sName, sPos), iIndex = j + 1).sName)
				cmds.connectAttr('%s.outputQuat' %sDecomposeMatrixFkRot, '%s.inputQuat' %sQuatToEulerFkRot)
				sComposeMatrix = cmds.createNode('composeMatrix', name = naming.oName(sType = 'composeMatrix', sSide = self._sSide, sPart = '%s%sFkRot' %(self._sName, sPos), iIndex = j + 1).sName)
				for sAxis in ['X', 'Y', 'Z']:
					cmds.setAttr('%s.input2%s' %(sMultFkRot, sAxis), 1/float(iAvg))
					cmds.connectAttr('%s.output%s' %(sMultFkRot, sAxis), '%s.inputRotate%s' %(sComposeMatrix, sAxis))					
				if j > 0:
					sMultMatrixFkPos = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%s%sFkPos' %(self._sName, sPos), iIndex = j+1 ).sName)
					for m, sCtrl in enumerate(lGrpBend[iAvg * (j - 1) : iAvg * j]):
						oCtrl = controls.oControl(sCtrl)
						lMatrix = cmds.getAttr('%s.matrix' %oCtrl.sZero)
						cmds.setAttr('%s.matrixIn[%d]' %(sMultMatrixFkPos, m*2), lMatrix, type = 'matrix')
						cmds.connectAttr('%s.outputMatrix' %sComposeMatrix)
					if sMultMatrixParent:
						cmds.connectAttr('%s.matrixSum' %sMultMatrixParent, '%s.matrixIn[%d]' %(sMultMatrixFkPos, iAvg * 2))
					cmds.connectAttr('%s.ro' %(oCtrl.sPasser), '%s.inputRotateOrder' %sQuatToEulerFkRot)
					constraints.matrixConnect(sMultMatrixFkPos, [oCtrlFk.sZero], 'matrixSum', lSkipScale = ['X', 'Y', 'Z'])
					sMultMatrixParent = sMultMatrixFkPos
				else:
					cmds.delete(cmds.pointConstraint(lGrpBend[0], oCtrlFk.sZero, mo = False))
				for sCtrl in enumerate(lGrpBend[iAvg * j : iAvg * j + 1]):
					oCtrl = controls.oControl(sCtrl)
					for sAxis in ['X', 'Y', 'Z']:
						cmds.setAttr('%s.output%s' %(sMultFkRot, sAxis), oCtrl.sPasser)
			for m in range(iRemain):
				sCtrl = lGrpBend[iAvg * j + m]
				oCtrl = controls.oControl(sCtrl)
				for sAxis in ['X', 'Y', 'Z']:
					cmds.setAttr('%s.output%s' %(sMultFkRot, sAxis), oCtrl.sPasser)

		#### twist matrix connect
		cmds.setAttr('%s.dTwistControlEnable' %self._sIkHnd, 1)
		cmds.setAttr('%s.dWorldUpType' %self._sIkHnd, 4)
		for i, sPos in enumerate(['Top', 'Bot']):
			sMultMatrixTwist = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sMatrixTwist%s' %(self._sName, sPos), iIndex = self._iIndex).sName)
			lMatrix = apiUtils.getLocalMatrixInNode([self._lJnts[-1], self._lJnts[0]][i], oCtrlTop.sName)
			cmds.setAttr('%s.matrixIn[0]' %sMultMatrixTwist, lMatrix, type = 'matrix')
			cmds.connectAttr('%s.matrixOutputWorld' %[oCtrlOffset_top, oCtrlOffset_bot][i], '%s.matrixIn[1]' %sMultMatrixTwist)
			cmds.connectAttr('%s.matrix' %[sGrp_topRvs, sGrp_botRvs][i], '%s.matrixIn[2]' %sMultMatrixTwist)
			cmds.connectAttr('%s.matrixOutputBend' %[lGrpBend_top, lGrpBend_bot][i][-1], '%s.matrixIn[3]' %sMultMatrixTwist)
			cmds.connectAttr('%s.matrixSum' %sMultMatrixTwist, '%s.%s' %(self._sIkHnd, ['dWorldUpMatrix', 'dWorldUpMatrixEnd'][i]))
		
		##  hide controls
		for sCtrl in [self._lCtrls[0], self._lCtrls[1], self._lCtrls[-2], self._lCtrls[-1]]:
			oCtrl = controls.oControl(sCtrl)
			cmds.setAttr('%s.v' %oCtrl.sZero, 0, lock = True)

		sCtrlShape = naming.oName(sType = 'ctrl', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		lCtrls = [oCtrlTop, oCtrlBot, oCtrlOffset_top, oCtrlOffset_bot] + lGrpBend_top + lGrpBend_bot + lCtrlsFkTop + lCtrlsFkBot
		lCtrlsName = []
		for oCtrl in lCtrls:
			lCtrlsName.append(oCtrl.sName)
		lCtrlsName += self._lCtrls[2: len(self._lCtrls) - 2]
		controls.addCtrlShape(lCtrlsName, sCtrlShape, bVis = False)
		cmds.addAttr(sCtrlShape, ln = 'topFkCtrlVis', at = 'long', min = 0, max = 1, keyable = False)		
		cmds.addAttr(sCtrlShape, ln = 'botFkCtrlVis', at = 'long', min = 0, max = 1, keyable = False)		
		cmds.addAttr(sCtrlShape, ln = 'topBendCtrlVis', at = 'long', min = 0, max = 1, keyable = False)		
		cmds.addAttr(sCtrlShape, ln = 'botBendCtrlVis', at = 'long', min = 0, max = 1, keyable = False)		
		cmds.addAttr(sCtrlShape, ln = 'tweakCtrlVis', at = 'long', min = 0, max = 1, keyable = False)
		cmds.setAttr('%s.topFkCtrlVis' %sCtrlShape, channelBox = True)
		cmds.setAttr('%s.botFkCtrlVis' %sCtrlShape, channelBox = True)
		cmds.setAttr('%s.topBendCtrlVis' %sCtrlShape, channelBox = True)
		cmds.setAttr('%s.botBendCtrlVis' %sCtrlShape, channelBox = True)
		cmds.setAttr('%s.tweakCtrlVis' %sCtrlShape, channelBox = True)
		for sCtrl in [self._lCtrls[2: len(self._lCtrls) - 2]]:
			oCtrl = controls.oControl(sCtrl)
			cmds.connectAttr('%s.tweakCtrlVis' %sCtrlShape, '%s.v' %oCtrl.sZero)
		for oCtrl in lGrpBend_top:
			cmds.connectAttr('%s.topBendCtrlVis' %sCtrlShape, '%s.v' %oCtrl.sZero)
		for oCtrl in lGrpBend_bot:
			cmds.connectAttr('%s.botBendCtrlVis' %sCtrlShape, '%s.v' %oCtrl.sZero)
		for oCtrl in lCtrlsFkTop:
			cmds.connectAttr('%s.topFkCtrlVis' %sCtrlShape, '%s.v' %oCtrl.sZero)
		for oCtrl in lCtrlsFkBot:
			cmds.connectAttr('%s.botFkCtrlVis' %sCtrlShape, '%s.v' %oCtrl.sZero)

		for i, sCtrl in enumerate([oCtrlTop.sName, oCtrlBot.sName]):
			oCtrlOffset = [oCtrlOffset_top, oCtrlOffset_bot][i]
			cmds.addAttr(sCtrl, ln = 'offsetCtrlVis', at = 'long', min = 0, max = 1, keyable = False)
			cmds.setAttr('%s.offsetCtrlVis' %sCtrl, channelBox = True)
			cmds.connectAttr('%s.offsetCtrlVis' %sCtrl, '%s.v' %oCtrlOffset.sZero)

		## write component info
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, lock = False)
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, 'baseFkOnIkSplineLimb', type = 'string', lock = True)

		cmds.setAttr('%s.sControls' %self._sComponentMaster, lock = False)
		sControlsString = ''
		for sCtrl in lCtrlsName:
			sControlsString += '%s,' %sCtrl
		cmds.setAttr('%s.sControls' %self._sComponentMaster, sControlsString[:-1], type = 'string', lock = True)

		self._getComponentInfo(self._sComponentMaster)