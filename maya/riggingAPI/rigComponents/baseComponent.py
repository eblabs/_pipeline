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
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import riggingAPI.constraints as constraints
import riggingAPI.joints as joints
import riggingAPI.rigComponents.rigUtils.componentInfo as componentInfo
import riggingAPI.rigComponents.rigUtils.addObjAttrs as addObjAttrs

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

	def _getComponentInfo(self, sComponent):
		self._sComponentMaster = sComponent
		oName = naming.oName(sComponent)
		self._sSide = oName.sSide
		self._sName = oName.sPart
		self._iIndex = oName.iIndex
		self._sComponentType = cmds.getAttr('%s.sComponentType' %sComponent)
		self._sComponentSpace = cmds.getAttr('%s.sComponentSpace' %sComponent)
		if not self._sComponentSpace:
			self._sComponentSpace = None
		self._sComponentPasser = cmds.getAttr('%s.sComponentPasser' %sComponent)
		if not self._sComponentPasser:
			self._sComponentPasser = None

		sControlsString = cmds.getAttr('%s.sControls' %sComponent)
		self._lCtrls = componentInfo.decomposeStringToStrList(sControlsString)
		self._addAttributeFromList('sCtrl', self._lCtrls)

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
