#################################################
# arm ik module
# this module should do the base biped arm ik rig
#################################################
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

import riggingAPI.rigComponents.baseComponent as baseComponent
import riggingAPI.rigComponents.baseLimbs.baseIkRPsolverLimb as baseIkRPsolverLimb

class armIkModule(baseIkRPsolverLimb.baseIkRPsolverLimb):
	"""docstring for armIkModule"""
	def __init__(self, *args, **kwargs):
		super(armIkModule, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		
	def createComponent(self):
		lBpJnts = self._lBpJnts
		self._lBpJnts = lBpJnts[:-1]
		sBpJntWristEnd = lBpJnts[-1]

		super(armIkModule, self).createComponent()

		## create wrist ik rig
		## jnt
		oJntName = naming.oName(sBpJntWristEnd)
		oJntName.sType = 'jnt'
		oJntName.sPart = '%sIkSC' %oJntName.sPart
		sJntWristEnd = joints.createJntOnExistingNode(sBpJntWristEnd, sBpJntWristEnd, oJntName.sName, sParent = self._lJnts[-1])
		
		sJntWristEndLocal = joints.createJntOnExistingNode(sJntWristEnd, 'IkSC', 'IkSCLocal', sParent = self._lJntsLocal[-1])

		for sAxis in ['X', 'Y', 'Z']:
			cmds.connectAttr('%s.translate%s' %(sJntWristEndLocal, sAxis), '%s.translate%s' %(sJntWristEnd, sAxis))
			cmds.connectAttr('%s.rotate%s' %(sJntWristEndLocal, sAxis), '%s.rotate%s' %(sJntWristEnd, sAxis))
			cmds.connectAttr('%s.scale%s' %(sJntWristEndLocal, sAxis), '%s.scale%s' %(sJntWristEnd, sAxis))

		## ik handle
		sIkHnd = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sSCsolver' %self._sName, iIndex = self._iIndex).sName
		cmds.ikHandle(sj = self._lJntsLocal[-1], ee = sJntWristEndLocal, sol = 'ikSCsolver', name = sIkHnd)
		cmds.parent(sIkHnd, self._sGrpIk)

		self._lJnts.append(sJntWristEnd)
		self._lJntsLocal.append(sJntWristEndLocal)

		## write component info
		self._writeGeneralComponentInfo('armIkModule', self._lJnts, self._lCtrls, self._lBindJnts)

		## writeOutputMatrixInfo
		if self._bInfo:
			cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixLocal%03d' %(len(self._lJnts) - 1), at = 'matrix')
			cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixWorld%03d' %(len(self._lJnts) - 1), at = 'matrix')

			sMultMatrixLocalParent = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixLocal' %self._sName, iIndex = len(self._lJnts) - 2).sName

			sMultMatrixLocal = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixLocal' %self._sName, iIndex = len(self._lJnts) - 1).sName)
			cmds.connectAttr('%s.matrix' %sJntWristEnd, '%s.matrixIn[0]' %sMultMatrixLocal)
			cmds.connectAttr('%s.matrixSum' %sMultMatrixLocalParent, '%s.matrixIn[1]' %sMultMatrixLocal)
			cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.outputMatrixLocal%03d' %(self._sComponentMaster, len(self._lJnts) - 1))
			sMultMatrixWorld = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixWorld' %self._sName, iIndex = len(self._lJnts) - 1).sName)
			cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.matrixIn[0]' %sMultMatrixWorld)
			cmds.connectAttr(self._sMultMatrixWorldParent, '%s.matrixIn[1]' %sMultMatrixWorld)
			cmds.connectAttr('%s.matrixSum' %sMultMatrixWorld, '%s.outputMatrixWorld%03d' %(self._sComponentMaster, len(self._lJnts) - 1))

		self._getComponentInfo(self._sComponentMaster)

		