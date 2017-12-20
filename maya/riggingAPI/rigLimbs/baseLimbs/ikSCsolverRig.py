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
class ikSCsolverRig(baseLimbRig.baseLimbRig):
	"""docstring for ikSCsolverRig"""
	def __init__(self, *args, **kwargs):
		super(ikSCsolverRig, self).__init__()

		if args:
			self._getRigInfo(args[0])
		else:
			sName = kwargs.get('sName', 'IkSCsolver')
			sSide = kwargs.get('sSide', 'm')
			sPart = kwargs.get('sPart', None)
			iIndex = kwargs.get('iIndex', None)
			lBpJnts = kwargs.get('lBpJnts', None)
			bCtrl = kwargs.get('bCtrl', True)
			sConnectInCtrl = kwargs.get('sConnectInCtrl', 'controls')
			sConnectInJnt = kwargs.get('sConnectInJnt', 'rigJoints')
			bSub = kwargs.get('bSub', False)
			iStacks = kwargs.get('iStacks', 1)
			lLockHideAttrs = kwargs.get('lLockHideAttrs', ['sx', 'sy', 'sz', 'v'])

			self._sName = sName
			self._lBpJnts = lBpJnts
			self._bCtrl = bCtrl
			self._bTranslate = bTranslate
			self._sSide = sSide
			self._sPart = sPart
			self._iIndex = iIndex
			self._sConnectInCtrl = sConnectInCtrl
			self._sConnectInJnt = sConnectInJnt
			self._bSub = bSub
			self._iStacks = iStacks
			self._lLockHideAttrs = lLockHideAttrs

	@property
	def sIkHnd(self):
		return self._sIkHnd

	def create(self):
		sGrp = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRig' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInJnt)
		
		sParent_jnt = sGrp
		lJnts = []
		for i, sBpJnt in enumerate(self._lBpJnts):
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			oJntName.sPart = '%s%s' %(oJntName.sPart, self._sName)
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			lJnts.append(sJnt)
			sParent_jnt = sJnt

		## ik handle
		sIkHnd = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = self._sPart, iIndex = self._iIndex).sName
		cmds.ikHandle(sj = lJnts[0], ee = lJnts[-1], sol = 'ikSCsolver', name = sIkHnd)

		## control
		if self._bCtrl:
			sGrpCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInCtrl)
			iRotateOrder = cmds.getAttr('%s.ro' %lJnts[0])
			oJntName = naming.oName(lJnts[0])
			oCtrl_root = controls.create(oJntName.sPart, sSide = oJntName.sSide, iIndex = oJntName.iIndex, iStacks = self._iStacks, bSub = self._bSub, sParent = sGrpCtrl, sPos = lJnts[0], iRotateOrder = iRotateOrder, sShape = 'cube', fSize = 4, lLockHideAttrs = self._lLockHideAttrs)
			oJntName = naming.oName(lJnts[-1])
			oCtrl_aim = controls.create(oJntName.sPart, sSide = oJntName.sSide, iIndex = oJntName.iIndex, iStacks = self._iStacks, bSub = self._bSub, sParent = sGrpCtrl, sPos = lJnts[-1], iRotateOrder = iRotateOrder, sShape = 'cube', fSize = 4, lLockHideAttrs = self._lLockHideAttrs)
			
			cmds.pointConstraint(oCtrl_root.sOutput, lJnts[0], mo = False)
			#### control connect out node
			sConnectOutCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRigConnectOutCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = oCtrl.sOutput, bVis = True)
			constraints.constraint([lJnts[-1], sConnectOutCtrl], sType = 'parent', bForce = True, bMaintainOffset = False)			
			sParentIk = oCtrl_aim.sOutput
			lCtrls = [oCtrl_root.sName, oCtrl_aim.sName]
		else:
			sParentIk = self._sConnectInCtrl
			lCtrls = ''

		sGrpIkHndle = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRigIkHndle' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sParentIk, bVis = False)
		cmds.parent(sIkHnd, sGrpIkHndle)

		## write rig info
		sString_lJnts = self._convertListToString(lJnts)
		sString_lCtrls = self._convertListToString(lCtrls)
		lRigInfo = ['ikSCsolverRig', self._sConnectInJnt, self._sConnectInCtrl, lJnts[-1], sConnectOutCtrl, sString_lJnts, sString_lCtrls, sIkHnd, sGrpCtrl, sGrp]
		lAttrs = ['sModuleType', 'sConnectInJnt', 'sConnectInCtrl', 'sConnectOutJnt', 'sConnectOutCtrl', 'lJnts', 'lCtrls', 'sIkHnd', 'sGrpCtrl', 'sModuleNode']
		self._writeRigInfo(sGrp, lRigInfo, lAttrs)

		self._getRigInfo(sGrp)

	def _getRigInfo(self, sModuleNode):
		super(ikRPSolverRig, self)._getRigInfo(sModuleNode)
		self._sIkHnd = cmds.getAttr('%s.sIkHnd' %sModuleNode)
