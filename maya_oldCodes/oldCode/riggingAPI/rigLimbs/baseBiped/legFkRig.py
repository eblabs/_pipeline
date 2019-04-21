## import
import maya.cmds as cmds
import maya.mel as mel
## import libs
import common.transforms as transforms
import namingAPI.naming as naming
import riggingAPI.joints as joints
import riggingAPI.constraints as constraints
import riggingAPI.controls as controls
import riggingAPI.rigLimbs.baseLimbs.fkJointChainRig as fkJointChainRig

## function
class legFkRig(fkJointChainRig.fkJointChainRig):
	"""docstring for legFkRig"""
	def __init__(self, *args, **kwargs):
		super(legFkRig, self).__init__(*args, **kwargs)

		self._sPart = 'leg'
		self._sName = 'Fk'

	@property
	def lJntsOutput(self):
		return self._lJntsOutput

	def create(self):
		self._lBpJnts = [
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'upperLeg').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'knee').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'ankle').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'ball').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'toe').sName,
						]

		super(legFkRig, self).create()

		sString_lJntsOutput = self._convertListToString(self._lJnts[:-1])
		lRigInfo = ['legFkRig', sString_lJntsOutput]
		lAttrs = ['sModuleType', 'lJntsOutput']
		self._writeRigInfo(self._sModuleNode, lRigInfo, lAttrs)

		self._getRigInfo(self._sModuleNode)

	def _getRigInfo(self, sModuleNode):
		super(legFkRig, self)._getRigInfo(sModuleNode)
		if cmds.attributeQuery('lJntsOutput', node = sModuleNode, ex = True):
			sJntsOutputString = cmds.getAttr('%s.lJntsOutput' %sModuleNode)
			self._lJntsOutput = sJntsOutputString.split(',')