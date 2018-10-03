########################################################
# base fk drive ik spline limb
# limb functions
#     -- spline ik tweaker
#     -- multi fk bend control
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
import riggingAPI.rigComponents.rigUtils.createDriveJoints as createDriveJoints
## kwarg class
class kwargsGenerator(baseIkSplineSolverLimb.kwargsGenerator):
	"""docstring for kwargsGenerator"""
	def __init__(self):
		super(kwargsGenerator, self).__init__()
		self.dKwargs = {'lBpBend': None}
		self.addKwargs()

class baseFkDriveIkSplineLimb(baseIkSplineSolverLimb.baseIkSplineSolverLimb):
	"""docstring for baseFkDriveIkSplineLimb"""
	def __init__(self, *args, **kwargs):
		super(baseFkDriveIkSplineLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpBend = kwargs.get('lBpBend', True)

	def createComponent(self):
		super(baseFkDriveIkSplineLimb, self).createComponent()

		## create temp controller
		sCrv = cmds.curve(p=[[0,0,0], [1,0,0]], k=[0,1], d=1, per = False, name = 'TEMP_CRV')
		sCtrlShape = naming.oName(sType = 'ctrl', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		controls.addCtrlShape([sCrv], sCtrlShape, bVis = False, dCtrlShapeInfo = None, bTop = False)
		cmds.addAttr(sCtrlShape, ln = 'tweakCtrlVis', at = 'long', min = 0, max = 1, dv = 0, keyable = False)
		cmds.setAttr('%s.tweakCtrlVis' %sCtrlShape, channelBox = True)

		## bend control

		lCtrls_bend = []
		sParent = self._sComponentControls
		for i, sBpBend in enumerate(self._lBpBend):
			oName = naming.oName(sBpBend)
			iRotateOrder = cmds.getAttr('%s.ro' %sBpBend)
			oCtrl_bend = controls.create(oName.sPart, sSide = oName.sSide, iIndex = i + 1, iStacks = self._iStacks, bSub = True, iRotateOrder = iRotateOrder, sParent = sParent, sShape = 'square', fSize = 6, lLockHideAttrs = self._lLockHideAttrs)
			cmds.delete(cmds.parentConstraint(sBpBend, oCtrl_bend.sZero, mo = False))
			lCtrls_bend.append(oCtrl_bend)
			sParent = oCtrl_bend.sOutput

		## connect tweak ctrls
		sMatrixPlug = lCtrls_bend[0].sMatrixOutputWorldPlug
		for i, sCtrl_tweak in enumerate(self._lCtrls):
			oCtrl_tweak = controls.oControl(sCtrl_tweak)
			lMatrixInverse = cmds.getAttr('%s.inverseMatrix' %oCtrl_tweak.sZero)

			
			sMultMatrix = naming.oName(sType = 'multMatrix', sSide = oCtrl_tweak.sSide, sPart = '%sMatrix' %oCtrl_tweak.sPart, iIndex = oCtrl_tweak.iIndex).sName
			sMultMatrix = cmds.createNode('multMatrix', name = sMultMatrix)
			cmds.connectAttr(lCtrls_bend[i].sMatrixOutputWorldPlug, '%s.matrixIn[0]' %sMultMatrix)
			if i > 0:
				cmds.connectAttr(sMatrixPlug, '%s.matrixIn[1]' %sMultMatrix)
			sMultMatrixInverse = naming.oName(sType = 'multMatrix', sSide = oCtrl_tweak.sSide, sPart = '%sMatrixInverse' %oCtrl_tweak.sPart, iIndex = oCtrl_tweak.iIndex).sName
			sMultMatrixInverse = cmds.createNode('multMatrix', name = sMultMatrixInverse)
			cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.matrixIn[0]' %sMultMatrixInverse)
			cmds.setAttr('%s.matrixIn[1]' %sMultMatrixInverse, lMatrixInverse, type = 'matrix')
			constraints.matrixConnect(sMultMatrixInverse, [oCtrl_tweak.sPasser], 'matrixSum', lSkipScale = ['X', 'Y', 'Z'])
			sMatrixPlug = '%s.matrixSum' %sMultMatrix
			cmds.connectAttr('%s.tweakCtrlVis' %sCtrlShape, '%s.v' %oCtrl_tweak.sZero)

		#### twist matrix connect
		lMultMatrixTwist = []
		oCtrl_tweakTop = controls.oControl(self._lCtrls[-1])
		oCtrl_tweakBot = controls.oControl(self._lCtrls[0])
		lCtrl_tweak = [oCtrl_tweakTop, oCtrl_tweakBot]
		for i, sPos in enumerate(['Top', 'Bot']):
			sMultMatrixTwist = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sMatrixTwist%s' %(self._sName, sPos), iIndex = self._iIndex).sName)
			lMatrix = apiUtils.getLocalMatrixInNode([self._lJnts[-1], self._lJnts[0]][i], lCtrl_tweak[i].sName)
			cmds.setAttr('%s.matrixIn[0]' %sMultMatrixTwist, lMatrix, type = 'matrix')
			cmds.connectAttr(lCtrl_tweak[i].sMatrixOutputWorldPlug, '%s.matrixIn[1]' %sMultMatrixTwist)
			lMultMatrixTwist.append(sMultMatrixTwist)
		cmds.setAttr('%s.dTwistControlEnable' %self._sIkHnd, 1)
		cmds.setAttr('%s.dWorldUpType' %self._sIkHnd, 4)
		for i, sMultMatrixTwist in enumerate(lMultMatrixTwist):
			cmds.connectAttr('%s.matrixSum' %sMultMatrixTwist, '%s.%s' %(self._sIkHnd, ['dWorldUpMatrixEnd', 'dWorldUpMatrix'][i]))

		self._lTweakCtrls = self._lCtrls
		self._lBendCtrls = []
		for oCtrl_bend in lCtrls_bend:
			self._lBendCtrls.append(oCtrl_bend.sName)
		self._lCtrls += self._lBendCtrls
		controls.addCtrlShape(self._lCtrls, sCtrlShape, bVis = False, dCtrlShapeInfo = None, bTop = False)
		cmds.delete(sCrv)

		## write component info
		self._writeGeneralComponentInfo('baseFkDriveIkSplineLimb', self._lJnts, self._lCtrls, self._lBindJnts, self._lBindRootJnts)

		sBendCtrls = componentInfo.composeListToString(self._lBendCtrls)
		sTweakCtrls = componentInfo.composeListToString(self._lTweakCtrls)

		lValues = [sBendCtrls,sTweakCtrls]
		for i, sAttr in enumerate(['lBendCtrls', 'lTweakCtrls']):
			cmds.addAttr(self._sComponentMaster, ln = sAttr, dt = 'string')
			cmds.setAttr('%s.%s' %(self._sComponentMaster, sAttr), lValues[i], lock = True, type = 'string')

		self._getComponentInfo(self._sComponentMaster)

	def _getComponentInfo(self, sComponent):
		super(baseFkDriveIkSplineLimb, self)._getComponentInfo(sComponent)

		sBendCtrls = self._getComponentAttr(sComponent, 'lBendCtrls')
		sTweakCtrls = self._getComponentAttr(sComponent, 'lTweakCtrls')

		self._lBendCtrls = componentInfo.decomposeStringToStrList(sBendCtrls)
		self._lTweakCtrls = componentInfo.decomposeStringToStrList(sTweakCtrls)

		self._addAttributeFromList('sBendCtrl', self._lBendCtrls)
		self._addAttributeFromList('sTweakCtrl', self._lTweakCtrls)