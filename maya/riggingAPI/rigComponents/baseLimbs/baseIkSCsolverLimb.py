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
import riggingAPI.constraints as constraints

import riggingAPI.rigComponents.baseLimbs.baseJointsLimb as baseJointsLimb
## import rig utils
import riggingAPI.rigComponents.rigUtils.createDriveJoints as createDriveJoints
import riggingAPI.rigComponents.rigUtils.addTwistJoints as addTwistJoints

## kwarg class
class kwargsGenerator(baseJointsLimb.kwargsGenerator):
	"""docstring for kwargsGenerator"""
	def __init__(self):
		super(kwargsGenerator, self).__init__()
		self.dKwargs = {'bStretch': False,
						'lLimitFactor': [0, 10],
						'lFactorY': [2, 0.5],
						'lFactorZ': [2, 0.5]}
		self.addKwargs()

class baseIkSCsolverLimb(baseJointsLimb.baseJointsLimb):
	"""docstring for baseIkSCsolverLimb"""
	def __init__(self, *args, **kwargs):
		super(baseIkSCsolverLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._bStretch = kwargs.get('bStretch', False)
			self._lLimitFactor = kwargs.get('lLimitFactor', [0, 10])
			self._lFactorY = kwargs.get('lFactorY', [2, 0.5])
			self._lFactorZ = kwargs.get('lFactorZ', [2, 0.5])
	
	def createComponent(self):
		super(baseIkSCsolverLimb, self).createComponent()

		sParent_jnt = self._sComponentJoints
		sParent_ctrl = self._sComponentControls
		lJnts = []
		lCtrls = []
		lBindJnts = []

		## controls
		oCtrlRoot = controls.create('%sRoot' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, sParent = self._sComponentControls, sPos = self._lBpJnts[0], sShape = 'cube', fSize = 8, lLockHideAttrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
		lCtrls.append(oCtrlRoot.sName)
		oCtrlAim = controls.create('%sAim' %self._sName, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = True, sParent = self._sComponentControls, sPos = self._lBpJnts[-1], sShape = 'cube', fSize = 8, lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		lCtrls.append(oCtrlAim.sName)

		## put ik joint chain locally
		sGrp_ikJnts = transforms.createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sSCJointsLocal' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld)
		sParent_jntLocal = sGrp_ikJnts
		lJntsLocal = []

		lJntsLocal, lBindJnts = createDriveJoints.createDriveJoints(self._lBpJnts, sParent = sGrp_ikJnts, sSuffix = 'IkSCLocal', bBind = False)
		
		## stretch
		if self._bStretch:
			## add stretch attr
			attributes.addDivider([oCtrlAim.sName], 'stretch')
			cmds.addAttr(oCtrlAim.sName, ln = 'limitFactorPos', at = 'float', min = 1, dv = self._lLimitFactor[1], keyable = True)
			cmds.addAttr(oCtrlAim.sName, ln = 'limitFactorNeg', at = 'float', min = 0, max = 1, dv = self._lLimitFactor[0], keyable = True)
			cmds.addAttr(oCtrlAim.sName, ln = 'factorYPos', at = 'float', min = 0, dv = self._lFactorY[1], keyable = True)
			cmds.addAttr(oCtrlAim.sName, ln = 'factorZPos', at = 'float', min = 0, dv = self._lFactorZ[1], keyable = True)
			cmds.addAttr(oCtrlAim.sName, ln = 'factorYNeg', at = 'float', min = 0, dv = self._lFactorY[0], keyable = True)
			cmds.addAttr(oCtrlAim.sName, ln = 'factorZNeg', at = 'float', min = 0, dv = self._lFactorZ[0], keyable = True)
			cmds.addAttr(oCtrlAim.sName, ln = 'stretchLengthOrig', at = 'float')

			sGrp_stretch = transforms.createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sSCJointStretch' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld)
			
			## distance measure
			sDistance = cmds.createNode('distanceBetween', name = naming.oName(sType = 'distanceBetween', sSide = self._sSide, sPart = '%sStretch' %self._sName, iIndex = self._iIndex).sName)
			sNullRoot = transforms.createTransformNode(naming.oName(sType = 'null', sSide = self._sSide, sPart = '%sRootStretch' %self._sName, iIndex = self._iIndex).sName, sPos = oCtrlRoot.sName, sParent = sGrp_stretch)
			sNullAim = transforms.createTransformNode(naming.oName(sType = 'null', sSide = self._sSide, sPart = '%sAimStretch' %self._sName, iIndex = self._iIndex).sName, sPos = oCtrlAim.sName, sParent = sGrp_stretch)
			constraints.matrixConnect(oCtrlRoot.sName, [sNullRoot], 'matrixOutputWorld', lSkipRotate = ['X', 'Y', 'Z'], lSkipScale = ['X', 'Y', 'Z'])
			constraints.matrixConnect(oCtrlAim.sName, [sNullAim], 'matrixOutputWorld', lSkipRotate = ['X', 'Y', 'Z'], lSkipScale = ['X', 'Y', 'Z'])

			cmds.connectAttr('%s.t' %sNullRoot, '%s.point1' %sDistance)
			cmds.connectAttr('%s.t' %sNullAim, '%s.point2' %sDistance)
			fDis = cmds.getAttr('%s.distance' %sDistance)
			cmds.setAttr('%s.stretchLengthOrig' %oCtrlAim.sName, fDis, lock = True)

			sDivide = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = self._sSide, sPart = '%sStretchFactor' %self._sName, iIndex = self._iIndex).sName)
			cmds.setAttr('%s.operation' %sDivide, 2)
			cmds.connectAttr('%s.distance' %sDistance, '%s.input1X' %sDivide)
			cmds.connectAttr('%s.stretchLengthOrig' %oCtrlAim.sName, '%s.input2X' %sDivide)

			sConditionStretchOutput = cmds.createNode('condition', name = naming.oName(sType = 'condition', sSide = self._sSide, sPart = '%sStretchOutput' %self._sName, iIndex = self._iIndex).sName)
			cmds.connectAttr('%s.outputX' %sDivide, '%s.firstTerm' %sConditionStretchOutput)
			cmds.setAttr('%s.secondTerm' %sConditionStretchOutput, 1)
			cmds.setAttr('%s.operation' %sConditionStretchOutput, 2)

			sConditionStretchPos = cmds.createNode('condition', name = naming.oName(sType = 'condition', sSide = self._sSide, sPart = '%sStretchPos' %self._sName, iIndex = self._iIndex).sName)
			cmds.connectAttr('%s.outputX' %sDivide, '%s.firstTerm' %sConditionStretchPos)
			cmds.connectAttr('%s.limitFactorPos' %oCtrlAim.sName, '%s.secondTerm' %sConditionStretchPos)
			cmds.setAttr('%s.operation' %sConditionStretchPos, 4)
			cmds.connectAttr('%s.outputX' %sDivide, '%s.colorIfTrueR' %sConditionStretchPos)
			cmds.connectAttr('%s.limitFactorPos' %oCtrlAim.sName, '%s.colorIfFalseR' %sConditionStretchPos)
			cmds.connectAttr('%s.outColorR' %sConditionStretchPos, '%s.colorIfTrueR' %sConditionStretchOutput)

			sConditionStretchNeg = cmds.createNode('condition', name = naming.oName(sType = 'condition', sSide = self._sSide, sPart = '%sStretchNeg' %self._sName, iIndex = self._iIndex).sName)
			cmds.connectAttr('%s.outputX' %sDivide, '%s.firstTerm' %sConditionStretchNeg)
			cmds.connectAttr('%s.limitFactorNeg' %oCtrlAim.sName, '%s.secondTerm' %sConditionStretchNeg)
			cmds.setAttr('%s.operation' %sConditionStretchNeg, 2)
			cmds.connectAttr('%s.outputX' %sDivide, '%s.colorIfTrueR' %sConditionStretchNeg)
			cmds.connectAttr('%s.limitFactorNeg' %oCtrlAim.sName, '%s.colorIfFalseR' %sConditionStretchNeg)
			cmds.connectAttr('%s.outColorR' %sConditionStretchNeg, '%s.colorIfFalseR' %sConditionStretchOutput)

			for i, lFactors in enumerate([self._lFactorY, self._lFactorZ]):
				sAxis = ['Y', 'Z'][i]
				sRemapPos = cmds.createNode('remapValue', name = naming.oName(sType = 'remapValue', sSide = self._sSide, sPart = '%sStretch%sPos' %(self._sName, sAxis), iIndex = self._iIndex).sName)
				sRemapNeg = cmds.createNode('remapValue', name = naming.oName(sType = 'remapValue', sSide = self._sSide, sPart = '%sStretch%sNeg' %(self._sName, sAxis), iIndex = self._iIndex).sName)
				cmds.connectAttr('%s.outputX' %sDivide, '%s.inputValue' %sRemapPos)
				cmds.connectAttr('%s.outputX' %sDivide, '%s.inputValue' %sRemapNeg)
				cmds.setAttr('%s.inputMin' %sRemapPos, 1)
				cmds.connectAttr('%s.limitFactorPos' %oCtrlAim.sName, '%s.inputMax' %sRemapPos)
				cmds.connectAttr('%s.limitFactorNeg' %oCtrlAim.sName, '%s.inputMin' %sRemapNeg)
				cmds.setAttr('%s.inputMax' %sRemapNeg, 1)
				cmds.setAttr('%s.outputMin' %sRemapPos, 1)
				cmds.setAttr('%s.outputMax' %sRemapNeg, 1)
				cmds.connectAttr('%s.factor%sPos' %(oCtrlAim.sName, sAxis), '%s.outputMax' %sRemapPos)
				cmds.connectAttr('%s.factor%sNeg' %(oCtrlAim.sName, sAxis), '%s.outputMin' %sRemapNeg)
				cmds.connectAttr('%s.outValue' %sRemapPos, '%s.colorIfTrue%s' %(sConditionStretchOutput, ['G', 'B'][i]))
				cmds.connectAttr('%s.outValue' %sRemapNeg, '%s.colorIfFalse%s' %(sConditionStretchOutput, ['G', 'B'][i]))

			sMultStretchX = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'multDoubleLinear', sSide = self._sSide, sPart = '%sStretchX' %self._sName, iIndex = self._iIndex).sName)
			cmds.connectAttr('%s.stretchLengthOrig' %oCtrlAim.sName, '%s.input1' %sMultStretchX)
			cmds.connectAttr('%s.outColorR' %sConditionStretchOutput, '%s.input2' %sMultStretchX)

			cmds.connectAttr('%s.output' %sMultStretchX, '%s.tx' %lJntsLocal[-1])
			cmds.connectAttr('%s.outColorG' %sConditionStretchOutput, '%s.sy' %lJntsLocal[0])
			cmds.connectAttr('%s.outColorB' %sConditionStretchOutput, '%s.sz' %lJntsLocal[0])

		lJnts, lBindJnts = createDriveJoints.createDriveJoints(self._lBpJnts, sParent = self._sComponentJoints, sSuffix = 'IkSC', bBind = self._bBind)

		for i, sJntLocal in enumerate(lJntsLocal):
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.translate%s' %(sJntLocal, sAxis), '%s.translate%s' %(lJnts[i], sAxis))
				cmds.connectAttr('%s.rotate%s' %(sJntLocal, sAxis), '%s.rotate%s' %(lJnts[i], sAxis))
				cmds.connectAttr('%s.scale%s' %(sJntLocal, sAxis), '%s.scale%s' %(lJnts[i], sAxis))

		## ik handles
		sIkHnd = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sSCsolver' %self._sName, iIndex = self._iIndex).sName
		cmds.ikHandle(sj = lJntsLocal[0], ee = lJntsLocal[-1], sol = 'ikSCsolver', name = sIkHnd)

		#### offset group
		sGrpIk = transforms.createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sSCsolverOffset' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld, sPos = oCtrlAim.sName)
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
		if lBindJnts:
			self._lBindRootJnts = [lBindJnts[0]]
		else:
			self._lBindRootJnts = None

		## write component info
		self._writeGeneralComponentInfo('baseIkSCsolverLimb', lJnts, lCtrls, lBindJnts, self._lBindRootJnts)

		## output matrix
		if self._bInfo:
			self._writeOutputMatrixInfo(lJnts)

		## add twist joints
		addTwistJoints.twistJointsForLimb(self._iTwistJntNum, self._lSkipTwist, lJnts, self._lBpJnts, bBind = self._bBind, sNode = self._sComponentMaster, bInfo = self._bInfo)

		self._getComponentInfo(self._sComponentMaster)

	def _getComponentInfo(self, sComponent):
		super(baseIkSCsolverLimb, self)._getComponentInfo(sComponent)
		self.rootCtrl = self._lCtrls[0]
		self.ikCtrl = self._lCtrls[1]