## import
import maya.cmds as cmds
import maya.mel as mel
## import libs
import common.transforms as transforms
import namingAPI.naming as naming
import riggingAPI.joints as joints
import riggingAPI.constraints as constraints
import riggingAPI.controls as controls
import modelingAPI.surfaces as surfaces
import baseLimbRig
## function
class ribbonRig(baseLimbRig.baseLimbRig):
	"""docstring for ribbonRig"""
	def __init__(self, *args, **kwargs):
		super(ribbonRig, self).__init__()

		if args:
			self.__getRigInfo(args[0])
		else:
			sName = kwargs.get('sName', 'Ribbon')
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
			self._sGrpNode = sGrpNode

	@property
	def sConnectOutRootCtrl(self):
		return self._sConnectOutRootCtrl

	@property
	def sRibbon(self):
		return self._sRibbon

	def create(self):
		sGrp = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRig' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInJnt)
		sGrpCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInCtrl)
		sGrpNode = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sNode' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sGrpNode)

		lJnts = []
		for i, sBpJnt in enumerate(self._lBpJnts):
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			oJntName.sPart = '%s%s' %(oJntName.sPart, self._sName)
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sGrp)
			lJnts.append(sJnt)

		## create ribbon surface
		
		## if no control bpjnt, create controls, cluster ribbon
		lCtrls = []
		if not self._lBpCtrls:
			sRibbon = surfaces.createRibbonFromNodes(naming.oName(sType = 'surface', sSide = self._sSide, sPart = '%s%s' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lJnts, bAuto = True, fWidth = 2, bNormalize = False, sParent = sGrpNode)
			cmds.setAttr('%s.v' %sRibbon, 0)
			lCls = surfaces.clusterSurface(sRibbon, sUV = 'u')
			cmds.rebuildSurface(sRibbon, ch = True, su = len(lJnts) - 1, sv = 1, dv = 3, du = 3)
			for i, sCls in enumerate(lCls):
				oCtrl = controls.create('%s%s' %(self._sPart, self._sName), sSide = self._sSide, iIndex = i, iStacks = self._iStacks, bSub = self._bSub, sParent = sGrpCtrl, sPos = sCls, sShape = 'cube', fSize = 4, lLockHideAttrs = self._lLockHideAttrs)
				cmds.parent(sCls, oCtrl.sOutput)
				lCtrls.append(oCtrl.sName)
		else:
			sRibbon = surfaces.createRibbonFromNodes(naming.oName(sType = 'surface', sSide = self._sSide, sPart = '%s%s' %(self._sPart, self._sName), iIndex = self._iIndex).sName, self._lBpCtrls, bAuto = True, fWidth = 2, bNormalize = False, sParent = sGrpNode)
			cmds.setAttr('%s.v' %sRibbon, 0)
			lCls = surfaces.clusterSurface(sRibbon, sUV = 'u')
			cmds.rebuildSurface(sRibbon, ch = True, su = len(lJnts) - 1, sv = 1, dv = 3, du = 3)
			for i, sCls in enumerate(lCls):
				oJntName = naming.oName(self._lBpCtrls[i])
				iRotateOrder = cmds.getAttr('%s.ro' %self._lBpCtrls[i])
				oCtrl = controls.create('%s%s' %(oJntName.sPart, self._sName), sSide = oJntName.sSide, iIndex = oJntName.iIndex, iStacks = self._iStacks, bSub = self._bSub, sParent = sGrpCtrl, iRotateOrder = iRotateOrder, sPos = self._lBpCtrls[i], sShape = 'cube', fSize = 4, lLockHideAttrs = self._lLockHideAttrs)
				cmds.parent(sCls, oCtrl.sOutput)
				lCtrls.append(oCtrl.sName)

		### attach joints
		sGrpFollicle, lFollicles = constraints.follicleConstraint(sRibbon, lJnts, bMaintainOffset = True)
		cmds.parent(sGrpFollicle, sGrpNode)

		#### control connect out node
		sConnectOutCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRigConnectOutCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sGrpCtrl, bVis = True)
		constraints.constraint([lJnts[-1], sConnectOutCtrl], sType = 'parent', bForce = True, bMaintainOffset = True)
		
		#### control root connect out node
		sConnectOutRootCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRigConnectOutRootCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sGrpCtrl, bVis = True)
		constraints.constraint([lJnts[0], sConnectOutRootCtrl], sType = 'parent', bForce = True, bMaintainOffset = True)
		

		## write rig info
		sString_lJnts = self._convertListToString(lJnts)
		sString_lCtrls = self._convertListToString(lCtrls)
		lRigInfo = ['ribbonRig', self._sConnectInJnt, self._sConnectInCtrl, lJnts[-1], sConnectOutCtrl, sConnectOutRootCtrl, sString_lJnts, sString_lCtrls, sRibbon, sGrpCtrl, sGrp]
		lAttrs = ['sModuleType', 'sConnectInJnt', 'sConnectInCtrl', 'sConnectOutJnt', 'sConnectOutCtrl', 'sConnectOutRootCtrl', 'lJnts', 'lCtrls', 'sRibbon', 'sGrpCtrl', 'sModuleNode']
		self._writeRigInfo(sGrp, lRigInfo, lAttrs)

		self._getRigInfo(sGrp)

	def _getRigInfo(self, sModuleNode):
		super(ribbonRig, self)._getRigInfo(sModuleNode)
		if cmds.attributeQuery('sRibbon', node = sModuleNode, ex = True):
			self._sRibbon = cmds.getAttr('%s.sRibbon' %sModuleNode)
		if cmds.attributeQuery('sConnectOutRootCtrl', node = sModuleNode, ex = True):
			self._sConnectOutRootCtrl = cmds.getAttr('%s.sConnectOutRootCtrl' %sModuleNode)

	


