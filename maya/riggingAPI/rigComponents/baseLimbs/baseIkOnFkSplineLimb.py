########################################################
# base fk on ik spline limb
# limb functions
#     -- spline ik tweaker
#     -- top and bot ik control, with translate
#     -- fk bend control
#	  -- fk reverse bend control
#     -- individual ik control
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
import riggingAPI.rigComponents.rigUtils.componentInfo as componentInfo
import riggingAPI.rigComponents.baseLimbs.baseIkSplineSolverLimb as baseIkSplineSolverLimb

## kwarg class
class kwargsGenerator(baseIkSplineSolverLimb.kwargsGenerator):
	"""docstring for kwargsGenerator"""
	def __init__(self):
		super(kwargsGenerator, self).__init__()
		self.dKwargs = {'lBpCtrls': None,
						'bRvsBend': True,}
		self.addKwargs()

class baseIkOnFkSplineLimb(baseIkSplineSolverLimb.baseIkSplineSolverLimb):
	"""docstring for baseIkOnFkSplineLimb"""
	def __init__(self, *args, **kwargs):
		super(baseIkOnFkSplineLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpCtrls = kwargs.get('lBpCtrls', None)
			self._bRvsBend = kwargs.get('bRvsBend', True)

	def createComponent(self):
		super(baseIkOnFkSplineLimb, self).createComponent()

		## create temp controller
		sCrv = cmds.curve(p=[[0,0,0], [1,0,0]], k=[0,1], d=1, per = False, name = 'TEMP_CRV')
		sCtrlShape = naming.oName(sType = 'ctrl', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		controls.addCtrlShape([sCrv], sCtrlShape, bVis = False, dCtrlShapeInfo = None, bTop = False)
		cmds.addAttr(sCtrlShape, ln = 'bendCtrlVis', at = 'long', min = 0, max = 1, keyable = False)
		cmds.setAttr('%s.bendCtrlVis' %sCtrlShape, channelBox = True)

		## top bot control
		lCtrls = []
		lRotateOrder = []
		lParts = []
		for sBpCtrl in self._lBpCtrls:
			oName = naming.oName(sBpCtrl)
			iRotateOrder = cmds.getAttr('%s.ro' %sBpCtrl)
			oCtrl = controls.create(oName.sPart, sSide = oName.sSide, iIndex = oName.iIndex, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = self._sComponentControls, sPos = sBpCtrl, sShape = 'cube', fSize = 6, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
			lCtrls.append(oCtrl)
			lRotateOrder.append(iRotateOrder)
			lParts.append(oName.sPart)
		cmds.setAttr('%s.v' %lCtrls[1].sZero, self._bRvsBend)

		## bend controls
		lCtrls_bend = []
		lCtrls_bendRvs = []
		iBend = 1
		iBendRvs = len(self._lCtrls) - 3 
		for i, sCtrl_tweak in enumerate(self._lCtrls):
			if i != 1 and i != len(self._lCtrls) - 2:
				if i < len(self._lCtrls) - 1:
					oCtrl_bend = controls.create('%sBend' %self._sName, sSide = oName.sSide, iIndex = iBend, iStacks = self._iStacks, bSub = True, iRotateOrder = lRotateOrder[0], sParent = self._sComponentControls, sShape = 'square', fSize = 6, lLockHideAttrs = self._lLockHideAttrs)
					cmds.delete(cmds.pointConstraint(sCtrl_tweak, oCtrl_bend.sZero, mo = False))
					cmds.delete(cmds.orientConstraint(lCtrls[0].sName, oCtrl_bend.sZero, mo = False))
					lCtrls_bend.append(oCtrl_bend)

					iBend += 1

				if self._bRvsBend:
					if i > 0:
						oCtrl_bendRvs = controls.create('%sBendRvs' %self._sName, sSide = oName.sSide, iIndex = iBendRvs, iStacks = self._iStacks, bSub = True, iRotateOrder = lRotateOrder[1], sParent = self._sComponentControls, sShape = 'square', fSize = 6, lLockHideAttrs = self._lLockHideAttrs)
						cmds.delete(cmds.pointConstraint(sCtrl_tweak, oCtrl_bendRvs.sZero, mo = False))
						cmds.delete(cmds.orientConstraint(lCtrls[1].sName, oCtrl_bendRvs.sZero, mo = False))
						lCtrls_bendRvs.append(oCtrl_bendRvs)

						iBendRvs -= 1

		lCtrls_bend.reverse()
		lBends = []
		lBends.append(lCtrls_bend)
		cmds.connectAttr('%s.bendCtrlVis' %sCtrlShape, '%s.v' %lCtrls_bend[-1].sZero)
		if lCtrls_bendRvs:
			lBends.append(lCtrls_bendRvs)
			cmds.addAttr(sCtrlShape, ln = 'bendRvsCtrlVis', at = 'long', min = 0, max = 1, keyable = False)
			cmds.setAttr('%s.bendRvsCtrlVis' %sCtrlShape, channelBox = True)
			cmds.connectAttr('%s.bendRvsCtrlVis' %sCtrlShape, '%s.v' %lCtrls_bendRvs[-1].sZero)

		lMultMatrix = []
		for iPos, lCtrls_bendFk in enumerate(lBends):
			sMultMatrix = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sBend%sMatrix' %(self._sName, ['', 'Rvs'][iPos]), iIndex = self._iIndex).sName
			cmds.createNode('multMatrix', name = sMultMatrix)
			lMultMatrix.append(sMultMatrix)
			for i, oCtrl in enumerate(lCtrls_bendFk[:-1]):
				cmds.parent(oCtrl.sZero, lCtrls_bendFk[i+1].sOutput)
				cmds.connectAttr(oCtrl.sMatrixOutputWorldPlug, '%s.matrixIn[%d]' %(sMultMatrix, i+1))
			cmds.connectAttr(lCtrls_bendFk[-1].sMatrixOutputWorldPlug, '%s.matrixIn[%d]' %(sMultMatrix, i+2))
			## connect ik ctrl
			lMatrixLocal = apiUtils.getLocalMatrixInNode(lCtrls[iPos].sName, lCtrls_bendFk[0].sName)
			cmds.setAttr('%s.matrixIn[0]' %sMultMatrix, lMatrixLocal, type = 'matrix')
			cmds.connectAttr('%s.inverseMatrix' %lCtrls[iPos].sZero, '%s.matrixIn[%d]' %(sMultMatrix, i + 3))
			constraints.matrixConnect(sMultMatrix, [lCtrls[iPos].sPasser], 'matrixSum', lSkipScale = ['X', 'Y', 'Z'])

		cmds.addAttr(sCtrlShape, ln = 'tweakCtrlVis', at = 'long', min = 0, max = 1, keyable = False)
		cmds.setAttr('%s.tweakCtrlVis' %sCtrlShape, channelBox = True)

		## connect tweak controls
		for i, sCtrl_tweak in enumerate(self._lCtrls):
			oCtrl_tweak = controls.oControl(sCtrl_tweak)
			if i < 2 or i > len(self._lCtrls) - 3:
				if i < 2:
					oCtrl_ik = lCtrls[1]
				else:
					oCtrl_ik = lCtrls[0]
				cmds.delete(cmds.orientConstraint(oCtrl_ik.sName, oCtrl_tweak.sZero, mo = False))
				sMultMatrix = naming.oName(sType = 'multMatrix', sSide = oCtrl_tweak.sSide, sPart = '%sMatrix' %oCtrl_tweak.sPart, iIndex = oCtrl_tweak.iIndex).sName
				cmds.createNode('multMatrix', name = sMultMatrix)

				self._connectCtrlToNode(oCtrl_tweak, oCtrl_ik.sName, oCtrl_ik.sMatrixOutputWorldPlug, sMultMatrix)
				cmds.setAttr('%s.v' %oCtrl_tweak.sZero, 0, lock = True)

			else:
				fWeight = 1 - ((i-1) / float(len(self._lCtrls)-3))
				sOrient = cmds.orientConstraint(lCtrls[0].sName, lCtrls[1].sName, oCtrl_tweak.sZero, mo = False)[0]
				cmds.setAttr('%s.interpType' %sOrient, 2)
				cmds.setAttr('%s.%sW0' %(sOrient, lCtrls[0].sName), fWeight)
				cmds.setAttr('%s.%sW1' %(sOrient, lCtrls[1].sName), 1 - fWeight)
				cmds.delete(sOrient)

				cmds.addAttr(oCtrl_tweak.sName, ln = 'weight', at = 'float', min = 0, max = 1, dv = fWeight, keyable = True)

				lMatrixPasser_01 = apiUtils.getLocalMatrixInNode(oCtrl_tweak.sName, lCtrls[0].sName)
				lMatrixPasser_02 = apiUtils.getLocalMatrixInNode(oCtrl_tweak.sName, lCtrls[1].sName)

				sMultMatrixTop = naming.oName(sType = 'multMatrix', sSide = oCtrl_tweak.sSide, sPart = '%sMatrix%s%s' %(oCtrl_tweak.sPart, lParts[0][0].upper(), lParts[0][1:]), iIndex = oCtrl_tweak.iIndex).sName
				cmds.createNode('multMatrix', name = sMultMatrixTop)
				sMultMatrixBot = naming.oName(sType = 'multMatrix', sSide = oCtrl_tweak.sSide, sPart = '%sMatrix%s%s' %(oCtrl_tweak.sPart, lParts[1][0].upper(), lParts[1][1:]), iIndex = oCtrl_tweak.iIndex).sName
				cmds.createNode('multMatrix', name = sMultMatrixBot)

				cmds.setAttr('%s.matrixIn[0]' %sMultMatrixTop, lMatrixPasser_01, type = 'matrix')
				cmds.setAttr('%s.matrixIn[0]' %sMultMatrixBot, lMatrixPasser_02, type = 'matrix')

				cmds.connectAttr(lCtrls[0].sMatrixOutputWorldPlug, '%s.matrixIn[1]' %sMultMatrixTop)
				cmds.connectAttr(lCtrls[1].sMatrixOutputWorldPlug, '%s.matrixIn[1]' %sMultMatrixBot)

				cmds.connectAttr('%s.inverseMatrix' %oCtrl_tweak.sZero, '%s.matrixIn[2]' %sMultMatrixTop)
				cmds.connectAttr('%s.inverseMatrix' %oCtrl_tweak.sZero, '%s.matrixIn[2]' %sMultMatrixBot)

				sRvs = naming.oName(sType = 'reverse', sSide = oCtrl_tweak.sSide, sPart = '%sMatrixWeight' %oCtrl_tweak.sPart, iIndex = oCtrl_tweak.iIndex).sName
				cmds.createNode('reverse', name = sRvs)
				cmds.connectAttr('%s.weight' %oCtrl_tweak.sName, '%s.inputX' %sRvs)

				sWtAddMatrix = naming.oName(sType = 'wtAddMatrix', sSide = oCtrl_tweak.sSide, sPart = '%sMatrix' %oCtrl_tweak.sPart, iIndex = oCtrl_tweak.iIndex).sName
				cmds.createNode('wtAddMatrix', name = sWtAddMatrix)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixTop, '%s.wtMatrix[0].matrixIn' %sWtAddMatrix)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixBot, '%s.wtMatrix[1].matrixIn' %sWtAddMatrix)
				cmds.connectAttr('%s.weight' %oCtrl_tweak.sName, '%s.wtMatrix[0].weightIn' %sWtAddMatrix)
				cmds.connectAttr('%s.outputX' %sRvs, '%s.wtMatrix[1].weightIn' %sWtAddMatrix)

				constraints.matrixConnect(sWtAddMatrix, [oCtrl_tweak.sPasser], 'matrixSum', lSkipScale = ['X', 'Y', 'Z'])

				cmds.connectAttr('%s.tweakCtrlVis' %sCtrlShape, '%s.v' %oCtrl_tweak.sZero)

		#### twist matrix connect
		lMultMatrixTwist = []
		for i, sPos in enumerate(['Top', 'Bot']):
			sMultMatrixTwist = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sMatrixTwist%s' %(self._sName, sPos), iIndex = self._iIndex).sName)
			lMatrix = apiUtils.getLocalMatrixInNode([self._lJnts[-1], self._lJnts[0]][i], lCtrls[i].sName)
			cmds.setAttr('%s.matrixIn[0]' %sMultMatrixTwist, lMatrix, type = 'matrix')
			cmds.connectAttr(lCtrls[i].sMatrixOutputWorldPlug, '%s.matrixIn[1]' %sMultMatrixTwist)
			lMultMatrixTwist.append(sMultMatrixTwist)
		cmds.setAttr('%s.dTwistControlEnable' %self._sIkHnd, 1)
		cmds.setAttr('%s.dWorldUpType' %self._sIkHnd, 4)
		for i, sMultMatrixTwist in enumerate(lMultMatrixTwist):
			cmds.connectAttr('%s.matrixSum' %sMultMatrixTwist, '%s.%s' %(self._sIkHnd, ['dWorldUpMatrixEnd', 'dWorldUpMatrix'][i]))

		self._lTweakCtrls = self._lCtrls
		self._sTopCtrl = lCtrls[0].sName
		self._sBotCtrl = lCtrls[1].sName
		lCtrls_bend.reverse()
		lCtrls_bendRvs.reverse()
		self._lBendCtrls = []
		for oCtrl in lCtrls_bend:
			self._lBendCtrls.append(oCtrl.sName)
		self._lBendRvsCtrls = []
		for oCtrl in lCtrls_bendRvs:
			self._lBendRvsCtrls.append(oCtrl.sName)
		self._lCtrls = [self._sTopCtrl] + [self._sBotCtrl] + self._lBendCtrls + self._lBendRvsCtrls + self._lTweakCtrls

		controls.addCtrlShape(self._lCtrls, sCtrlShape, bVis = False, dCtrlShapeInfo = None, bTop = False)
		cmds.delete(sCrv)
		## write component info
		self._writeGeneralComponentInfo('baseIkOnFkSplineLimb', self._lJnts, self._lCtrls, self._lBindJnts, self._lBindRootJnts)

		sBendCtrls = componentInfo.composeListToString(self._lBendCtrls)
		sBendRvsCtrls = componentInfo.composeListToString(self._lBendRvsCtrls)
		sTweakCtrls = componentInfo.composeListToString(self._lTweakCtrls)

		lValues = [self._sTopCtrl, self._sBotCtrl, sBendCtrls, sBendRvsCtrls, sTweakCtrls]
		for i, sAttr in enumerate(['sTopCtrl', 'sBotCtrl', 'lBendCtrls', 'lBendRvsCtrls', 'lTweakCtrls']):
			cmds.addAttr(self._sComponentMaster, ln = sAttr, dt = 'string')
			cmds.setAttr('%s.%s' %(self._sComponentMaster, sAttr), lValues[i], lock = True, type = 'string')

		self._getComponentInfo(self._sComponentMaster)

	def _getComponentInfo(self, sComponent):
		super(baseIkOnFkSplineLimb, self)._getComponentInfo(sComponent)

		self._sTopCtrl = self._getComponentAttr(sComponent, 'sTopCtrl')
		self._sBotCtrl = self._getComponentAttr(sComponent, 'sBotCtrl')
		sBendCtrls = self._getComponentAttr(sComponent, 'lBendCtrls')
		sBendRvsCtrls = self._getComponentAttr(sComponent, 'lBendRvsCtrls')
		sTweakCtrls = self._getComponentAttr(sComponent, 'lTweakCtrls')

		self._lBendCtrls = componentInfo.decomposeStringToStrList(sBendCtrls)
		self._lBendRvsCtrls = componentInfo.decomposeStringToStrList(sBendRvsCtrls)
		self._lTweakCtrls = componentInfo.decomposeStringToStrList(sTweakCtrls)

		self.sTopCtrl = self._sTopCtrl
		self.sBotCtrl = self._sBotCtrl
		self._addAttributeFromList('sBendCtrl', self._lBendCtrls)
		self._addAttributeFromList('sBendRvsCtrl', self._lBendRvsCtrls)
		self._addAttributeFromList('sTweakCtrl', self._lTweakCtrls)

	def _getCtrlPasserMatrixOnNode(self, oCtrl, sNode):
		lMatrixLocal = apiUtils.getLocalMatrixInNode(oCtrl.sName, sNode)
		mMatrixLocal = apiUtils.convertListToMMatrix(lMatrixLocal)
		lMatrixPasser = apiUtils.convertMMatrixToList(mMatrixLocal.inverse())
		return lMatrixPasser

	def _connectCtrlToNode(self, oCtrl, sNode, sPlug, sMultMatrix):
		lMatrixLocal = apiUtils.getLocalMatrixInNode(oCtrl.sName, sNode)
		cmds.setAttr('%s.matrixIn[0]' %sMultMatrix, lMatrixLocal, type = 'matrix')
		cmds.connectAttr(sPlug, '%s.matrixIn[1]' %sMultMatrix)
		cmds.connectAttr('%s.inverseMatrix' %oCtrl.sZero, '%s.matrixIn[2]' %sMultMatrix)
		constraints.matrixConnect(sMultMatrix, [oCtrl.sPasser], 'matrixSum', lSkipScale = ['X', 'Y', 'Z'])







