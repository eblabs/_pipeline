## import
import maya.cmds as cmds
import maya.mel as mel
## import libs
import common.transforms as transforms
import namingAPI.naming as naming
import riggingAPI.joints as joints
import riggingAPI.constraints as constraints
import riggingAPI.controls as controls
import baseLimbRig
## function
class fkJointChainRig(baseLimbRig.baseLimbRig):
	"""docstring for fkJointChainRig"""
	def __init__(self, *args, **kwargs):
		super(fkJointChainRig, self).__init__()

		if args:
			self._getRigInfo(args[0])
		else:
			sName = kwargs.get('sName', 'FkChain')
			sSide = kwargs.get('sSide', 'm')
			sPart = kwargs.get('sPart', None)
			iIndex = kwargs.get('iIndex', None)
			lBpJnts = kwargs.get('lBpJnts', None)
			sConnectInCtrl = kwargs.get('sConnectInCtrl', 'controls')
			sConnectInJnt = kwargs.get('sConnectInJnt', 'rigJoints')
			bSub = kwargs.get('bSub', False)
			iStacks = kwargs.get('iStacks', 1)
			lLockHideAttrs = kwargs.get('lLockHideAttrs', ['sx', 'sy', 'sz', 'v'])

			self._sName = sName
			self._lBpJnts = lBpJnts
			self._sSide = sSide
			self._sPart = sPart
			self._iIndex = iIndex
			self._sConnectInCtrl = sConnectInCtrl
			self._sConnectInJnt = sConnectInJnt
			self._bSub = bSub
			self._iStacks = iStacks
			self._lLockHideAttrs = lLockHideAttrs

	def create(self):
		sGrp = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRig' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInJnt)
		sGrpCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInCtrl)
		sParent_jnt = sGrp
		sParent_ctrl = sGrpCtrl
		lJnts = []
		lCtrls = []
		for i, sBpJnt in enumerate(self._lBpJnts):
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			oJntName.sPart = '%s%s' %(oJntName.sPart, self._sName)
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			lJnts.append(sJnt)
			if i < len(self._lBpJnts) - 1:
				iRotateOrder = cmds.getAttr('%s.ro' %sJnt)
				oCtrl = controls.create(oJntName.sPart, sSide = oJntName.sSide, iIndex = oJntName.iIndex, iStacks = self._iStacks, bSub = self._bSub, sParent = sParent_ctrl, sPos = sJnt, iRotateOrder = iRotateOrder, sShape = 'square', fSize = 8, lLockHideAttrs = self._lLockHideAttrs)
				cmds.parentConstraint(oCtrl.sOutput, sJnt, mo = False)
				lCtrls.append(oCtrl.sName)
				sParent_jnt = sJnt
				sParent_ctrl = oCtrl.sOutput

		## write rig info
		sString_lJnts = self._convertListToString(lJnts)
		sString_lCtrls = self._convertListToString(lCtrls)
		lRigInfo = ['fkJointChainRig', self._sConnectInJnt, self._sConnectInCtrl, sJnt, oCtrl.sOutput, sString_lJnts, sString_lCtrls, sGrpCtrl, sGrp]
		lAttrs = ['sModuleType', 'sConnectInJnt', 'sConnectInCtrl', 'sConnectOutJnt', 'sConnectOutCtrl', 'lJnts', 'lCtrls', 'sGrpCtrl', 'sModuleNode']
		self._writeRigInfo(sGrp, lRigInfo, lAttrs)

		self._getRigInfo(sGrp)