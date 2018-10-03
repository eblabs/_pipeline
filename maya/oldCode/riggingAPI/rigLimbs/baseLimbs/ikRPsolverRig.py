## import
import maya.cmds as cmds
import maya.mel as mel
## import libs
import common.transforms as transforms
import namingAPI.naming as naming
import riggingAPI.joints as joints
import riggingAPI.constraints as constraints
import riggingAPI.controls as controls
import modelingAPI.curves as curves
import baseLimbRig
## function
class ikRPsolverRig(baseLimbRig.baseLimbRig):
	"""docstring for ikRPsolverRig"""
	def __init__(self, *args, **kwargs):
		super(ikRPsolverRig, self).__init__()

		if args:
			self._getRigInfo(args[0])
		else:
			sName = kwargs.get('sName', 'IkRPsolver')
			sSide = kwargs.get('sSide', 'm')
			sPart = kwargs.get('sPart', None)
			iIndex = kwargs.get('iIndex', None)
			lBpJnts = kwargs.get('lBpJnts', None)
			sBpCtrl = kwargs.get('sBpCtrl', None)
			sBpPv = kwargs.get('sBpPv', None)
			sBpRoot = kwargs.get('sBpRoot', None)
			bOrient = kwargs.get('bOrient', True)
			sConnectInCtrl = kwargs.get('sConnectInCtrl', 'controls')
			sConnectInJnt = kwargs.get('sConnectInJnt', 'rigJoints')
			bSub = kwargs.get('bSub', False)
			iStacks = kwargs.get('iStacks', 1)
			lLockHideAttrs = kwargs.get('lLockHideAttrs', ['sx', 'sy', 'sz', 'v'])

			self._sName = sName
			self._lBpJnts = lBpJnts
			self._sBpCtrl = sBpCtrl
			self._sBpPv = sBpPv
			self._sBpRoot = sBpRoot
			self._sSide = sSide
			self._sPart = sPart
			self._iIndex = iIndex
			self._bOrient = bOrient
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
		sGrpCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInCtrl)
		
		sParent_jnt = sGrp
		lJnts = []
		for i, sBpJnt in enumerate(self._lBpJnts):
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			oJntName.sPart = '%s%s' %(oJntName.sPart, self._sName)
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			lJnts.append(sJnt)
			sParent_jnt = sJnt

		lCtrls = []
		for i, sBpJnt in enumerate([self._sBpRoot, self._sBpPv, self._sBpCtrl]):
			oJntName = naming.oName(sBpJnt)
			iRotateOrder = cmds.getAttr('%s.ro' %sBpJnt)
			if i == 2:
				lLockHideAttrs = self._lLockHideAttrs
			else:
				lLockHideAttrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'] 
			oCtrl = controls.create(oJntName.sPart, sSide = oJntName.sSide, iIndex = oJntName.iIndex, iStacks = self._iStacks, bSub = self._bSub, sParent = sGrpCtrl, sPos = sBpJnt, iRotateOrder = iRotateOrder, sShape = 'cube', fSize = 8, lLockHideAttrs = lLockHideAttrs)
			lCtrls.append(oCtrl.sName)

		## ik handle
		if self._bOrient:
			sJntEnd_rp = lJnts[-2]
			sIkHnd_sc = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sSCsolver' %self._sPart, iIndex = self._iIndex).sName
			cmds.ikHandle(sj = lJnts[-2], ee = lJnts[-1], sol = 'ikSCsolver', name = sIkHnd_sc)
		else:
			sJntEnd_rp = lJnts[-1]
			sIkHnd_sc = None
		sIkHnd_rp = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sRPsolver' %self._sPart, iIndex = self._iIndex).sName
		cmds.ikHandle(sj = lJnts[0], ee = sJntEnd_rp, sol = 'ikRPsolver', name = sIkHnd_rp)

		#### parent ik handle
		oCtrl = controls.oControl(lCtrls[2])
		sGrpIkHndle = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRigIkHndle' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = oCtrl.sOutput, bVis = False)
		cmds.parent(sIkHnd_rp, sGrpIkHndle)
		if sIkHnd_sc:
			cmds.parent(sIkHnd_sc, sGrpIkHndle)

		#### pole vector
		oCtrl = controls.oControl(lCtrls[1])
		cmds.poleVectorConstraint(oCtrl.sOutput, sIkHnd_rp)
		## pole vector line
		curves.createCurveLine(naming.oName(sType = 'curve', sSide = self._sSide, sPart = '%sPvLineIk' %self._sPart, iIndex = self._iIndex).sName, [lJnts[1], oCtrl.sOutput], sParent = sGrpCtrl)

		#### root control
		oCtrl = controls.oControl(lCtrls[0])
		cmds.pointConstraint(oCtrl.sOutput, lJnts[0], mo = False)

		#### control connect out node
		sConnectOutCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRigConnectOutCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = oCtrl.sOutput, bVis = True)
		constraints.constraint([lJnts[-1], sConnectOutCtrl], sType = 'parent', bForce = True, bMaintainOffset = True)
		## write rig info
		sString_lJnts = self._convertListToString(lJnts)
		sString_lCtrls = self._convertListToString(lCtrls)
		lRigInfo = ['ikRPsolverRig', self._sConnectInJnt, self._sConnectInCtrl, lJnts[-1], sConnectOutCtrl, sString_lJnts, sString_lCtrls, sIkHnd_rp, sGrpCtrl, sGrp]
		lAttrs = ['sModuleType', 'sConnectInJnt', 'sConnectInCtrl', 'sConnectOutJnt', 'sConnectOutCtrl', 'lJnts', 'lCtrls', 'sIkHnd', 'sGrpCtrl', 'sModuleNode']
		self._writeRigInfo(sGrp, lRigInfo, lAttrs)

		self._getRigInfo(sGrp)

	def _getRigInfo(self, sModuleNode):
		super(ikRPsolverRig, self)._getRigInfo(sModuleNode)
		if cmds.attributeQuery('sIkHnd', node = sModuleNode, ex = True):
			self._sIkHnd = cmds.getAttr('%s.sIkHnd' %sModuleNode)


