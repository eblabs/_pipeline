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
			self._sConnectIn = kwargs.get('sConnectIn', None)

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
	def sComponentControlsXform(self):
		return self._sComponentControlsXform

	@property
	def iJointCount(self):
		return self._iJointCount

	@property
	def lControls(self):
		return self._lCtrls

	@property
	def lBindJoints(self):
		return self._lBindJoints


	def createComponent(self):
		# create groups
		### master group
		sComponentMaster = naming.oName(sType = 'rigComponent', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentMaster, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sParent)

		### transform group
		sComponentXform = naming.oName(sType = 'xform', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentXform, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentMaster)

		### rig nodes world group
		sComponentRigNodesWorld = naming.oName(sType = 'rigNodesWorld', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentRigNodesWorld, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentMaster)

		### sub components group
		sComponentSubComponents = naming.oName(sType = 'subComponents', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentSubComponents, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentMaster)

		### passer group
		sComponentPasser = naming.oName(sType = 'passer', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentPasser, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentXform)

		### space group
		sComponentSpace = naming.oName(sType = 'space', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentSpace, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentPasser)

		### controls transform group
		sComponentControlsXform = naming.oName(sType = 'controlsXform', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentControlsXform, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentSpace)

		### controls group
		sComponentControls = naming.oName(sType = 'controls', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentControls, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentControlsXform)

		### joints group
		sComponentJoints = naming.oName(sType = 'joints', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentJoints, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentSpace)

		### drive joints group
		sComponentDrvJoints = naming.oName(sType = 'drvJoints', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentDrvJoints, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentJoints)

		### bind joints group
		sComponentBindJoints = naming.oName(sType = 'bindJoints', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentBindJoints, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentJoints)

		### rig nodes local group
		sComponentRigNodesLocal = naming.oName(sType = 'rigNodesLocal', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentRigNodesLocal, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentSpace)

		# visibility switch
		### joints
		cmds.addAttr(sComponentMaster, ln = 'joints', at = 'enum', enumName = 'on:off:tempelate:reference', keyable = False, dv = 1)
		cmds.setAttr('%s.joints' %sComponentMaster, channelBox = True)
		### bind joints vis
		cmds.addAttr(sComponentMaster, ln = 'bindJoints', at = 'long', , min = 0, max = 1, keyable = False, dv = 1)
		cmds.setAttr('%s.bindJoints' %sComponentMaster, channelBox = True)
		### drive joints vis
		cmds.addAttr(sComponentMaster, ln = 'drvJoints', at = 'long', , min = 0, max = 1, keyable = False, dv = 0)
		cmds.setAttr('%s.drvJoints' %sComponentMaster, channelBox = True)
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
		sConditionJointsVis = naming.oName(sType = 'condition', sSide = self._sSide, sPart = '%sJointVis' %self._sName, iIndex = self._iIndex).sName
		cmds.createNode('condition', name = sConditionJointsVis)
		cmds.connectAttr('%s.joints' %sComponentMaster, '%s.firstTerm' %sConditionJointsVis)
		cmds.setAttr('%s.secondTerm' %sConditionJointsVis, 1)
		cmds.setAttr('%s.colorIfTrueR' %sConditionJointsVis, 0)
		cmds.setAttr('%s.colorIfFalseR' %sConditionJointsVis, 1)
		attributes.connectAttrs(['%s.outColorR' %sConditionJointsVis], ['%s.v' %sComponentJoints], bForce = True)
		cmds.setAttr('%s.overrideEnabled' %sComponentJoints, 1)
		attributes.enumToSingleAttrs('joints', ['%s.overrideDisplayType' %sComponentJoints], iEnumRange = 4, lValRange = [[0,0],[0,0],[0,1],[0,2]], sEnumObj = sComponentMaster)

		attributes.connectAttrs(['%s.bindJoints' %sComponentMaster], ['%s.v' %sComponentBindJoints], bForce = True)
		attributes.connectAttrs(['%s.drvJoints' %sComponentMaster], ['%s.v' %sComponentDrvJoints], bForce = True)
		attributes.connectAttrs(['%s.controls' %sComponentMaster], ['%s.v' %sComponentControls], bForce = True)
		attributes.connectAttrs(['%s.rigNodes' %sComponentMaster, '%s.rigNodes' %sComponentMaster], ['%s.v' %sComponentRigNodesLocal, '%s.v' %sComponentRigNodesWorld], bForce = True)
		attributes.connectAttrs(['%s.subComponents' %sComponentMaster], ['%s.v' %sComponentSubComponents], bForce = True)
		
		# input attrs
		### input matrix
		cmds.addAttr(sComponentMaster, ln = 'inputMatrix', at = 'matrix')
		cmds.addAttr(sComponentMaster, ln = 'inputMatrixInverse', at = 'matrix')
		sMultMatrix = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sInputMatrix' %self._sName, iIndex = self._iIndex).sName
		sDecomposeMatrix = naming.oName(sType = 'decomposeMatrix', sSide = self._sSide, sPart = '%sInputMatrix' %self._sName, iIndex = self._iIndex).sName
		cmds.connectAttr('%s.inputMatrixInverse' %sComponentMaster, '%s.matrixIn[0]' %sMultMatrix)
		cmds.connectAttr('%s.inputMatrix' %sComponentMaster, '%s.matrixIn[1]' %sMultMatrix)
		cmds.conenctAttr('%s.matrixSum' %sMultMaster, '%s.inputMatrix' %sDecomposeMatrix)
		for sAxis in ['X', 'Y', 'Z']:
			attributes.connectAttrs(['%s.outputTranslate%s' %(sDecomposeMatrix, sAxis), '%s.outputRotate%s' %(sDecomposeMatrix, sAxis), '%s.outputScale%s' %(sDecomposeMatrix, sAxis)], ['%s.translate%s' %(sComponentXform, sAxis), '%s.rotate%s' %(sComponentXform, sAxis), '%s.scale%s' %(sComponentXform, sAxis)], bForce = True)
		attributes.connectAttrs(['%s.outputShear' %sDecomposeMatrix], ['%s.shear' %sComponentXform], bForce = True)

		self._sComponentMaster = sComponentMaster
		self._sComponentXform = sComponentXform
		self._sComponentPasser = sComponentPasser
		self._sComponentSpace = sComponentSpace
		self._sComponentRigNodesWorld = sComponentRigNodesWorld
		self._sComponentSubComponents = sComponentSubComponents
		self._sComponentControlsXform = sComponentControlsXform
		self._sComponentControls = sComponentControls
		self._sComponentJoints = sComponentJoints
		self._sComponentDrvJoints = sComponentDrvJoints
		self._sComponentBindJoints = sComponentBindJoints
		self._sComponentRigNodesLocal = sComponentRigNodesLocal

		## add component info
		#### joint count
		cmds.addAttr(sComponentMaster, ln = 'sComponentType', at = 'string')
		cmds.setAttr('%s.sComponentType' %sComponentMaster, 'baseComponent', at = 'string')
		cmds.addAttr(sComponentMaster, ln = 'sComponentSpace', at = 'string')
		cmds.setAttr('%s.sComponentSpace' %sComponentMaster, sComponentSpace, at = 'string', lock = True)
		cmds.addAttr(sComponentMaster, ln = 'sComponentPasser', at = 'string')
		cmds.setAttr('%s.sComponentPasser' %sComponentMaster, sComponentPasser, at = 'string', lock = True)
		cmds.addAttr(sComponentMaster, ln = 'iJointCount', at = 'long')
		cmds.addAttr(sComponentMaster, ln = 'sControls', dt = 'string')
		cmds.addAttr(sComponentMaster, ln = 'sBindJoints', dt = 'string')

		## connect component
		if self._sConnectIn:
			self.connectComponents(sComponentMaster, self._sConnectIn)

	def connectComponents(self, sComponent, sMatrixPlug):
		lMatrixIn = cmds.getAttr(sMatrixPlug)
		mMatrix = apiUtils.convertListToMMatrix(lMatrixIn)
		mMatrixInverse = mMatrix.inverse()
		lMatrixInInverse = apiUtils.convertMMatrixToList(mMatrixInverse)
		cmds.setAttr('%s.inputMatrixInverse' %sComponent, lMatrixInInverse, type = 'matrix')
		cmds.connectAttr(sMatrixPlug, '%s.inputMatrix' %sComponent, f = True)

	def _getComponentInfo(self, sComponent):
		self._sComponentType = cmds.getAttr('%s.sComponentType' %sComponent)
		self._sComponentSpace = cmds.getAttr('%s.sComponentSpace' %sComponent)
		self._sComponentPasser = cmds.getAttr('%s.sComponentPasser' %sComponent)
		self._sComponentControlsXform = cmds.getAttr('%s.sComponentControlsXform' %sComponent)
		self._iJointCount = cmds.getAttr('%s.iJointCount' %sComponent)
		sControlsString = cmds.getAttr('%s.sControls' %sComponent)
		if sControlsString:
			self._lCtrls = sControlsString.split(',')
		else:
			self._lCtrls = None
		sBindJointsString = cmds.getAttr('%s.sBindJoints' %sComponent)
		if sBindJointsString:
			self._lBindJoints = sBindJointsString.split(',')
		else:
			self._lBindJoints = None

	def _writeOutputMatrixInfo(self, lJnts, bHierarchy = True):

		sMultMatrixWorldParent = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixWorldParent' %self._sName).sName)					
		cmds.connectAttr('%s.matrix' %self._sComponentSpace, '%s.matrixIn[0]' %sMultMatrixWorldParent)
		cmds.connectAttr('%s.matrix' %self._sComponentPasser, '%s.matrixIn[1]' %sMultMatrixWorldParent)
		cmds.connectAttr('%s.inputMatrix' %self._sComponentMaster, '%s.matrixIn[2]' %sMultMatrixWorldParent)

		if bHierarchy:
			sMultMatrixLocalParent = None
			for i, sJnt in enumerate(lJnts):
				cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixLocal%03d' %i, at = 'matrix')
				cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixWorld%03d' %i, at = 'matrix')
				if sMultMatrixParent:
					sMultMatrixLocal = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixLocal' %self._sName, iIndex = i).sName)
					cmds.connectAttr('%s.matrix' %sJnt, '%s.matrixIn[0]' %sMultMatrixLocal)
					cmds.connectAttr('%s.matrixSum' %sMultMatrixLocalParent, '%s.matrixIn[1]' %sMultMatrixLocal)
					cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.outputMatrixLocal%03d' %(self._sComponentMaster, i))
					sMultMatrixWorld = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixWorld' %self._sName, iIndex = i).sName)
					cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.matrixIn[0]' %sMultMatrixWorld)
					cmds.conenctAttr('%s.matrixSum' %sMultMatrixWorldParent, '%s.matrixIn[1]' %sMultMatrixWorld)
					cmds.conenctAttr('%s.matrixSum' %sMultMatrixWorld, '%s.outputMatrixWorld%03d' %(self._sComponentMaster, i))
				else:
					cmds.connectAttr('%s.matrix' %sJnt, '%s.outputMatrixLocal%03d' %(self._sComponentMaster, i))
					sMultMatrixWorld = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixWorld' %self._sName, iIndex = i).sName)					
					cmds.connectAttr('%s.matrix' %sJnt, '%s.matrixIn[0]' %sMultMatrixWorld)
					cmds.connectAttr('%s.matrixSum' %sMultMatrixWorldParent, '%s.matrixIn[1]' %sMultMatrixWorld)
					cmds.connectAttr('%s.matrixSum' %sMultMatrixWorld, '%s.outputMatrixWorld%03d' %(self._sComponentMaster, i))

				cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.outputMatrix%03d' %(self._sComponentMaster, i))
				sMultMatrixParent = sMultMatrix

		else:
			for i, sJnt in enumerate(lJnts):
				cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixLocal%03d' %i, at = 'matrix')
				cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixWorld%03d' %i, at = 'matrix')
				sMultMatrixWorld = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixWorld' %self._sName, iIndex = i).sName)
				cmds.connectAttr('%s.matrix' %sJnt, '%s.outputMatrixLocal%03d' %(self._sComponentMaster, i))
				cmds.connectAttr('%s.matrix' %sJnt, '%s.matrixIn[0]' %sMultMatrixWorld)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixWorldParent, '%s.matrixIn[1]' %sMultMatrixWorld)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixWorld, '%s.outputMatrixWorld%03d' %(self._sComponentMaster, i))


