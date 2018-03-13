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

class baseJointsLimb(baseComponent.baseComponent):
	"""docstring for baseJointsLimb"""
	def __init__(self, arg):
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

	@property
	def iJointCount(self):
		return self._iJointCount

	@property
	def lBindJoints(self):
		return self._lBindJoints

	@property
	def iTwistJointCount(self):
		return self._iTwistJntNum

	def createComponent(self):
		super(baseJointsLimb, self).createComponent()

		cmds.addAttr(sComponentMaster, ln = 'iJointCount', at = 'long')
		cmds.addAttr(sComponentMaster, ln = 'sControls', dt = 'string')
		cmds.addAttr(sComponentMaster, ln = 'sBindJoints', dt = 'string')
		cmds.addAttr(sComponentMaster, ln = 'sTwistSections', dt = 'string')
		cmds.addAttr(sComponentMaster, ln = 'iTwistJointCount', at = 'long')
		cmds.addAttr(sComponentMaster, ln = 'sTwistBindJoints', dt = 'string')

	def _writeGeneralComponentInfo(self, sComponentType, lJnts, lCtrls, lBindJnts):
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, lock = False, type = 'string')
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, sComponentType, type = 'string', lock = True)

		cmds.setAttr('%s.iJointCount' %self._sComponentMaster, lock = False)
		cmds.setAttr('%s.iJointCount' %self._sComponentMaster, len(lJnts), lock = True)

		sControlsString = componentInfo.composeListToString(lCtrls)
		cmds.setAttr('%s.sControls' %self._sComponentMaster, lock = False, type = 'string')
		cmds.setAttr('%s.sControls' %self._sComponentMaster, sControlsString, type = 'string', lock = True)

		sBindString = componentInfo.composeListToString(lBindJnts)
		cmds.setAttr('%s.sBindJoints' %self._sComponentMaster, lock = False, type = 'string')
		cmds.setAttr('%s.sBindJoints' %self._sComponentMaster, sBindString[:-1], type = 'string', lock = True)


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

		iSectionIndex = 0
		for i in range(self._iJointCount):
			dAttrs = {'localMatrixPlug': '%s.outputMatrixLocal%03d' %(self._sComponentMaster, i),
					  'worldMatrixPlug': '%s.outputMatrixWorld%03d' %(self._sComponentMaster, i)}

			if i < len(self._lBindJoints):
				dAttrs.update({'bindJoint': self._lBindJoints[i]})

			if i in sTwistSections:
				lTwistOutputLocal = []
				lTwistOutputWorld = []
				lTwistBind = []
				for iTwist in range(self._iTwistJntNum):
					lTwistOutputLocal.append('%s.output%03dTwistMatrixLocal%03d' %(self._sComponentMaster, i, iTwist))
					lTwistOutputWorld.append('%s.output%03dTwistMatrixWorld%03d' %(self._sComponentMaster, i, iTwist))
					lTwistBind.append(self._lTwistBindJnts[iSectionIndex*(self._iTwistJntNum - 1) + iTwist])
				dAttrs.update({'twistLocalMatrixPlug': lTwistOutputLocal, 
							   'twistWorldMatrixPlug': lTwistOutputWorld,
							   'twistBindJoint': lTwistBind})

			self._addObjAttr('joint%03d' %i, dAttrs)