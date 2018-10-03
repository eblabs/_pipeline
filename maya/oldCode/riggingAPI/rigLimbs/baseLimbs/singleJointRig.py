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
class singleJointRig(baseLimbRig.baseLimbRig):
	"""docstring for singleJointRig"""
	def __init__(self, *args, **kwargs):
		super(singleJointRig, self).__init__()

		if args:
			self._getRigInfo(args[0])
		else:
			sBpJnt = kwargs.get('sBpJnt', None)
			sConnectInCtrl = kwargs.get('sConnectInCtrl', 'controls')
			sConnectInJnt = kwargs.get('sConnectInJnt', 'rigJoints')
			bSub = kwargs.get('bSub', False)
			iStacks = kwargs.get('iStacks', 1)
			lLockHideAttrs = kwargs.get('lLockHideAttrs', ['sx', 'sy', 'sz', 'v'])

			self._sConnectInCtrl = sConnectInCtrl
			self._sConnectInJnt = sConnectInJnt
			self._bSub = bSub
			self._iStacks = iStacks
			self._lLockHideAttrs = lLockHideAttrs

			self._sBpJnt = sBpJnt


	def create(self):
		oName = naming.oName(self._sBpJnt)
		self._sSide = oName.sSide
		self._sPart = oName.sPart
		self._iIndex = oName.iIndex
		self._lPos = transforms.getNodeTransformInfo(self._sBpJnt)
		self._iRotateOrder = cmds.getAttr('%s.ro' %self._sBpJnt)

		sGrp = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%sRig' %self._sPart, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInJnt)
		sJnt = joints.createJntOnTransformInfo(naming.oName(sType = 'jnt', sSide = self._sSide, sPart = self._sPart, iIndex = self._iIndex).sName, self._lPos, iRotateOrder = self._iRotateOrder, sParent = sGrp)
		sGrpCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%sCtrl' %self._sPart, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInCtrl)
		oCtrl = controls.create(self._sPart, sSide = self._sSide, iIndex = self._iIndex, iStacks = self._iStacks, bSub = self._bSub, sParent = sGrpCtrl, iRotateOrder = self._iRotateOrder, sShape = 'circle', fSize = 10, lLockHideAttrs = self._lLockHideAttrs)
		transforms.setNodeTransform(oCtrl.sZero, self._lPos)
		constraints.constraint([oCtrl.sOutput, sJnt], sType = 'parent')

		## write rig info
		lRigInfo = ['singleJointRig', self._sConnectInJnt, self._sConnectInCtrl, sJnt, oCtrl.sOutput, sJnt, oCtrl.sName, sGrpCtrl, sGrp]
		lAttrs = ['sModuleType', 'sConnectInJnt', 'sConnectInCtrl', 'sConnectOutJnt', 'sConnectOutCtrl', 'lJnts', 'lCtrls', 'sGrpCtrl', 'sModuleNode']
		self._writeRigInfo(sGrp, lRigInfo, lAttrs)

		self._getRigInfo(sGrp)