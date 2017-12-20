## import
import maya.cmds as cmds
import maya.mel as mel
## import libs
import common.transforms as transforms
import namingAPI.naming as naming
import riggingAPI.joints as joints
import riggingAPI.constraints as constraints
import riggingAPI.controls as controls
import riggingAPI.rigLimbs.baseLimbs.ikRPsolverRig as ikRPsolverRig
import modelingAPI.curves as curves
## function
class armIkRig(ikRPsolverRig.ikRPsolverRig ):
	"""docstring for armIkRig"""
	def __init__(self, *args, **kwargs):
		super(armIkRig, self).__init__(*args, **kwargs)

		self._sPart = 'arm'
		self._bOrient = True
		self._sName = 'Ik'

	@property
	def lJntsOutput(self):
		return self._lJntsOutput

	def create(self):
		self._lBpJnts = [
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'upperArm').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'elbow').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'wrist').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'wristEnd').sName,
						]

		self._sBpCtrl = naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'handIk').sName
		self._sBpPv = naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'elbowPvIk').sName
		self._sBpRoot = naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'upperArmIk').sName
		
		super(armIkRig, self).create()

		sString_lJntsOutput = self._convertListToString(self._lJnts[:-1])
		lRigInfo = ['armIkRig', sString_lJntsOutput]
		lAttrs = ['sModuleType', 'lJntsOutput']
		self._writeRigInfo(self._sModuleNode, lRigInfo, lAttrs)

		self._getRigInfo(self._sModuleNode)

	def _getRigInfo(self, sModuleNode):
		super(armIkRig, self)._getRigInfo(sModuleNode)
		if cmds.attributeQuery('lJntsOutput', node = sModuleNode, ex = True):
			sJntsOutputString = cmds.getAttr('%s.lJntsOutput' %sModuleNode)
			self._lJntsOutput = sJntsOutputString.split(',')