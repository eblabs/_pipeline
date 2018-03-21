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
import common.debug as debug
import baseIkSplineSolverLimb

## kwarg class
class kwargsGenerator(baseIkSplineSolverLimb.kwargsGenerator):
	"""docstring for kwargsGenerator"""
	def __init__(self):
		super(kwargsGenerator, self).__init__()
		self.dKwargs = {'iRotateOrder': 0,
						'bTop': True,
						'bBot': True}
		self.addKwargs()

class baseFkOnIkSplineLimb(baseIkSplineSolverLimb.baseIkSplineSolverLimb):
	"""docstring for baseFkOnIkSplineLimb"""
	def __init__(self, *args, **kwargs):
		super(baseFkOnIkSplineLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._iRotateOrder = kwargs.get('iRotateOrder', 0)
			self._bTop = kwargs.get('bTop', True)
			self._bBot = kwargs.get('bBot', True)

	def createComponent(self):
		super(baseFkOnIkSplineLimb, self).createComponent()
		
		iRotateOrder = self._iRotateOrder
		## get reverse rotateOrder
		lRotateOrderRvs = [5, 3, 4, 1, 2, 0]
		iRotateOrderRvs = lRotateOrderRvs[iRotateOrder]

		## top and bot ik control
		lCtrlBend = []
		lCtrlBendName = []
		lGrpRvs = []
		lGrpRvsZero = []
		lCtrlOffset = []
		lCtrlCls = []
		lCtrlClsEnd = []

		sGrp_topRvsZero = transforms.createTransformNode(naming.oName(sType = 'zero', sSide = self._sSide, sPart = '%sTopBendRvs' %self._sName, iIndex = self._iIndex).sName, iRotateOrder = iRotateOrder, sParent = self._sComponentControls, sPos = self._lCtrls[-2])
		sGrp_topRvs = transforms.createTransformNode(naming.oName(sType = 'null', sSide = self._sSide, sPart = '%sTopBendRvs' %self._sName, iIndex = self._iIndex).sName, iRotateOrder = iRotateOrderRvs, sParent = sGrp_topRvsZero, sPos = sGrp_topRvsZero)
		oCtrlTop = controls.create('%sTopIk' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = sGrp_topRvs, sPos = sGrp_topRvs, sShape = 'cube', fSize = 6, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		oCtrlOffset_top = controls.create('%sTopIkOffset' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = oCtrlTop.sOutput, sPos = oCtrlTop.sOutput, sShape = 'cube', fSize = 3, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		if self._bTop:
			lCtrlBend.append(oCtrlTop)
			lCtrlBendName.append('Top')
			lGrpRvs.append(sGrp_topRvs)
			lGrpRvsZero.append(sGrp_topRvsZero)
			lCtrlOffset.append(oCtrlOffset_top)
			lCtrlCls.append(self._lCtrls[-2])
			lCtrlClsEnd.append(self._lCtrls[-1])
		else:
			cmds.setAttr('%s.v' %oCtrlTop.sZero, 0)
		
		sGrp_botRvsZero = transforms.createTransformNode(naming.oName(sType = 'zero', sSide = self._sSide, sPart = '%sBotBendRvs' %self._sName, iIndex = self._iIndex).sName, iRotateOrder = iRotateOrder, sParent = self._sComponentControls, sPos = self._lCtrls[1])
		sGrp_botRvs = transforms.createTransformNode(naming.oName(sType = 'null', sSide = self._sSide, sPart = '%sBotBendRvs' %self._sName, iIndex = self._iIndex).sName, iRotateOrder = iRotateOrderRvs, sParent = sGrp_botRvsZero, sPos = sGrp_botRvsZero)
		oCtrlBot = controls.create('%sBotIk' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = sGrp_botRvs, sPos = sGrp_botRvs, sShape = 'cube', fSize = 6, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		oCtrlOffset_bot = controls.create('%sBotIkOffset' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = oCtrlBot.sOutput, sPos = oCtrlBot.sOutput, sShape = 'cube', fSize = 3, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		if self._bBot:
			lCtrlBend.append(oCtrlBot)
			lCtrlBendName.append('Bot')
			lGrpRvs.append(sGrp_botRvs)
			lGrpRvsZero.append(sGrp_botRvsZero)
			lCtrlOffset.append(oCtrlOffset_bot)
			lCtrlCls.append(self._lCtrls[1])
			lCtrlClsEnd.append(self._lCtrls[0])
		else:
			cmds.setAttr('%s.v' %oCtrlBot.sZero, 0)

		###### matrix connect, add multiply attrs
		lRotatePlug = []
		for i, oCtrl in enumerate(lCtrlBend):
			attributes.addDivider([oCtrl.sName], 'RotMult')
			for j in range(1, len(self._lCtrls) - 1):
				cmds.addAttr(oCtrl.sName, ln = 'rotMult%02d' %j, at = 'float', min = 0, max = 1, dv = 1, keyable = True)

			sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = self._sSide, sPart = '%s%sBend' %(self._sName, lCtrlBendName[i])).sName)
			sQuatToEuler = cmds.createNode('quatToEuler', name = naming.oName(sType = 'quatToEuler', sSide = self._sSide, sPart = '%s%sBend' %(self._sName, lCtrlBendName[i])).sName)
			cmds.connectAttr('%s.matrixOutputLocal' %oCtrl.sName, '%s.inputMatrix' %sDecomposeMatrix)
			cmds.connectAttr('%s.outputQuat' %sDecomposeMatrix, '%s.inputQuat' %sQuatToEuler)
			cmds.connectAttr('%s.ro' %oCtrl.sName, '%s.inputRotateOrder' %sQuatToEuler)
			sMult = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%s%sBend' %(self._sName, lCtrlBendName[i])).sName)
			cmds.setAttr('%s.operation' %sMult, 2)
			sMultRvs = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%s%sBendRvs' %(self._sName, lCtrlBendName[i])).sName)
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.outputRotate%s' %(sQuatToEuler, sAxis), '%s.input1%s' %(sMult, sAxis))
				cmds.setAttr('%s.input2%s' %(sMult, sAxis), len(self._lCtrls) - 2)
				cmds.connectAttr('%s.outputRotate%s' %(sQuatToEuler, sAxis), '%s.input1%s' %(sMultRvs, sAxis))
				cmds.setAttr('%s.input2%s' %(sMultRvs, sAxis), -1)
				cmds.connectAttr('%s.output%s' %(sMultRvs, sAxis), '%s.rotate%s' %(lGrpRvs[i], sAxis))
			lRotatePlug.append(sMult)

		###### create individual bend control for each cluster (no top nor bot end cluster)
		sParent_ctrl = self._sComponentControls
		lGrpBend_top = []
		lGrpBend_bot = []
		for i, sCtrl in enumerate(self._lCtrls[1:len(self._lCtrls)-1]):
			lMultRot = []
			lCtrlBendIndiv = []

			if self._bTop:
				oCtrl_top = controls.create('%sTopBend' %self._sName, sSide = self._sSide, iIndex = i + 1, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sPos = sCtrl, sParent = sParent_ctrl, sShape = 'cube', fSize = 4, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'] )
				lGrpBend_top.append(oCtrl_top)
				sMultRot_top = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%sTopBendMult' %self._sName, iIndex = i + 1).sName)
				lMultRot.append(sMultRot_top)
				lCtrlBendIndiv.append(oCtrl_top)

			if self._bBot:
				oCtrl_bot = controls.create('%sBotBend' %self._sName, sSide = self._sSide, iIndex = len(self._lCtrls) - i - 2, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sPos = sCtrl, sParent = sParent_ctrl, sShape = 'cube', fSize = 4, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'] )			
				lGrpBend_bot.append(oCtrl_bot)
				sMultRot_bot = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%sBotBendMult' %self._sName, iIndex = len(self._lCtrls) - i - 2).sName)
				lMultRot.append(sMultRot_bot)
				lCtrlBendIndiv.append(oCtrl_bot)

			for sAxis in ['X', 'Y', 'Z']:
				for j, sMultRot in enumerate(lMultRot):
					cmds.connectAttr('%s.output%s' %(lRotatePlug[j], sAxis), '%s.input1%s' %(sMultRot, sAxis))
					cmds.connectAttr('%s.rotMult%02d' %(lCtrlBend[j].sName, i + 1), '%s.input2%s' %(sMultRot, sAxis))
					cmds.connectAttr('%s.output%s' %(sMultRot, sAxis), '%s.rotate%s' %(lCtrlBendIndiv[j].lStacks[0], sAxis))

		lGrpBend_bot.reverse()

		lGrpBend = []
		for lCtrls in [lGrpBend_top, lGrpBend_bot]:
			if lCtrls:
				for oCtrl in lCtrls:
					print oCtrl.sName
				lGrpBend.append(lCtrls)

				for i, oCtrl in enumerate(lCtrls[1:]):
					oParent = lCtrls[i]
					cmds.parent(oCtrl.sZero, oParent.sOutput)

					## add world matrix
					cmds.addAttr(oCtrl.sName, ln = 'matrixOutputBend', at = 'matrix')

					sMultMatrix = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrl.sSide, sPart = '%sMatrixOutputBend' %oCtrl.sPart, iIndex = oCtrl.iIndex).sName)
					cmds.connectAttr('%s.matrixOutputWorld' %oCtrl.sName, '%s.matrixIn[0]' %sMultMatrix)
					if i > 0:
						cmds.connectAttr('%s.matrixOutputBend' %oParent.sName, '%s.matrixIn[1]' %sMultMatrix)
					else:
						cmds.connectAttr('%s.matrixOutputWorld' %oParent.sName, '%s.matrixIn[1]' %sMultMatrix)
					cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.matrixOutputBend' %oCtrl.sName)

		## connect bend matrix to top and bot ik bend ctrl
		for i, lGrp in enumerate(lGrpBend):
			constraints.matrixConnect(lGrpBend[i][-1].sName, [lGrpRvsZero[i]], 'matrixOutputBend', lSkipScale = ['X', 'Y', 'Z'])
		
		## get top bot ik bend ctrl translate matrix
		lMultMatrix = []
		for i, oCtrl in enumerate(lCtrlBend):
			sGrpRvs = lGrpRvs[i]
			sMultMatrix = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%s%sMatrix' %(self._sName, lCtrlBendName[i]), iIndex = self._iIndex).sName)
			lMultMatrix.append(sMultMatrix)
			sGrpRvsZero = lGrpRvsZero[i]
			sGrpBend = lGrpBend[i][-1].sName
			oCtrlOffset = lCtrlOffset[i]
			sCtrlCls = lCtrlCls[i]
			oCtrlCls = controls.oControl(sCtrlCls)

			cmds.connectAttr('%s.matrixOutputWorld' %oCtrlOffset.sName, '%s.matrixIn[0]' %sMultMatrix)
			cmds.connectAttr('%s.matrixOutputWorld' %oCtrl.sName, '%s.matrixIn[1]' %sMultMatrix)
			cmds.connectAttr('%s.matrix' %sGrpRvs, '%s.matrixIn[2]' %sMultMatrix)
			cmds.connectAttr('%s.matrix' %sGrpRvsZero, '%s.matrixIn[3]' %sMultMatrix)

			
			sMultMatrixCls = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixOutput' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			lMatrix = apiUtils.getLocalMatrixInNode(oCtrlCls.sPasser, oCtrlOffset.sName, sNodeAttr = 'worldMatrix[0]', sParentAttr = 'worldMatrix[0]')
			lInverseMatrix = cmds.getAttr('%s.inverseMatrix' %oCtrlCls.sZero)
			cmds.setAttr('%s.matrixIn[0]' %sMultMatrixCls, lMatrix, type = 'matrix')
			cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.matrixIn[1]' %sMultMatrixCls)
			cmds.setAttr('%s.matrixIn[2]' %sMultMatrixCls, lInverseMatrix, type = 'matrix')
			constraints.matrixConnect(sMultMatrixCls, [oCtrlCls.sPasser], 'matrixSum', lSkipTranslate = [], lSkipRotate = [], lSkipScale = ['x', 'y', 'z'], bForce = True)

			sCtrlClsEnd = lCtrlClsEnd[i]
			oCtrlClsEnd = controls.oControl(sCtrlClsEnd)

			sMultMatrixClsEnd = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrlClsEnd.sSide, sPart = '%sMatrixOutput' %oCtrlClsEnd.sPart, iIndex = oCtrlClsEnd.iIndex).sName)
			lMatrix = apiUtils.getLocalMatrixInNode(oCtrlClsEnd.sPasser, oCtrlOffset.sName, sNodeAttr = 'worldMatrix[0]', sParentAttr = 'worldMatrix[0]')
			lInverseMatrix = cmds.getAttr('%s.inverseMatrix' %oCtrlClsEnd.sZero)
			cmds.setAttr('%s.matrixIn[0]' %sMultMatrixClsEnd, lMatrix, type = 'matrix')
			cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.matrixIn[1]' %sMultMatrixClsEnd)
			cmds.setAttr('%s.matrixIn[2]' %sMultMatrixClsEnd, lInverseMatrix, type = 'matrix')
			constraints.matrixConnect(sMultMatrixClsEnd, [oCtrlClsEnd.sPasser], 'matrixSum', lSkipTranslate = [], lSkipRotate = [], lSkipScale = ['x', 'y', 'z'], bForce = True)
		
		##### mid cls connect
		iNum = len(self._lCtrls[2:]) - 1

		#### get top bot local translate
		lMinusTranslate = []
		for i, sMatrix in enumerate(lMultMatrix):
			oNameMatrix = naming.oName(sMatrix)
			sGrpBend = lGrpBend[i][-1].sName
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

		for i, sCtrlCls in enumerate(self._lCtrls[2:iNum + 1]):
			oCtrlCls = controls.oControl(sCtrlCls)
			sAddMatrix = cmds.createNode('addMatrix', name = naming.oName(sType = 'addMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			sMultMatrixRotCls = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixBendRot' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			sMultMatrixCls = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.matrixSum' %sAddMatrix, '%s.matrixIn[0]' %sMultMatrixCls)			
			lInverseMatrix = cmds.getAttr('%s.inverseMatrix' %oCtrlCls.sZero)
			cmds.setAttr('%s.matrixIn[1]' %sMultMatrixCls, lInverseMatrix, type = 'matrix')
			fWeight = (i + 1) / float(iNum)
			sPlus = cmds.createNode('plusMinusAverage', name = naming.oName(sType = 'plusMinusAverage', sSide = oCtrlCls.sSide, sPart = '%sTranslateOutput' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)

			for j, sPos in enumerate(lCtrlBendName):
				sMult = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = oCtrlCls.sSide, sPart = '%s%sTranslate' %(oCtrlCls.sPart, sPos), iIndex = oCtrlCls.iIndex).sName)
				if sPos == 'Top':
					sGrpBend = lGrpBend[j][i + 1].sName
					for sAxis in ['X', 'Y', 'Z']:
						cmds.setAttr('%s.input2%s' %(sMult, sAxis), fWeight)
				else:
					sGrpBend = lGrpBend[j][-i - 2].sName
					for sAxis in ['X', 'Y', 'Z']:
						cmds.setAttr('%s.input2%s' %(sMult, sAxis), 1-fWeight)
				cmds.connectAttr('%s.matrixOutputBend' %sGrpBend, '%s.matrixIn[%d]' %(sAddMatrix, j))
				cmds.connectAttr('%s.matrixOutputBend' %sGrpBend, '%s.matrixIn[%d]' %(sMultMatrixRotCls, j))
				cmds.connectAttr('%s.output3D' %lMinusTranslate[j], '%s.input1' %sMult)
				cmds.connectAttr('%s.output' %sMult, '%s.input3D[%d]' %(sPlus, j))

			sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.matrixSum' %sMultMatrixCls, '%s.inputMatrix' %sDecomposeMatrix)
			cmds.connectAttr('%s.outputTranslate' %sDecomposeMatrix, '%s.input3D[2]' %sPlus)

			sDecomposeMatrixRot = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = oCtrlCls.sSide, sPart = '%sMatrixBendRot' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.matrixSum' %sMultMatrixRotCls, '%s.inputMatrix' %sDecomposeMatrixRot)
			sQuatToEuler = cmds.createNode('quatToEuler', name = naming.oName(sType = 'quatToEuler', sSide = oCtrlCls.sSide, sPart = '%sMatrixBend' %oCtrlCls.sPart, iIndex = oCtrlCls.iIndex).sName)
			cmds.connectAttr('%s.outputQuat' %sDecomposeMatrixRot, '%s.inputQuat' %sQuatToEuler)
			cmds.connectAttr('%s.ro' %oCtrlCls.sPasser, '%s.inputRotateOrder' %sQuatToEuler)

			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.output3D%s' %(sPlus, sAxis.lower()), '%s.translate%s' %(oCtrlCls.sPasser, sAxis))
				cmds.connectAttr('%s.outputRotate%s' %(sQuatToEuler, sAxis), '%s.rotate%s' %(oCtrlCls.sPasser, sAxis))

		#### twist matrix connect
		lMultMatrixTwist = []
		for i, sPos in enumerate(['Top', 'Bot']):
			sMultMatrixTwist = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sMatrixTwist%s' %(self._sName, sPos), iIndex = self._iIndex).sName)
			lMatrix = apiUtils.getLocalMatrixInNode([self._lJnts[-1], self._lJnts[0]][i], [oCtrlTop, oCtrlBot][i].sName)
			cmds.setAttr('%s.matrixIn[0]' %sMultMatrixTwist, lMatrix, type = 'matrix')
			cmds.connectAttr('%s.matrixOutputWorld' %[oCtrlOffset_top, oCtrlOffset_bot][i].sName, '%s.matrixIn[1]' %sMultMatrixTwist)
			cmds.connectAttr('%s.matrixOutputWorld' %[oCtrlTop, oCtrlBot][i].sName, '%s.matrixIn[2]' %sMultMatrixTwist)
			cmds.connectAttr('%s.matrix' %[sGrp_topRvs, sGrp_botRvs][i], '%s.matrixIn[3]' %sMultMatrixTwist)
			cmds.connectAttr('%s.matrix' %[sGrp_topRvsZero, sGrp_botRvsZero][i], '%s.matrixIn[4]' %sMultMatrixTwist)
			lMultMatrixTwist.append(sMultMatrixTwist)
		cmds.setAttr('%s.dTwistControlEnable' %self._sIkHnd, 1)
		cmds.setAttr('%s.dWorldUpType' %self._sIkHnd, 4)
		for i, sMultMatrixTwist in enumerate(lMultMatrixTwist):
			cmds.connectAttr('%s.matrixSum' %sMultMatrixTwist, '%s.%s' %(self._sIkHnd, ['dWorldUpMatrixEnd', 'dWorldUpMatrix'][i]))
		
		##  hide controls
		for sCtrl in [self._lCtrls[0], self._lCtrls[1], self._lCtrls[-2], self._lCtrls[-1]]:
			oCtrl = controls.oControl(sCtrl)
			cmds.setAttr('%s.v' %oCtrl.sZero, 0, lock = True)

		sCtrlShape = naming.oName(sType = 'ctrl', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		lCtrls = [oCtrlTop, oCtrlBot, oCtrlOffset_top, oCtrlOffset_bot] + lGrpBend_top + lGrpBend_bot
		lCtrlsName = []
		for oCtrl in lCtrls:
			lCtrlsName.append(oCtrl.sName)
		lCtrlsName += self._lCtrls[2: len(self._lCtrls) - 2]
		controls.addCtrlShape(lCtrlsName, sCtrlShape, bVis = False)
		for i, sPos in enumerate(lCtrlBendName):			
			cmds.addAttr(sCtrlShape, ln = '%sBendCtrlVis' %sPos.lower(), at = 'long', min = 0, max = 1, keyable = False)		
			cmds.setAttr('%s.%sBendCtrlVis' %(sCtrlShape, sPos.lower()), channelBox = True)

			for oCtrl in lGrpBend[i]:
				cmds.connectAttr('%s.%sBendCtrlVis' %(sCtrlShape, sPos.lower()), '%s.v' %oCtrl.sZero)

		cmds.addAttr(sCtrlShape, ln = 'tweakCtrlVis', at = 'long', min = 0, max = 1, keyable = False)
		cmds.setAttr('%s.tweakCtrlVis' %sCtrlShape, channelBox = True)
		for sCtrl in self._lCtrls[2: len(self._lCtrls) - 2]:
			oCtrl = controls.oControl(sCtrl)
			cmds.connectAttr('%s.tweakCtrlVis' %sCtrlShape, '%s.v' %oCtrl.sZero)

		for i, sCtrl in enumerate([oCtrlTop.sName, oCtrlBot.sName]):
			oCtrlOffset = [oCtrlOffset_top, oCtrlOffset_bot][i]
			cmds.addAttr(sCtrl, ln = 'offsetCtrlVis', at = 'long', min = 0, max = 1, keyable = False)
			cmds.setAttr('%s.offsetCtrlVis' %sCtrl, channelBox = True)
			cmds.connectAttr('%s.offsetCtrlVis' %sCtrl, '%s.v' %oCtrlOffset.sZero)

		## write component info
		self._writeGeneralComponentInfo('baseFkOnIkSplineLimb', self._lJnts, lCtrlsName, self._lBindJnts, self._lBindRootJnts)
		
		self._getComponentInfo(self._sComponentMaster)