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
import common.attributes as attributes
import baseLimbRig
## function
class ikSplineRig(baseLimbRig.baseLimbRig):
	"""docstring for ikSplineRig"""
	def __init__(self, *args, **kwargs):
		super(ikSplineRig, self).__init__()

		if args:
			self._getRigInfo(args[0])
		else:
			sName = kwargs.get('sName', 'IkSpline')
			sSide = kwargs.get('sSide', 'm')
			sPart = kwargs.get('sPart', None)
			iIndex = kwargs.get('iIndex', None)
			lBpJnts = kwargs.get('lBpJnts', None)
			sConnectInCtrl = kwargs.get('sConnectInCtrl', 'controls')
			sConnectInJnt = kwargs.get('sConnectInJnt', 'rigJoints')
			sGrpNode = kwargs.get('sGrpNode', 'rigsHide')
			bSub = kwargs.get('bSub', False)
			iStacks = kwargs.get('iStacks', 1)
			lLockHideAttrs = kwargs.get('lLockHideAttrs', ['sx', 'sy', 'sz', 'v'])
			lBpCtrls = kwargs.get('lBpCtrls', None)
			bOrientTop = kwargs.get('bOrientTop', True)
			bOrientBot = kwargs.get('bOrientBot', True)
			lCtrlOrient = kwargs.get('lCtrlOrient', None)

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
			self._lBpCtrls = lBpCtrls
			self._bOrientTop = bOrientTop
			self._bOrientBot = bOrientBot
			self._sGrpNode = sGrpNode
			self._lCtrlOrient = lCtrlOrient

	@property
	def sIkHnd(self):
		return self._sIkHnd

	@property
	def sConnectOutRootCtrl(self):
		return self._sConnectOutRootCtrl

	def create(self):
		sGrp = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRig' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInJnt)
		sGrpCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInCtrl)
		sGrpNode = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sNode' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sGrpNode)
		## twist locs
		sMatcherBot, sOffsetBot = transforms.createTransformMatcherNode(self._lBpJnts[0], sParent = None)
		sMatcherTop, sOffsetTop = transforms.createTransformMatcherNode(self._lBpJnts[-1], sParent = None)

		## create curve
		lBot = []
		lTop = []
		if self._bOrientTop:
			lTop.append(sMatcherTop)
		if self._bOrientBot:
			lBot.append(sMatcherBot)
		sCrv = curves.createCurveOnNodes(naming.oName(sType = 'curve', sSide = self._sSide, sPart = '%s%s' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lBot + self._lBpCtrls + lTop, iDegree = 3, sParent = sGrpNode)
		cmds.setAttr('%s.v' %sCrv, 0)

		## create joints
		sParent_jnt = sGrp
		lJnts = []
		for i, sBpJnt in enumerate(self._lBpJnts):
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			oJntName.sPart = '%s%s' %(oJntName.sPart, self._sName)
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			lJnts.append(sJnt)
			sParent_jnt = sJnt

		## create cluster
		lClsHnds = curves.clusterCurve(sCrv)

		## create contorls
		lCtrls = []
		if not self._lBpCtrls:
			self._lBpCtrls = self._lBpJnts
		for i, sJnt in enumerate(self._lBpCtrls):
			oJntName = naming.oName(sJnt)
			iRotateOrder = cmds.getAttr('%s.ro' %sJnt)
			oCtrl = controls.create('%s%s' %(oJntName.sPart, self._sName), sSide = oJntName.sSide, iIndex = oJntName.iIndex, iStacks = self._iStacks, bSub = self._bSub, sParent = sGrpCtrl, sPos = sJnt, iRotateOrder = iRotateOrder, sShape = 'cube', fSize = 8, lLockHideAttrs = self._lLockHideAttrs)
			if self._lCtrlOrient:
				transforms.worldOrientTransform(oCtrl.sPasser, sFoward = self._lCtrlOrient[0], sUp = self._lCtrlOrient[1])
			if self._bOrientBot:
				cmds.parent(lClsHnds[i + 1], oCtrl.sOutput)
				if i == 0:
					cmds.parent(lClsHnds[0], oCtrl.sOutput)
			else:
				cmds.parent(lClsHnds[i], oCtrl.sOutput)
			if self._bOrientTop:
				if i == len(self._lBpCtrls) - 1:
					cmds.parent(lClsHnds[-1], oCtrl.sOutput)
			lCtrls.append(oCtrl.sName)

		## rebuild curve
		curves.rebuildCurveWithSameCvNum(sCrv)

		## spline ik handle
		sIkHnd = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%s%s' %(self._sPart, self._sName), iindex = self._iIndex).sName
		cmds.ikHandle(sj = lJnts[0], ee = lJnts[-1], sol = 'ikSplineSolver', c = sCrv, ccv = False, pcv = False, name = sIkHnd)
		cmds.makeIdentity(lJnts, apply = True, t = 1, r = 1, s = 1)
		cmds.parent(sIkHnd, sGrpCtrl)
		cmds.setAttr('%s.v' %sIkHnd, 0)

		## advanced twist
		for i, sCtrl in enumerate([lCtrls[0], lCtrls[-1]]):
			oCtrl = controls.oControl(sCtrl)
			cmds.parent([sOffsetBot, sOffsetTop][i], oCtrl.sOutput)
		cmds.setAttr('%s.dTwistControlEnable' %sIkHnd, 1)
		cmds.setAttr('%s.dWorldUpType' %sIkHnd, 4)
		attributes.connectAttrs(['%s.worldMatrix[0]' %sMatcherBot, '%s.worldMatrix[0]' %sMatcherTop], ['%s.dWorldUpMatrix' %sIkHnd, '%s.dWorldUpMatrixEnd' %sIkHnd], bForce = True)

		#### control connect out node
		sConnectOutCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRigConnectOutCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sGrpCtrl, bVis = True)
		constraints.constraint([lJnts[-1], sConnectOutCtrl], sType = 'parent', bForce = True, bMaintainOffset = True)
		
		#### control root connect out node
		sConnectOutRootCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRigConnectOutRootCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sGrpCtrl, bVis = True)
		constraints.constraint([lJnts[0], sConnectOutRootCtrl], sType = 'parent', bForce = True, bMaintainOffset = True)
		

		## write rig info
		sString_lJnts = self._convertListToString(lJnts)
		sString_lCtrls = self._convertListToString(lCtrls)
		lRigInfo = ['ikSplineRig', self._sConnectInJnt, self._sConnectInCtrl, lJnts[-1], sConnectOutCtrl, sConnectOutRootCtrl, sString_lJnts, sString_lCtrls, sIkHnd, sGrpCtrl, sGrp]
		lAttrs = ['sModuleType', 'sConnectInJnt', 'sConnectInCtrl', 'sConnectOutJnt', 'sConnectOutCtrl', 'sConnectOutRootCtrl', 'lJnts', 'lCtrls', 'sIkHnd', 'sGrpCtrl', 'sModuleNode']
		self._writeRigInfo(sGrp, lRigInfo, lAttrs)

		self._getRigInfo(sGrp)

	def _getRigInfo(self, sModuleNode):
		super(ikSplineRig, self)._getRigInfo(sModuleNode)
		self._sIkHnd = cmds.getAttr('%s.sIkHnd' %sModuleNode)
		self._sConnectOutRootCtrl = cmds.getAttr('%s.sConnectOutRootCtrl' %sModuleNode)

