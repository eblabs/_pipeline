## import
import maya.cmds as cmds
import maya.mel as mel
## import libs
import common.transforms as transforms
import namingAPI.naming as naming
import riggingAPI.joints as joints
import riggingAPI.constraints as constraints
import riggingAPI.controls as controls
import riggingAPI.rigLimbs.baseLimbs.blendModeRig as blendModeRig
import armFkRig
import armIkRig

class armRig(blendModeRig.blendModeRig):
	"""docstring for armRig"""
	def __init__(self, *args, **kwargs):
		super(armRig, self).__init__(*args, **kwargs)
		
		self._dRigLimbs = {'fk': {'class': armFkRig.armFkRig},
					 	   'ik': {'class': armIkRig.armIkRig}}

		self._sName = 'ikFkBlend'
		self._sPart = 'arm'
		self._lMatchersFk = None
		self._lMatchersIk = None

	@property
	def lMatchersFk(self):
		return self._lMatchersFk

	@property
	def lMatchersIk(self):
		return self._lMatchersIk
		
	def create(self):
		self._lBpJnts = [
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'upperArm').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'elbow').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'wrist').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'wristEnd').sName,
						]
		super(armRig, self).create()

		## create matchers
		lIndex_fkik = [0,1]
		lString_fkik = ['fk', 'ik']
		for i, iIndex in enumerate(lIndex_fkik):
			if iIndex in self._lModuleIndex:
				sMatchersString = ''
				iIndex_each = self._lModuleIndex.index(i)
				sModuleNode_each = self._lModuleNodes[iIndex_each]
				if iIndex == 0:
					oModule_each = armFkRig.armFkRig(sModuleNode_each)
				elif iIndex == 1:
					oModule_each = armIkRig.armIkRig(sModuleNode_each)
				for j, sCtrl in enumerate(oModule_each.lCtrls):
					sMatcher, sOffset = transforms.createTransformMatcherNode(sCtrl, sParent = self._lJnts[j])
					sMatchersString += '%s,'%sMatcher
				self._writeRigInfo(self._sModuleNode, [sMatchersString[:-1]], ['lMatchers%s' %lString_fkik[i].title()])

		self._writeRigInfo(self._sModuleNode, ['armRig'], ['sModuleType'])

		self._getRigInfo(self._sModuleNode)

	def _getRigInfo(self, sModuleNode):
		super(armRig, self)._getRigInfo(sModuleNode)
		if cmds.attributeQuery('lMatchersFk', node = sModuleNode, ex = True):
			sMatchersStringFk = cmds.getAttr('%s.lMatchersFk' %sModuleNode)
			self._lMatchersFk = sMatchersStringFk.split(',')
		if cmds.attributeQuery('lMatchersIk', node = sModuleNode, ex = True):
			sMatchersStringIk = cmds.getAttr('%s.lMatchersIk' %sModuleNode)
			self._lMatchersIk = sMatchersStringIk.split(',')

