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
import legFkRig
import legIkRig

class legRig(blendModeRig.blendModeRig):
	"""docstring for legRig"""
	def __init__(self, *args, **kwargs):
		super(legRig, self).__init__(*args, **kwargs)
		
		self._dRigLimbs = {'fk': {'class': legFkRig.legFkRig},
					 	   'ik': {'class': legIkRig.legIkRig}}

		self._sName = 'ikFkBlend'
		self._sPart = 'leg'
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
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'upperLeg').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'knee').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'ankle').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'ball').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'toe').sName,
						]

		super(legRig, self).create()

		## create matchers
		lIndex_fkik = [0,1]
		lString_fkik = ['fk', 'ik']
		for i, iIndex in enumerate(lIndex_fkik):
			if iIndex in self._lModuleIndex:
				sMatchersString = ''
				iIndex_each = self._lModuleIndex.index(i)
				sModuleNode_each = self._lModuleNodes[iIndex_each]
				if iIndex == 0:
					oModule_each = legFkRig.legFkRig(sModuleNode_each)
				elif iIndex == 1:
					oModule_each = legIkRig.legIkRig(sModuleNode_each)
				for j, sCtrl in enumerate(oModule_each.lCtrls):
					sMatcher, sOffset = transforms.createTransformMatcherNode(sCtrl, sParent = self._lJnts[j])
					sMatchersString += '%s,'%sMatcher
				self._writeRigInfo(self._sModuleNode, [sMatchersString[:-1]], ['lMatchers%s' %lString_fkik[i].title()])

		self._writeRigInfo(self._sModuleNode, ['legRig'], ['sModuleType'])

		self._getRigInfo(self._sModuleNode)

	def _getRigInfo(self, sModuleNode):
		super(legRig, self)._getRigInfo(sModuleNode)
		if cmds.attributeQuery('lMatchersFk', node = sModuleNode, ex = True):
			sMatchersStringFk = cmds.getAttr('%s.lMatchersFk' %sModuleNode)
			self._lMatchersFk = sMatchersStringFk.split(',')
		if cmds.attributeQuery('lMatchersIk', node = sModuleNode, ex = True):
			sMatchersStringIk = cmds.getAttr('%s.lMatchersIk' %sModuleNode)
			self._lMatchersIk = sMatchersStringIk.split(',')

