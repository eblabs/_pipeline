######################################################################
# base joints limb
# this limb contains general functions and kwargs for all joints limb,
# all joints limb should inheirt from this class
######################################################################
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

## import rigUtils
import riggingAPI.rigComponents.rigUtils.componentInfo as componentInfo

import riggingAPI.rigComponents.baseComponent as baseComponent
reload(baseComponent)

## kwarg class
class kwargsGenerator(baseComponent.kwargsGenerator):
	"""docstring for kwargsGenerator"""
	def __init__(self):
		super(kwargsGenerator, self).__init__()
		self.dKwargs = {'lBpJnts': None,
						'iStacks': 1,
						'lLockHideAttrs': ['sx', 'sy', 'sz', 'v'],
						'bBind': False,
						'iTwistJntNum': 0,
						'lSkipTwist': [],
						'sBindParent': None,
							}
		self.addKwargs()

class baseJointsLimb(baseComponent.baseComponent):
	"""docstring for baseJointsLimb"""
	def __init__(self, *args, **kwargs):
		super(baseJointsLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpJnts = kwargs.get('lBpJnts', None)
			self._iStacks = kwargs.get('iStacks', 1)
			self._lLockHideAttrs = kwargs.get('lLockHideAttrs', ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'])
			self._bBind = kwargs.get('bBind', False)
			self._iTwistJntNum = kwargs.get('iTwistJntNum', 0)
			self._lSkipTwist = kwargs.get('lSkipTwist', [])
			self._sBindParent = kwargs.get('sBindParent', None)

	@property
	def iJointCount(self):
		return self._iJointCount

	@property
	def lBindJoints(self):
		return self._lBindJoints

	@property
	def lBindRootJoints(self):
		return self._lBindRootJoints

	@property
	def iTwistJointCount(self):
		return self._iTwistJntNum

	def createComponent(self):
		super(baseJointsLimb, self).createComponent()

		### inherits local group
		sComponentInheritsLocal = naming.oName(sType = 'inherits', sSide = self._sSide, sPart = '%sLocal' %self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentInheritsLocal, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentOffset, bInheritsTransform = False)

		### xform local group
		sComponentXformLocal = naming.oName(sType = 'xform', sSide = self._sSide, sPart = '%sLocal' %self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentXformLocal, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentInheritsLocal)
		attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sDriver = self._sComponentXform, sDriven = sComponentXformLocal, bForce = True)

		### passer local group
		sComponentPasserLocal = naming.oName(sType = 'passer', sSide = self._sSide, sPart = '%sLocal' %self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentPasserLocal, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentXformLocal)
		attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sDriver = self._sComponentPasser, sDriven = sComponentPasserLocal, bForce = True)

		### space local group
		sComponentSpaceLocal = naming.oName(sType = 'space', sSide = self._sSide, sPart = '%sLocal' %self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentSpaceLocal, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentPasserLocal)
		attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sDriver = self._sComponentSpace, sDriven = sComponentSpaceLocal, bForce = True)
		

		## joints group
		sComponentJoints = naming.oName(sType = 'joints', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentJoints, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentSpaceLocal)
				
		### drive joints group
		sComponentDrvJoints = naming.oName(sType = 'drvJoints', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		transforms.createTransformNode(sComponentDrvJoints, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentJoints)

		### bind joints group
		# sComponentBindJoints = naming.oName(sType = 'bindJoints', sSide = self._sSide, sPart = self._sName, iIndex = self._iIndex).sName
		# transforms.createTransformNode(sComponentBindJoints, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sComponentJoints)

		# visibility switch
		### joints
		cmds.addAttr(self._sComponentMaster, ln = 'joints', at = 'enum', enumName = 'on:off:tempelate:reference', keyable = False, dv = 1)
		cmds.setAttr('%s.joints' %self._sComponentMaster, channelBox = True)
		### bind joints vis
		# cmds.addAttr(self._sComponentMaster, ln = 'bindJoints', at = 'long', min = 0, max = 1, keyable = False, dv = 1)
		# cmds.setAttr('%s.bindJoints' %self._sComponentMaster, channelBox = True)
		### drive joints vis
		cmds.addAttr(self._sComponentMaster, ln = 'drvJoints', at = 'long', min = 0, max = 1, keyable = False, dv = 0)
		cmds.setAttr('%s.drvJoints' %self._sComponentMaster, channelBox = True)

		### move/deform geo
		cmds.addAttr(self._sComponentMaster, ln = 'localize', at = 'long', min = 0, max = 1, keyable = False, dv = 0)
		cmds.setAttr('%s.localize' %self._sComponentMaster, channelBox = True)
		sRvs = cmds.createNode('reverse', name = naming.oName(sType = 'reverse', sSide = self._sSide, sPart = '%sLocalize' %self._sName, iIndex = self._iIndex).sName)
		cmds.connectAttr('%s.localize' %self._sComponentMaster, '%s.inputX' %sRvs)
		cmds.connectAttr('%s.outputX' %sRvs, '%s.inheritsTransform' %sComponentInheritsLocal)

		cmds.addAttr(self._sComponentMaster, ln = 'iJointCount', at = 'long')
		cmds.addAttr(self._sComponentMaster, ln = 'sControls', dt = 'string')
		cmds.addAttr(self._sComponentMaster, ln = 'sBindJoints', dt = 'string')
		cmds.addAttr(self._sComponentMaster, ln = 'sBindRootJoints', dt = 'string')
		cmds.addAttr(self._sComponentMaster, ln = 'sTwistSections', dt = 'string')
		cmds.addAttr(self._sComponentMaster, ln = 'iTwistJointCount', at = 'long')
		cmds.addAttr(self._sComponentMaster, ln = 'sTwistBindJoints', dt = 'string')

		### connect attrs
		sConditionJointsVis = cmds.createNode('condition', name = naming.oName(sType = 'condition', sSide = self._sSide, sPart = '%sJointVis' %self._sName, iIndex = self._iIndex).sName)
		cmds.createNode('condition', name = sConditionJointsVis)
		cmds.connectAttr('%s.joints' %self._sComponentMaster, '%s.firstTerm' %sConditionJointsVis)
		cmds.setAttr('%s.secondTerm' %sConditionJointsVis, 1)
		cmds.setAttr('%s.colorIfTrueR' %sConditionJointsVis, 0)
		cmds.setAttr('%s.colorIfFalseR' %sConditionJointsVis, 1)
		attributes.connectAttrs(['%s.outColorR' %sConditionJointsVis], ['%s.v' %sComponentJoints], bForce = True)
		cmds.setAttr('%s.overrideEnabled' %sComponentJoints, 1)
		attributes.enumToSingleAttrs('joints', ['%s.overrideDisplayType' %sComponentJoints], iEnumRange = 4, lValRange = [[0,0],[0,0],[0,1],[0,2]], sEnumObj = self._sComponentMaster)

		#attributes.connectAttrs(['%s.bindJoints' %self._sComponentMaster], ['%s.v' %sComponentBindJoints], bForce = True)
		attributes.connectAttrs(['%s.drvJoints' %self._sComponentMaster], ['%s.v' %sComponentDrvJoints], bForce = True)

		self._sComponentJoints = sComponentJoints
		self._sComponentDrvJoints = sComponentDrvJoints
		#self._sComponentBindJoints = sComponentBindJoints


	def _writeGeneralComponentInfo(self, sComponentType, lJnts, lCtrls, lBindJnts, lBindRootJnts):
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, lock = False, type = 'string')
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, sComponentType, type = 'string', lock = True)

		cmds.setAttr('%s.iJointCount' %self._sComponentMaster, lock = False)
		cmds.setAttr('%s.iJointCount' %self._sComponentMaster, len(lJnts), lock = True)

		sControlsString = componentInfo.composeListToString(lCtrls)
		cmds.setAttr('%s.sControls' %self._sComponentMaster, lock = False, type = 'string')
		cmds.setAttr('%s.sControls' %self._sComponentMaster, sControlsString, type = 'string', lock = True)

		sBindString = componentInfo.composeListToString(lBindJnts)
		cmds.setAttr('%s.sBindJoints' %self._sComponentMaster, lock = False, type = 'string')
		cmds.setAttr('%s.sBindJoints' %self._sComponentMaster, sBindString, type = 'string', lock = True)

		sBindRootString = componentInfo.composeListToString(lBindRootJnts)
		cmds.setAttr('%s.sBindRootJoints' %self._sComponentMaster, lock = False, type = 'string')
		cmds.setAttr('%s.sBindRootJoints' %self._sComponentMaster, sBindRootString, type = 'string', lock = True)

	def _writeOutputMatrixInfo(self, lJnts):
		sMultMatrixWorldParent = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixWorldParent' %self._sName).sName)					
		cmds.connectAttr('%s.matrix' %self._sComponentSpace, '%s.matrixIn[0]' %sMultMatrixWorldParent)
		cmds.connectAttr('%s.matrix' %self._sComponentPasser, '%s.matrixIn[1]' %sMultMatrixWorldParent)
		cmds.connectAttr('%s.inputMatrix' %self._sComponentMaster, '%s.matrixIn[2]' %sMultMatrixWorldParent)
		sMultMatrixWorldParent = '%s.matrixSum' %sMultMatrixWorldParent
		self._sMultMatrixWorldParent = sMultMatrixWorldParent

		sMultMatrixLocalParent = None
		for i, sJnt in enumerate(lJnts):
			cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixLocal%03d' %i, at = 'matrix')
			cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixWorld%03d' %i, at = 'matrix')
			if sMultMatrixLocalParent:
				sMultMatrixLocal = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixLocal' %self._sName, iIndex = i).sName)
				cmds.connectAttr('%s.matrix' %sJnt, '%s.matrixIn[0]' %sMultMatrixLocal)
				cmds.connectAttr(sMultMatrixLocalParent, '%s.matrixIn[1]' %sMultMatrixLocal)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.outputMatrixLocal%03d' %(self._sComponentMaster, i))
				sMultMatrixWorld = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixWorld' %self._sName, iIndex = i).sName)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.matrixIn[0]' %sMultMatrixWorld)
				cmds.connectAttr(sMultMatrixWorldParent, '%s.matrixIn[1]' %sMultMatrixWorld)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixWorld, '%s.outputMatrixWorld%03d' %(self._sComponentMaster, i))
				sMultMatrixLocalParent = '%s.matrixSum' %sMultMatrixLocal
			else:
				cmds.connectAttr('%s.matrix' %sJnt, '%s.outputMatrixLocal%03d' %(self._sComponentMaster, i))
				sMultMatrixWorld = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixWorld' %self._sName, iIndex = i).sName)					
				cmds.connectAttr('%s.matrix' %sJnt, '%s.matrixIn[0]' %sMultMatrixWorld)
				cmds.connectAttr(sMultMatrixWorldParent, '%s.matrixIn[1]' %sMultMatrixWorld)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixWorld, '%s.outputMatrixWorld%03d' %(self._sComponentMaster, i))
				sMultMatrixLocalParent = '%s.matrix' %sJnt

	def _getComponentInfo(self, sComponent):
		super(baseJointsLimb, self)._getComponentInfo(sComponent)

		self._iJointCount = cmds.getAttr('%s.iJointCount' %sComponent)

		sBindJointsString = cmds.getAttr('%s.sBindJoints' %sComponent)
		self._lBindJoints = componentInfo.decomposeStringToStrList(sBindJointsString)

		self._iTwistJntNum = cmds.getAttr('%s.iTwistJointCount' %sComponent)
		
		sTwistBindJoints = cmds.getAttr('%s.sTwistBindJoints' %sComponent)
		self._lTwistBindJnts = componentInfo.decomposeStringToStrList(sTwistBindJoints)

		sTwistSections = cmds.getAttr('%s.sTwistSections' %sComponent)
		self._lTwistSections = componentInfo.decomposeStringToIntList(sTwistSections)

		sBindRootJointsString = cmds.getAttr('%s.sBindRootJoints' %sComponent)
		self._lBindRootJoints = componentInfo.decomposeStringToStrList(sBindRootJointsString)

		iSectionIndex = 0
		for i in range(self._iJointCount):
			dAttrs = {'localMatrixPlug': '%s.outputMatrixLocal%03d' %(self._sComponentMaster, i),
					  'worldMatrixPlug': '%s.outputMatrixWorld%03d' %(self._sComponentMaster, i)}

			if self._lBindJoints and i < len(self._lBindJoints):
				dAttrs.update({'bindJoint': self._lBindJoints[i]})

			self._addObjAttr('joint%03d' %i, dAttrs)

			if self._lTwistSections:
				if i in self._lTwistSections:
					for iTwist in range(self._iTwistJntNum):
						dAttrs = {'localMatrixPlug': '%s.output%03dTwistMatrixLocal%03d' %(self._sComponentMaster, i, iTwist),
								  'worldMatrixPlug': '%s.output%03dTwistMatrixWorld%03d' %(self._sComponentMaster, i, iTwist),
								  'bindJoint': self._lTwistBindJnts[iSectionIndex*(self._iTwistJntNum - 1) + iTwist]}
						self._addObjAttr('joint%03d.twist%03d' %(i, iTwist), dAttrs)

			