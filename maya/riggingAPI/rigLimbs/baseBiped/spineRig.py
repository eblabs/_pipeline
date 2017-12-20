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
import riggingAPI.rigLimbs.baseLimbs.ikSplineRig as ikSplineRig
import riggingAPI.rigLimbs.baseLimbs.ribbonRig as ribbonRig
import common.attributes as attributes
## function
class spineRig(ribbonRig.ribbonRig):
	"""docstring for spineRig"""
	def __init__(self, *args, **kwargs):
		super(spineRig, self).__init__(*args, **kwargs)

		self._sSide = 'middle'
		self._lBpJnts = cmds.ls('%s_*' %naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'spine').sName, type = 'joint')
		self._lBpCtrls = [
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'spineCtrl', iIndex = 1).sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'spineCtrl', iIndex = 2).sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'spineCtrl', iIndex = 3).sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'spineCtrl', iIndex = 4).sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'spineCtrl', iIndex = 5).sName,
							]

		self._lBpCtrlsPelvis = [
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'pelvisCtrl').sName,
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'pelvisEndCtrl').sName,
									]

		self._sName = 'Ribbon'
		self._sPart = 'spine'
		self._sNameRig = 'IkFkRibbon'
		self._sPartPelvis = 'pelvis'
		self._lCtrlOrient = ['z', 'y']

	@property
	def lModuleNodes(self):
		return self._lModuleNodes

	def create(self):
		self._lBpCtrlsSpine = self._lBpCtrls
		self._lBpCtrls = [self._lBpCtrlsPelvis[1]] + self._lBpCtrls

		sGrp = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRig' %(self._sPart, self._sNameRig), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInJnt)
		sGrpCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sCtrl' %(self._sPart, self._sNameRig), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInCtrl)
		sGrpNode = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sNode' %(self._sPart, self._sNameRig), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sGrpNode)

		self._sConnectInJnt = sGrp
		self._sConnectInCtrl = sGrpCtrl
		self._sGrpNode = sGrpNode

		super(spineRig, self).create()


		## fk rig

		oSpineFk = fkJointChainRig.fkJointChainRig(
													sName = 'Fk',
													sSide = self._sSide,
													sPart = self._sPart,
													iIndex = self._iIndex,
													lBpJnts = self._lBpCtrlsSpine,
													sConnectInCtrl = self._sConnectInCtrl,
													sConnectInJnt = self._sConnectInJnt,
													bSub = self._bSub,
													iStacks = self._iStacks,
													lLockHideAttrs = self._lLockHideAttrs)

		oSpineFk.create()

		## pelvis rig
		oPelvisFk = fkJointChainRig.fkJointChainRig(
													sName = 'Fk',
													sSide = self._sSide,
													sPart = self._sPartPelvis,
													iIndex = self._iIndex,
													lBpJnts = self._lBpCtrlsPelvis,
													sConnectInCtrl = self._sConnectInCtrl,
													sConnectInJnt = self._sConnectInJnt,
													bSub = self._bSub,
													iStacks = self._iStacks,
													lLockHideAttrs = self._lLockHideAttrs
														)
		oPelvisFk.create()

		## ik spline
		oSpineIk = ikSplineRig.ikSplineRig(
											sName = 'ikSpline',
											sSide = self._sSide,
											sPart = self._sPart,
											iIndex = self._iIndex,
											lBpJnts = self._lBpCtrls,
											sConnectInCtrl = self._sConnectInCtrl,
											sConnectInJnt = self._sConnectInJnt,
											sGrpNode = self._sGrpNode,
											bSub = self._bSub,
											iStacks = self._iStacks,
											lLockHideAttrs = self._lLockHideAttrs,
											lBpCtrls = self._lBpCtrlsSpine[:-1],
											bOrientTop = True,
											bOrientBot = True,
											lCtrlOrient = self._lCtrlOrient,
											)
		oSpineIk.create()

		## constraint and hidde ribbon controls
		for i, sCtrl in enumerate(self._lCtrls):
			oCtrl = controls.oControl(sCtrl)
			cmds.parentConstraint(oSpineIk.lJnts[i], oCtrl.sPasser, mo = False)
			cmds.setAttr('%s.v' %oCtrl.sPasser, 0)

		## constraint ik controls
		## pelvis
		oCtrl = controls.oControl(oSpineIk.lCtrls[0])
		constraints.constraint([oPelvisFk.lJnts[0], oCtrl.sPasser], sType = 'parent', bMaintainOffset = True)

		## spine
		for i, sCtrl in enumerate(oSpineIk.lCtrls[1:]):
			oCtrl = controls.oControl(sCtrl)
			if i == 0:
				constraints.constraint([oSpineFk.lJnts[i], oCtrl.sPasser], sType = 'parent', bMaintainOffset = True)
			else:
				constraints.constraint([oSpineFk.lJnts[i + 1], oCtrl.sPasser], sType = 'parent', bMaintainOffset = True)
		## add ctrl shape
		sCtrlShape = naming.oName(sType = 'ctrl', sSide = self._sSide, sPart = self._sPart, iIndex = self._iIndex).sName
		controls.addCtrlShape(oSpineIk.lCtrls + oSpineFk.lCtrls + oPelvisFk.lCtrls, sCtrlShape, bVis = False)

		cmds.addAttr(sCtrlShape, ln = 'ikCtrlVis', at = 'long', min = 0, max = 1)
		cmds.setAttr('%s.ikCtrlVis' %sCtrlShape, channelBox = True)
		attributes.connectAttrs(['%s.ikCtrlVis' %sCtrlShape], ['%s.v' %oSpineIk.sGrpCtrl], bForce = True)

		## write rig info
		sModuleNodes = '%s,%s,%s' %(oSpineFk.sModuleNode, oPelvisFk.sModuleNode, oSpineIk.sModuleNode)

		sString_lJnts = self._convertListToString(self._lJnts)
		sString_lCtrls = self._convertListToString(oSpineFk.lCtrls + oPelvisFk.lCtrls + oSpineIk.lCtrls)
		lRigInfo = ['spineRig', self._sConnectInJnt, self._sConnectInCtrl, self._sConnectOutJnt, self._sConnectOutCtrl, self._sConnectOutRootCtrl,sString_lJnts, sString_lCtrls, sGrpCtrl, sModuleNodes, sGrp]
		lAttrs = ['sModuleType', 'sConnectInJnt', 'sConnectInCtrl', 'sConnectOutJnt', 'sConnectOutCtrl', 'sConnectOutRootCtrl', 'lJnts', 'lCtrls', 'sGrpCtrl', 'lModuleNodes', 'sModuleNode']
		self._writeRigInfo(sGrp, lRigInfo, lAttrs)

		self._getRigInfo(sGrp)

	def _getRigInfo(self, sModuleNode):
		super(spineRig, self)._getRigInfo(sModuleNode)
		if cmds.attributeQuery('lModuleNodes', node = sModuleNode, ex = True):
			sModuleNodesString = cmds.getAttr('%s.lModuleNodes' %sModuleNode)
			self._lModuleNodes = sModuleNodesString.split(',')

