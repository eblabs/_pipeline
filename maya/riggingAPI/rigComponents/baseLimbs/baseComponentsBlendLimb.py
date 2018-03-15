#####################################################
# base components blend limb
# this limb should blend several rigs into one rig
#####################################################
## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import namingAPI.namingDict as namingDict
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import common.importer as importer
import common.dataInfo as dataInfo
import riggingAPI.joints as joints
import riggingAPI.controls as controls
import modelingAPI.curves as curves
import riggingAPI.constraints as constraints

import riggingAPI.rigComponents.baseLimb.baseJointsLimb as baseJointsLimb
## import rig utils
import riggingAPI.rigComponents.rigUtils.createDriveJoints as createDriveJoints

## kwarg class
class kwargsGenerator(baseJointsLimb.kwargsGenerator):
	"""docstring for kwargsGenerator"""
	def __init__(self):
		super(kwargsGenerator, self).__init__()
		self.dKwargs = {'dComponents': {}}
		self.addKwargs()

class baseComponentsBlendLimb(baseJointsLimb.baseJointsLimb):
	"""docstring for baseComponentsBlendLimb"""
	def __init__(self, *args, **kwargs):
		super(baseComponentsBlendLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._dComponents = kwargs.get('dComponents', {})

			## dComponents example
			#{Key name: 
			#  { 'sModulePath': module path,
			#	 'sModuleName': module name
			#	 'dKwargs': kwargs,}
			#}
	@property
	def dComponentLimbs(self):
		return self._dComponentLimbs

	def createComponent(self):
		super(baseComponentsBlendLimb, self).createComponent()

		cmds.setAttr('%s.subComponents' %self._sComponentMaster, 1)

		lJnts, lBindJnts = createDriveJoints.createDriveJoints(self._lBpJnts, sParent = self._sComponentDrvJoints, sSuffix = '', bBind = self._bBind, sBindParent = self._sBindParent)

		## create temp controller
		sCrv = cmds.curve(p=[[0,0,0], [1,0,0]], k=[0,1], d=1, per = False, name = 'TEMP_CRV')
		sCtrlShape = naming.oName(sType = 'ctrl', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		controls.addCtrlShape([sCrv], sCtrlShape, bVis = False, dCtrlShapeInfo = None, bTop = False)

		sEnumName = ''
		iIndexCustom = 90
		lKey = self._dComponents.keys()
		lIndex = []
		lIndexOrder = []
		for sKey in lKey:
			if namingDict.spaceDict.has_key(sKey):
				iIndexKey = namingDict.spaceDict[sKey]
			else:
				iIndexKey = iIndexCustom
				iIndexCustom += 1
			lIndex.append(iIndexKey)
			lIndexOrder.append(iIndexKey)

		lIndexOrder.sort()
		for iIndex in lIndexOrder:
			iNum = lIndex.index(iIndex)
			sEnumName += '%s=%d:' %(lKey[iNum], iIndex)

		## add attrs
		cmds.addAttr(sCtrlShape, ln = 'moduleA', at = 'enum', keyable = True, en = sEnumName[:-1], dv = lIndexOrder[0])
		cmds.addAttr(sCtrlShape, ln = 'moduleB', at = 'enum', keyable = True, en = sEnumName[:-1], dv = lIndexOrder[0])
		cmds.addAttr(sCtrlShape, ln = 'moduleBlend', at = 'float', keyable = True, min = 0, max = 10)
		sMultBlend = naming.oName(sType = 'multDoubleLinear', sSide = self._sSide, sPart = '%sModuleBlendOutput' %self._sName, iIndex = self._iIndex).sName
		cmds.createNode('multDoubleLinear', name = sMultBlend)
		cmds.connectAttr('%s.moduleBlend' %sCtrlShape, '%s.input1' %sMultBlend)
		cmds.setAttr('%s.input2' %sMultBlend, 0.1, lock = True)
		sRvsBlend = naming.oName(sType = 'reverse', sSide = self._sSide, sPart = '%sModuleBlendOutput' %self._sName, iIndex = self._iIndex).sName
		cmds.createNode('reverse', name = sRvsBlend)
		cmds.connectAttr('%s.output' %sMultBlend, '%s.inputX' %sRvsBlend)
		sCondBlend = naming.oName(sType = 'condition', sSide = self._sSide, sPart = '%sModuleBlendIndex' %self._sName, iIndex = self._iIndex).sName
		cmds.createNode('condition', name = sCondBlend)
		cmds.connectAttr('%s.output' %sMultBlend, '%s.firstTerm' %sCondBlend)
		cmds.setAttr('%s.secondTerm' %sCondBlend, 0.5, lock = True)
		cmds.setAttr('%s.operation' %sCondBlend, 4)
		cmds.connectAttr('%s.moduleA' %sCtrlShape, '%s.colorIfTrueR' %sCondBlend)
		cmds.connectAttr('%s.moduleB' %sCtrlShape, '%s.colorIfFalseR' %sCondBlend)

		## choice node
		lNodes = []
		for sJnt in lJnts:
			oJntName = naming.oName(sJnt)
			sChoiceA = naming.oName(sType = 'choice', sSide = oJntName.sSide, sPart = '%sA' %oJntName.sPart, iIndex = oJntName.iIndex).sName
			sChoiceB = naming.oName(sType = 'choice', sSide = oJntName.sSide, sPart = '%sB' %oJntName.sPart, iIndex = oJntName.iIndex).sName
			sWtAddMatrix = naming.oName(sType = 'wtAddMatrix', sSide = oJntName.sSide, sPart = oJntName.sPart, iIndex = oJntName.iIndex).sName
			cmds.createNode('choice', name = sChoiceA)
			cmds.createNode('choice', name = sChoiceB)
			cmds.createNode('wtAddMatrix', name = sWtAddMatrix)
			cmds.connectAttr('%s.moduleA' %sCtrlShape, '%s.selector' %sChoiceA)
			cmds.connectAttr('%s.moduleB' %sCtrlShape, '%s.selector' %sChoiceB)
			cmds.connectAttr('%s.output' %sChoiceA, '%s.wtMatrix[0].matrixIn' %sWtAddMatrix)
			cmds.connectAttr('%s.output' %sChoiceB, '%s.wtMatrix[1].matrixIn' %sWtAddMatrix)
			cmds.connectAttr('%s.outputX' %sRvsBlend, '%s.wtMatrix[0].weightIn' %sWtAddMatrix)
			cmds.connectAttr('%s.output' %sMultBlend, '%s.wtMatrix[1].weightIn' %sWtAddMatrix)
			constraints.matrixConnectJnt(sWtAddMatrix, sJnt, 'matrixSum')
			lNodes.append([sChoiceA, sChoiceB])

		dModuleInfo = {}
		for sKey in self._dComponents.keys():
			sModulePath = self._dComponents[sKey]['sModulePath']
			sModuleName = self._dComponents[sKey]['sModuleName']
			dKwargs = self._dComponents[sKey]['dKwargs']
			dKwargs.update({'bInfo': False, 'lBpJnts': self._lBpJnts, 'sParent': self._sComponentSubComponents, 'sName': '%s%s%s' %(self._sName, sKey[0].upper(), sKey[1:]), 'sSide': self._sSide, 'iIndex': self._iIndex}, 'iTwistJntNum': 0)

			oModule = importer.importModule(sModulePath)
			oLimb = getattr(oModule, sModuleName)(**dKwargs)
			oLimb.createComponent()

			## connect attrs
			attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sDriver = self._sComponentPasser, sDriven = oLimb._sComponentPasser, bForce = True)
			attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sDriver = self._sComponentSpace, sDriven = oLimb._sComponentSpace, bForce = True)
			for sAttr in ['inputMatrix', 'inputMatrixOffset', 'deformGeo']:
				cmds.connectAttr('%s.%s' %(self._sComponentMaster, sAttr), '%s.%s' %(oLimb._sComponentMaster, sAttr))

			controls.addCtrlShape(oLimb._lCtrls, sCtrlShape, bVis = False, dCtrlShapeInfo = None, bTop = False)

			iNum = lKey.index(sKey)
			iIndex = lIndex[iNum]
			for i, sJnt in enumerate(lJnts):
				cmds.connectAttr('%s.matrix' %oLimb._lJnts[i], '%s.input[%d]' %(lNodes[i][0], iIndex))
				cmds.connectAttr('%s.matrix' %oLimb._lJnts[i], '%s.input[%d]' %(lNodes[i][1], iIndex))

			## control vis
			sCondCtrlVis = naming.oName(sType = 'condition', sSide = self._sSide, sPart = '%s%sCtrlVis' %(self._sName, sKey), iIndex = self._iIndex).sName
			cmds.createNode('condition', name = sCondCtrlVis)
			cmds.connectAttr('%s.outColorR' %sCondBlend, '%s.firstTerm' %sCondCtrlVis)
			cmds.setAttr('%s.secondTerm' %sCondCtrlVis, iIndex, lock = True)
			cmds.setAttr('%s.colorIfTrueR' %sCondCtrlVis, 1, lock = True)
			cmds.setAttr('%s.colorIfFalseR' %sCondCtrlVis, 0, lock = True)
			cmds.connectAttr('%s.outColorR' %sCondCtrlVis, '%s.controls' %oLimb._sComponentMaster)

			dModuleInfo.update({sKey: {'sModulePath': sModulePath, 'sModuleName': sModuleName, 'sComponentNode': oLimb._sComponentMaster}})

		cmds.delete(sCrv)

		## write component info
		self._writeGeneralComponentInfo('baseComponentsBlendLimb', lJnts, [sCtrlShape], lBindJnts)
		cmds.addAttr(self._sComponentMaster, ln = 'dModuleInfo', dt = 'string')
		cmds.setAttr('%s.dModuleInfo' %self._sComponentMaster, str(dModuleInfo), type = 'string', lock = True)
		## output matrix
		if self._bInfo:
			self._writeOutputMatrixInfo(lJnts)

		self._getComponentInfo(self._sComponentMaster)

	def _getComponentInfo(self, sComponent):
		super(baseComponentsBlendLimb, self)._getComponentInfo(sComponent)
		sModuleInfo = cmds.getAttr('%s.dModuleInfo' %sComponent)
		dModuleInfo = dataInfo.convertStringToDict(sModuleInfo)
		self._dComponentLimbs = {}

		for sKey in dModuleInfo.keys():
			sModulePath = dModuleInfo[sKey]['sModulePath']
			sModuleName = dModuleInfo[sKey]['sModuleName']
			sComponentNode = dModuleInfo[sKey]['sComponentNode']
			oModule = importer.importModule(sModulePath)
			oLimb = getattr(oModule, sModuleName)(sComponentNode)
			self._dComponentLimbs.update({sKey: oLimb})
