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
import riggingAPI.joints as joints
import riggingAPI.controls as controls
import modelingAPI.curves as curves
import riggingAPI.constraints as constraints

import riggingAPI.rigComponents.baseComponent as baseComponent

class baseComponentsBlendLimb(baseComponent.baseComponent):
	"""docstring for baseComponentsBlendLimb"""
	def __init__(self, *args, **kwargs):
		super(baseComponentsBlendLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpJnts = kwargs.get('lBpJnts', None)
			self._bBind = kwargs.get('bBind', False)
			self._dComponents = kwargs.get('dComponents', {})

			## dComponents example
			#{Key name: 
			#  { 'sModulePath': module path,
			#	 'sModuleName': module name
			#	 'dKwargs': kwargs,}
			#}

	def createComponent(self):
		super(baseComponentsBlendLimb, self).createComponent()

		sParent_jnt = self._sComponentDrvJoints
		sParent_bind = self._sComponentBindJoints
		lJnts = []
		lBindJnts = []

		for i, sBpJnt in enumerate(self._lBpJnts):
			## jnt
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			sParent_jnt = sJnt
			lJnts.append(sJnt)

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

		## create temp controller
		sCrv = cmds.curve(p=[[0,0,0], [1,0,0]], k=[0,1], d=1, per = False, name = 'TEMP_CRV')
		sCtrlShape = naming.oName(sType = 'ctrl', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		curves.addCtrlShape([sCrv], sCtrlShape, bVis = False, dCtrlShapeInfo = None, bTop = False)

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
		cmds.addAttr(sCtrlShape, ln = 'moduleBlend', at = 'float', keyable = True, min = 0, max = 1)
		sMultBlend = naming.oName(sType = 'multDoubleLinear', sSide = self._sSide, sPart = '%sModuleBlendOutput' %self._sName, iIndex = self._iIndex).sName
		cmds.createNode('multDoubleLinear', name = sMultBlend)
		cmds.connectAttr('%s.moduleBlend' %sCtrlShape, '%s.input1' %sMultBlend)
		cmds.setAttr('%s.input2' %sMultBlend, 0.1, lock = True)
		sRvsBlend = naming.oName(sType = 'reverse', sSide = self._sSide, sPart = '%sModuleBlendOutput' %self._sName, iIndex = self._iIndex).sName
		cmds.connectAttr('%s.output' %sMultBlend, '%s.inputX' %sRvsBlend)
		sCondBlend = naming.oName(sType = 'condition', sSide = self._sSide, sPart = '%sModuleBlendIndex' %self._sName, iIndex = self._iIndex).sName
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
			cmds.connectAttr('%s.output' %sRvsBlend, '%s.wtMatrix[0].weightIn' %sWtAddMatrix)
			cmds.connectAttr('%s.output' %sMultBlend, '%s.wtMatrix[1].weightIn' %sWtAddMatrix)
			constraints.matrixConnect(sWtAddMatrix, [sJnt], 'matrixSum')
			lNodes.append([sChoiceA, sChoiceB])

		dModuleInfo = {}
		for sKey in self._dComponents.keys():
			sModulePath = self._dComponents[sKey]['sModulePath']
			sModuleName = self._dComponents[sKey]['sModuleName']
			dKwargs = self._dComponents[sKey]['dKwargs']
			dKwargs.update({'bInfo': False, 'lBpJnts': self._lBpJnts, 'sParent': self._sComponentSubComponents, 'sName': '%s%s%s' %(self._sName, sKey[0].upper(), sKey[1:]), 'sSide': self._sSide, 'iIndex': self._iIndex})

			oModule = __import__(sModulePath)
			oLimb = getattr(oMdule, sModuleName)(**dKwargs)
			oLimb.createComponent()

			## connect attrs
			attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sDriver = self._sComponentPasser, sDriven = oLimb._sComponentPasser, bForce = True)
			attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sDriver = self._sComponentSpace, sDriven = oLimb._sComponentSpace, bForce = True)
			for sAttr in ['inputMatrix', 'inputMatrixOffset', 'deformGeo']:
				cmds.connectAttr('%s.%s' %(self._sComponentMaster, sAttr), '%s.%s' %(oLimb._sComponentMaster, sAttr))

			for sCtrl in oLimb._lCtrls:
				controls.addCtrlShape(sCtrl, sCtrlShape, bVis = False, dCtrlShapeInfo = None, bTop = False)

			iNum = lKey.index(sKey)
			iIndex = lIndex[iNum]
			for i, sJnt in enumerate(lJnts):
				cmds.connectAttr('%s.matrix' %oLimb._lJnts[i], '%s.input[%d]' %(lNodes[0][0], iIndex))
				cmds.connectAttr('%s.matrix' %oLimb._lJnts[i], '%s.input[%d]' %(lNodes[0][1], iIndex))

			## control vis
			sCondCtrlVis = naming.oName(sType = 'condition', sSide = self._sSide, sPart = '%s%sCtrlVis' %(self._sName, sKey), iIndex = self._iIndex).sName
			cmds.createNode('condition', name = sCondCtrlVis)
			cmds.connectAttr('%s.outColorR' %sCondBlend, '%s.firstTerm' %sCondCtrlVis)
			cmds.setAttr('%s.secondTerm' %sCondCtrlVis, iIndex, lock = True)
			cmds.setAttr('%s.colorIfTrueR' %sCondCtrlVis, 1, lock = True)
			cmds.setAttr('%s.colorIfFalseR' %sCondCtrlVis, 0, lock = True)
			cmds.connectAttr('%s.outColorR' %sCondCtrlVis, '%s.controls' %oLimb._sComponentMaster)

			dModuleInfo.update({sKey: {'iIndex': iIndex, 'sModulePath': sModulePath, 'sModuleName': sModuleName, 'sComponentMaster': oLimb._sComponentMaster}})

		cmds.delete(sCrv)

		## write component info
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, 'baseComponentsBlendLimb', type = 'string', lock = True)
		cmds.setAttr('%s.iJointCount' %self._sComponentMaster, len(lJnts), lock = True)
		cmds.setAttr('%s.sControls' %self._sComponentMaster, sCtrlShape, type = 'string', lock = True)
		if self._bBind:
			sBindString = ''
			for sBind in lBindJnts:
				sBindString += '%s,' %sBind
			cmds.setAttr('%s.sBindJoints' %self._sComponentMaster, sBindString[:-1], type = 'string', lock = True)

		## output matrix
		if self._bInfo:
			self._writeOutputMatrixInfo(lJnts, bHierarchy = True)

		self._getComponentInfo(self._sComponentMaster)