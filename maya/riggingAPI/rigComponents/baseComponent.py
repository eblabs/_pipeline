#################################################
# base rig component
# this component should contain the rig module
# and have input and output attr on the master
# component node to connect with other components
#################################################
## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import namingAPI.namingDict as namingDict
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import riggingAPI.constraints as constraints
import riggingAPI.joints as joints
import riggingAPI.controls as controls
import riggingAPI.rigComponents.rigUtils.componentInfo as componentInfo
import riggingAPI.rigComponents.rigUtils.addObjAttrs as addObjAttrs
import common.debug as debug

## kwarg class
class kwargsGenerator(object):
	"""docstring for kwargsGenerator"""
	def __init__(self):
		super(kwargsGenerator, self).__init__()
		self.dKwargs = {'sName': None,
						'sSide': 'm',
						'iIndex': None,
						'sParent': None,
						'sConnectIn': None,
						'bInfo': True,
							}
		self.dKwargsAll = {}
		self.addKwargs()

	def addKwargs(self):
		for sKwarg, sKey in self.dKwargs.items():
			self.dKwargsAll.update({sKwarg: sKey})

						

## base component class
class baseComponent(object):
	"""docstring for baseComponent"""
	def __init__(self, *args, **kwargs):
		super(baseComponent, self).__init__()
		if args:
			self._getComponentInfo(args[0])
		else:
			self._sName = kwargs.get('sName', None)
			self._sSide = kwargs.get('sSide', 'm')
			self._iIndex = kwargs.get('iIndex', None)
			self._sParent = kwargs.get('sParent', None)
			self._bInfo = kwargs.get('bInfo', True)
			self._sWorldMatrixInput = kwargs.get('sWorldMatrixInput', None)

	@property
	def sComponentMaster(self):
		return self._sComponentMaster

	@property
	def sComponentType(self):
		return self._sComponentType

	@property
	def sComponentPasser(self):
		return self._sComponentPasser

	@property
	def sComponentSpace(self):
		return self._sComponentSpace

	@property
	def lControls(self):
		return self._lCtrls

	def createComponent(self):
		# create groups
		### master group
		sComponentMaster = naming.oName(sType = 'rigComponent', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentMaster, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sParent)

		### rig nodes world group
		sComponentRigNodesWorld = naming.oName(sType = 'rigNodesWorld', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentRigNodesWorld, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentMaster)

		### sub components group
		sComponentSubComponents = naming.oName(sType = 'subComponents', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentSubComponents, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentMaster)

		### inherits group
		sComponentInherits = naming.oName(sType = 'inherits', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentInherits, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentMaster)

		### xform group
		sComponentXform = naming.oName(sType = 'xform', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentXform, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentInherits)

		### passer group
		sComponentPasser = naming.oName(sType = 'passer', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentPasser, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentXform)

		### space group
		sComponentSpace = naming.oName(sType = 'space', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentSpace, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentPasser)

		## controls group
		sComponentControls = naming.oName(sType = 'controls', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentControls, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentSpace)
		
		### rig nodes local group
		sComponentRigNodesLocal = naming.oName(sType = 'rigNodesLocal', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentRigNodesLocal, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentSpace)

		# visibility switch
		### controls
		cmds.addAttr(sComponentMaster, ln = 'controls', at = 'long', min = 0, max = 1, keyable = False, dv = 1)
		cmds.setAttr('%s.controls' %sComponentMaster, channelBox = True)
		### rig nodes
		cmds.addAttr(sComponentMaster, ln = 'rigNodes', at = 'long', min = 0, max = 1, keyable = False, dv = 0)
		cmds.setAttr('%s.rigNodes' %sComponentMaster, channelBox = True)
		### sub components
		cmds.addAttr(sComponentMaster, ln = 'subComponents', at = 'long', min = 0, max = 1, keyable = False, dv = 0)
		cmds.setAttr('%s.subComponents' %sComponentMaster, channelBox = True)

		### connect attrs
		attributes.connectAttrs(['%s.controls' %sComponentMaster], ['%s.v' %sComponentControls], bForce = True)
		attributes.connectAttrs(['%s.rigNodes' %sComponentMaster, '%s.rigNodes' %sComponentMaster], ['%s.v' %sComponentRigNodesLocal, '%s.v' %sComponentRigNodesWorld], bForce = True)
		attributes.connectAttrs(['%s.subComponents' %sComponentMaster], ['%s.v' %sComponentSubComponents], bForce = True)
		
		# input attrs
		### input matrix
		cmds.addAttr(sComponentMaster, ln = 'inputMatrix', at = 'matrix')
		cmds.addAttr(sComponentMaster, ln = 'inputMatrixInverse', at = 'matrix')
		sMultMatrix = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sInputMatrix' %self._sName, iIndex = self._iIndex).sName
		sDecomposeMatrix = naming.oName(sType = 'decomposeMatrix', sSide = self._sSide, sPart = '%sInputMatrix' %self._sName, iIndex = self._iIndex).sName
		cmds.createNode('multMatrix', name = sMultMatrix)
		cmds.createNode('decomposeMatrix', name = sDecomposeMatrix)
		cmds.connectAttr('%s.inputMatrixInverse' %sComponentMaster, '%s.matrixIn[0]' %sMultMatrix)
		cmds.connectAttr('%s.inputMatrix' %sComponentMaster, '%s.matrixIn[1]' %sMultMatrix)
		cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.inputMatrix' %sDecomposeMatrix)
		for sAxis in ['X', 'Y', 'Z']:
			attributes.connectAttrs(['%s.outputTranslate%s' %(sDecomposeMatrix, sAxis), '%s.outputRotate%s' %(sDecomposeMatrix, sAxis), '%s.outputScale%s' %(sDecomposeMatrix, sAxis)], ['%s.translate%s' %(sComponentXform, sAxis), '%s.rotate%s' %(sComponentXform, sAxis), '%s.scale%s' %(sComponentXform, sAxis)], bForce = True)
		attributes.connectAttrs(['%s.outputShear' %sDecomposeMatrix], ['%s.shear' %sComponentXform], bForce = True)

		self._sComponentMaster = sComponentMaster
		self._sComponentXform = sComponentXform
		self._sComponentPasser = sComponentPasser
		self._sComponentSpace = sComponentSpace
		self._sComponentRigNodesWorld = sComponentRigNodesWorld
		self._sComponentSubComponents = sComponentSubComponents
		self._sComponentControls = sComponentControls
		self._sComponentRigNodesLocal = sComponentRigNodesLocal

		## add component info
		cmds.addAttr(sComponentMaster, ln = 'sComponentType', dt = 'string')
		cmds.setAttr('%s.sComponentType' %sComponentMaster, 'baseComponent', type = 'string')
		cmds.addAttr(sComponentMaster, ln = 'sComponentSpace', dt = 'string')
		cmds.setAttr('%s.sComponentSpace' %sComponentMaster, sComponentSpace, type = 'string', lock = True)
		cmds.addAttr(sComponentMaster, ln = 'sComponentPasser', dt = 'string')
		cmds.setAttr('%s.sComponentPasser' %sComponentMaster, sComponentPasser, type = 'string', lock = True)
		cmds.addAttr(sComponentMaster, ln = 'lWorldMatrix', dt = 'matrix')
		if self._sWorldMatrixInput:
			cmds.connectAttr(self._sWorldMatrixInput, '%s.lWorldMatrix' %sComponentMaster, f = True)
		self._sWorldMatrixPlug = '%s.lWorldMatrix' %sComponentMaster

	def connectComponents(self, sMatrixPlug):
		mMatrixOrig = apiUtils.createMMatrixFromTransformInfo()
		lMatrixOrig = apiUtils.convertMMatrixToList(mMatrixOrig)
		lMatrixIn = cmds.getAttr(sMatrixPlug)
		mMatrix = apiUtils.convertListToMMatrix(lMatrixIn)
		mMatrixInverse = mMatrix.inverse()
		lMatrixInInverse = apiUtils.convertMMatrixToList(mMatrixInverse)
		sMultMatrix = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sConnectIn' %self._sName, iIndex = self._iIndex).sName)
		cmds.setAttr('%s.matrixIn[0]' %sMultMatrix, lMatrixOrig, type = 'matrix')
		cmds.setAttr('%s.matrixIn[1]' %sMultMatrix, lMatrixInInverse, type = 'matrix')
		cmds.connectAttr(sMatrixPlug, '%s.matrixIn[2]' %sMultMatrix)
		cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.inputMatrix' %self._sComponentMaster, f = True)

	def addSpace(self, sCtrl, dSpace):
		#dSpace {'world': {'sPlug': 'object.matrixOutput', 'lType': ['t', 'r', 's'], 'lDefaultsA': ['t'], 'lDefaultsB': ['r']}}
		lKeys, lIndex, lPlugs, lDefaultsA, lDefaultsB = self._decomposeSpaceDict(dSpace)

		for i, sType in enumerate(['t', 'r', 's']):
			if lKeys[i]:
				if not cmds.attributeQuery('spaceA%s' %sType.upper(), node = sCtrl, ex = True):
					self._addSpaceAttr(sCtrl, sType, lKeys[i], lIndex[i], lPlugs[i], lDefaultsA[i], lDefaultsB[i])
				else:
					self._editSpaceAttr(sCtrl, sType, lKeys[i], lIndex[i], lPlugs[i], lDefaultsA[i], lDefaultsB[i])

	def _decomposeSpaceDict(self, dSpace):
		lKeys = []
		lIndex = []
		lPlugs = []
		lDefaultsA = []
		lDefaultsB = []
		
		dKeyIndex = {}
		iIndexCustom = 90

		for sPos in ['t', 'r', 's']:
			lKeys_pos = []
			lIndex_pos = []
			lPlugs_pos = []
			lDefaultsA_pos = None
			lDefaultsB_pos = None
			
			for sKey in dSpace.keys():
				if sPos in dSpace[sKey]['lType']:
					if namingDict.spaceDict.has_key(sKey):
						iIndexKey = namingDict.spaceDict[sKey]
					elif dKeyIndex.has_key(sKey):
						iIndexKey = dKeyIndex[sKey]
					else:
						iIndexKey = iIndexCustom
						iIndexCustom += 1
						dKeyIndex.update({sKey:iIndexKey})
					lKeys_pos.append(sKey)
					lIndex_pos.append(iIndexKey)
					lPlugs_pos.append(dSpace[sKey]['sPlug'])

					if dSpace[sKey]['lDefaultsA'] and sPos in dSpace[sKey]['lDefaultsA']:
						lDefaultsA_pos = iIndexKey
					if dSpace[sKey]['lDefaultsB'] and sPos in dSpace[sKey]['lDefaultsB']:
						lDefaultsB_pos = iIndexKey

			lKeys.append(lKeys_pos)
			lIndex.append(lIndex_pos)
			lPlugs.append(lPlugs_pos)
			lDefaultsA.append(lDefaultsA_pos)
			lDefaultsB.append(lDefaultsB_pos)

		return lKeys, lIndex, lPlugs, lDefaultsA, lDefaultsB




	def _addSpaceAttr(self, sCtrl, sType, lKeys, lIndex, lPlugs, iDefaultA, iDefaultB):
		oCtrl = controls.oControl(sCtrl)

		sEnumName = ''
		for i, sKey in enumerate(lKeys):
			sEnumName += '%s=%d:' %(sKey, lIndex[i])

		if iDefaultA == None:
			iDefaultA = lIndex[0]
		if iDefaultB == None:
			iDefaultB = lIndex[0]

		attributes.addDivider([sCtrl], 'space%s' %sType.upper())
		cmds.addAttr(sCtrl, ln = 'spaceA%s' %sType.upper(), nn = 'Space A %s' %sType.upper(), at = 'enum', keyable = True, en = sEnumName[:-1], dv = iDefaultA)
		cmds.addAttr(sCtrl, ln = 'spaceB%s' %sType.upper(), nn = 'Space B %s' %sType.upper(), at = 'enum', keyable = True, en = sEnumName[:-1], dv = iDefaultB)
		cmds.addAttr(sCtrl, ln = 'spaceBlend%s' %sType.upper(), at = 'float', keyable = True, min = 0, max = 10)
		sMultBlend = naming.oName(sType = 'multDoubleLinear', sSide = oCtrl.sSide, sPart = '%sSpaceBlendOutput%s' %(oCtrl.sPart, sType.upper()), iIndex = oCtrl.iIndex).sName
		cmds.createNode('multDoubleLinear', name = sMultBlend)
		cmds.connectAttr('%s.spaceBlend%s'%(sCtrl, sType.upper()), '%s.input1' %sMultBlend)
		cmds.setAttr('%s.input2' %sMultBlend, 0.1, lock = True)
		sRvsBlend = naming.oName(sType = 'reverse', sSide = oCtrl.sSide, sPart = '%sSpaceBlendOutput%s' %(oCtrl.sPart, sType.upper()), iIndex = oCtrl.iIndex).sName
		cmds.createNode('reverse', name = sRvsBlend)
		cmds.connectAttr('%s.output' %sMultBlend, '%s.inputX' %sRvsBlend)
		## choice
		sChoiceA = naming.oName(sType = 'choice', sSide = oCtrl.sSide, sPart = '%sSpaceA%s' %(oCtrl.sPart, sType.upper()), iIndex = oCtrl.iIndex).sName
		sChoiceB = naming.oName(sType = 'choice', sSide = oCtrl.sSide, sPart = '%sSpaceB%s' %(oCtrl.sPart, sType.upper()), iIndex = oCtrl.iIndex).sName
		sWtAddMatrix = naming.oName(sType = 'wtAddMatrix', sSide = oCtrl.sSide, sPart = '%sSpace%s' %(oCtrl.sPart, sType.upper()), iIndex = oCtrl.iIndex).sName
		cmds.createNode('choice', name = sChoiceA)
		cmds.createNode('choice', name = sChoiceB)
		cmds.createNode('wtAddMatrix', name = sWtAddMatrix)
		cmds.connectAttr('%s.spaceA%s' %(sCtrl, sType.upper()), '%s.selector' %sChoiceA)
		cmds.connectAttr('%s.spaceB%s' %(sCtrl, sType.upper()), '%s.selector' %sChoiceB)
		cmds.connectAttr('%s.output' %sChoiceA, '%s.wtMatrix[0].matrixIn' %sWtAddMatrix)
		cmds.connectAttr('%s.output' %sChoiceB, '%s.wtMatrix[1].matrixIn' %sWtAddMatrix)
		cmds.connectAttr('%s.outputX' %sRvsBlend, '%s.wtMatrix[0].weightIn' %sWtAddMatrix)
		cmds.connectAttr('%s.output' %sMultBlend, '%s.wtMatrix[1].weightIn' %sWtAddMatrix)
		sMultMatrix = naming.oName(sType = 'multMatrix', sSide = oCtrl.sSide, sPart = '%sSpace%s' %(oCtrl.sPart, sType.upper()), iIndex = oCtrl.iIndex).sName
		cmds.createNode('multMatrix', name = sMultMatrix)
		cmds.connectAttr('%s.matrixSum' %sWtAddMatrix, '%s.matrixIn[0]' %sMultMatrix)
		cmds.connectAttr('%s.worldInverseMatrix[0]' %oCtrl.sPasser, '%s.matrixIn[1]' %sMultMatrix)
		cmds.connectAttr(self._sWorldMatrixPlug, '%s.matrixIn[2]' %sMultMatrix)

		for i, sPlug in enumerate(lPlugs):
			sPlug_space = self._spaceMatrix(sCtrl, sPlug, lIndex[i])
			cmds.connectAttr(sPlug_space, '%s.input[%d]' %(sChoiceA, lIndex[i]), f = True)
			cmds.connectAttr(sPlug_space, '%s.input[%d]' %(sChoiceB, lIndex[i]), f = True)

		lSkipTranslate = ['x', 'y', 'z']
		lSkipRotate = ['x', 'y', 'z']
		lSkipScale = ['x', 'y', 'z']

		if sType == 't':
			lSkipTranslate = []
		elif sType == 'r':
			lSkipRotate = []
		else:
			lSkipScale = []
		constraints.matrixConnect(sMultMatrix, [oCtrl.sSpace], 'matrixSum', lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate, lSkipScale = lSkipScale)

	def _editSpaceAttr(self, sCtrl, sType, lKeys, lIndex, lPlugs, iDefaultA, iDefaultB):
		iDefaultA_orig = cmds.addAttr('%s.spaceA%s' %(sCtrl, sType.upper()), q = True, dv = True)
		iDefaultB_orig = cmds.addAttr('%s.spaceB%s' %(sCtrl, sType.upper()), q = True, dv = True)
		sEnumName_orig = cmds.addAttr('%s.spaceA%s' %(sCtrl, sType.upper()), q = True, en = True)

		sEnumName_orig += ':'

		if iDefaultA == None:
			iDefaultA = iDefaultA_orig
		if iDefaultB == None:
			iDefaultB = iDefaultB_orig

		for i, sKey in enumerate(lKeys):
			sEnumName_orig += '%s=%s:' %(sKey, lIndex[i])

		cmds.addAttr('%s.spaceA%s' %(sCtrl, sType.upper()), e = True, en = sEnumName_orig[:-1], dv = iDefaultA)
		cmds.addAttr('%s.spaceB%s' %(sCtrl, sType.upper()), e = True, en = sEnumName_orig[:-1], dv = iDefaultB)

		oCtrl = controls.oControl(sCtrl)
		sChoiceA = naming.oName(sType = 'choice', sSide = oCtrl.sSide, sPart = '%sSpaceA%s' %(oCtrl.sPart, sType.upper()), iIndex = oCtrl.iIndex).sName
		sChoiceB = naming.oName(sType = 'choice', sSide = oCtrl.sSide, sPart = '%sSpaceB%s' %(oCtrl.sPart, sType.upper()), iIndex = oCtrl.iIndex).sName
		
		for i, sPlug in enumerate(lPlugs):
			sPlug_space = self._spaceMatrix(sCtrl, sPlug, lIndex[i])
			cmds.connectAttr(sPlug_space, '%s.input[%d]' %(sChoiceA, lIndex[i]), f = True)
			cmds.connectAttr(sPlug_space, '%s.input[%d]' %(sChoiceB, lIndex[i]), f = True)

	def _spaceMatrix(self, sCtrl, sPlug, iIndex):
		oCtrl = controls.oControl(sCtrl)
		sMultMatrix = naming.oName(sType = 'multMatrix', sSide = oCtrl.sSide, sPart = '%sSpace%dMatrix' %(oCtrl.sPart, iIndex), iIndex = oCtrl.iIndex).sName
		if not cmds.objExists(sMultMatrix):
			cmds.createNode('multMatrix', name = sMultMatrix)
		lPlugMatrix = cmds.getAttr(sPlug)
		lMatrixLocal = apiUtils.getLocalMatrixInMatrix(oCtrl.sSpace, lPlugMatrix, sNodeAttr = 'worldMatrix[0]')
		cmds.setAttr('%s.matrixIn[0]' %sMultMatrix, lMatrixLocal, type = 'matrix')
		attributes.connectAttrs([sPlug], ['%s.matrixIn[1]' %sMultMatrix], bForce = True)
		return '%s.matrixSum' %sMultMatrix




	def _getComponentInfo(self, sComponent):
		self._sComponentMaster = sComponent
		oName = naming.oName(sComponent)
		self._sSide = oName.sSide
		self._sName = oName.sPart
		self._iIndex = oName.iIndex
		self._sComponentType = self._getComponentAttr(sComponent, 'sComponentType')
		self._sComponentSpace = self._getComponentAttr(sComponent, 'sComponentSpace')
		if not self._sComponentSpace:
			self._sComponentSpace = None
		self._sComponentPasser = self._getComponentAttr(sComponent, 'sComponentPasser')
		if not self._sComponentPasser:
			self._sComponentPasser = None

		sControlsString = self._getComponentAttr(sComponent, 'sControls')
		self._lCtrls = componentInfo.decomposeStringToStrList(sControlsString)
		self._addAttributeFromList('sCtrl', self._lCtrls)

		self._sWorldMatrixPlug = '%s.lWorldMatrix' %self._sComponentMaster
		self.worldMatrixPlug = self._sWorldMatrixPlug
		self._sInputMatrixPlug = '%s.inputMatrix' %self._sComponentMaster
		self.inputMatrixPlug = self._sInputMatrixPlug

	def _getComponentAttr(self, sComponent, sAttr):
		if cmds.attributeQuery(sAttr, node = sComponent, ex = True):
			sValue = cmds.getAttr('%s.%s' %(sComponent, sAttr))
		else:
			sValue = None
		return sValue

	def _addAttributeFromList(self, sAttrName, lList):
		if lList:
			dAttrs = self._generateAttrDict(sAttrName, lList)
			self._addAttributeFromDict(dAttrs)

	def _addAttributeFromDict(self, dAttrs):
		for key, value in dAttrs.items():
			setattr(self, key, value)

	def _generateAttrDict(self, sAttrName, lList):
		dAttrs = {}
		for i, sItem in enumerate(lList):
			dAttrs.update({'%s%03d' %(sAttrName, i): sItem})
		return dAttrs

	def _addObjAttr(self, sAttrName, dAttrs):
		lAttrs = sAttrName.split('.')
		sAttrParent = self
		if len(lAttrs) > 1:
			for sAttr in lAttrs[:-1]:
				sAttrParent = getattr(sAttrParent, sAttr)
			
		setattr(sAttrParent, lAttrs[-1], addObjAttrs.objectview(dAttrs))
