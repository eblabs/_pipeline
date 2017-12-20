## import
import maya.cmds as cmds
import maya.mel as mel
## import libs
import common.transforms as transforms
import namingAPI.naming as naming
import namingAPI.namingDict as namingDict
import riggingAPI.joints as joints
import riggingAPI.constraints as constraints
import riggingAPI.controls as controls
import common.attributes as attributes
import baseLimbRig

class blendModeRig(baseLimbRig.baseLimbRig):
	"""docstring for blendModeRig"""
	def __init__(self, *args, **kwargs):
		super(blendModeRig, self).__init__()
		
		if args:
			self._getRigInfo(args[0])
		else:
			dRigLimbs = kwargs.get('dRigLimbs', None)
			sName = kwargs.get('sName', 'blendMode')
			sSide = kwargs.get('sSide', 'm')
			sPart = kwargs.get('sPart', None)
			iIndex = kwargs.get('iIndex', None)
			lBpJnts = kwargs.get('lBpJnts', None)
			sConnectInCtrl = kwargs.get('sConnectInCtrl', 'controls')
			sConnectInJnt = kwargs.get('sConnectInJnt', 'rigJoints')
			sConstraintType = kwargs.get('sConstraintType', 'parent')

			#dRigLimbs = {'fk': {'class': armFkRig.armFkRig}}

			self._dRigLimbs = dRigLimbs
			self._sName = sName
			self._sSide = sSide
			self._sPart = sPart
			self._iIndex = iIndex
			self._lBpJnts = lBpJnts
			self._sConnectInCtrl = sConnectInCtrl
			self._sConnectInJnt = sConnectInJnt
			self._sConstraintType = sConstraintType

	@property
	def lModuleNodes(self):
		return self._lModuleNodes

	def lModuleIndex(self):
		return self._lModuleIndex

	def create(self):
		sGrp = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sRig' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInJnt)
		sGrpCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sConnectInCtrl)
		sParent_jnt = sGrp
		lJnts = []
		for i, sBpJnt in enumerate(self._lBpJnts):
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			lJnts.append(sJnt)
			sParent_jnt = sJnt
		
		## rig each limb
		iJnts_min = len(lJnts)
		dRigLimbs = {}
		lCtrls = []
		for sMode in self._dRigLimbs.keys():
			dRigLimbs_each = {sMode: {
										'iIndex': 0,
										'class': None,
										'lJnts': None,
											}}
			oLimb = self._dRigLimbs[sMode]['class'](sSide = self._sSide, iIndex = self._iIndex)
			oLimb._lBpJnts = self._lBpJnts
			oLimb._sConnectInJnt = sGrp
			oLimb._sConnectInCtrl = sGrpCtrl
			oLimb.create()
			
			if self._dRigLimbs[sMode].has_key('iIndex'):
				dRigLimbs_each[sMode]['iIndex'] = self._dRigLimbs[sMode]['iIndex']
			else:
				dRigLimbs_each[sMode]['iIndex'] = namingDict.spaceDict[sMode]

			dRigLimbs_each[sMode]['class'] = oLimb

			if hasattr(oLimb, 'lJntsOutput'):
				dRigLimbs_each[sMode]['lJnts'] = oLimb.lJntsOutput
				if len(oLimb.lJntsOutput) < iJnts_min:
					iJnts_min = len(oLimb.lJntsOutput)
			else:
				dRigLimbs_each[sMode]['lJnts'] = oLimb.lJnts
				if len(oLimb.lJnts) < iJnts_min:
					iJnts_min = len(oLimb.lJnts)

			lCtrls += oLimb.lCtrls

			dRigLimbs.update(dRigLimbs_each)

		## add shape node
		sCtrlShape = naming.oName(sType = 'ctrl', sSide = self._sSide, sPart = self._sPart, iIndex = self._iIndex).sName
		controls.addCtrlShape(lCtrls, sCtrlShape, bVis = False)

		## blend constraint joints
		for i in range(0, iJnts_min):
			lDrivers = []
			#dDrivers = {'cog': {'iIndex': 0, 'sOutput': 'ctrl_m_cog'}}
			dDrivers = {}
			for sMode in dRigLimbs.keys():
				dDriver_each = {sMode: {'iIndex': dRigLimbs[sMode]['iIndex'], 'sOutput': dRigLimbs[sMode]['lJnts'][i]}}
				dDrivers.update(dDriver_each)
			constraints.spaceConstraint(dDrivers, lJnts[i], sType = self._sConstraintType, sCtrl = sCtrlShape, bMaintainOffset = False, sName = self._sName, lDefaultVal = None)

		## vis switch
		sCondition = naming.oName(sType = 'condition', sSide = self._sSide, sPart = '%s%s%sSelector' %(self._sPart, self._sName[0].upper(), self._sName[1:]), iIndex = self._iIndex).sName
		cmds.createNode('condition', name = sCondition)
		cmds.connectAttr('%s.%sModeA' %(sCtrlShape, self._sName), '%s.colorIfTrueR' %sCondition)
		cmds.connectAttr('%s.%sModeB' %(sCtrlShape, self._sName), '%s.colorIfFalseR' %sCondition)
		cmds.connectAttr('%s.%sModeBlend' %(sCtrlShape, self._sName), '%s.firstTerm' %sCondition)
		cmds.setAttr('%s.secondTerm' %sCondition, 0.5)
		cmds.setAttr('%s.operation' %sCondition, 4)

		lAttrs = []
		lEnumIndex = []
		for sMode in dRigLimbs.keys():
			lAttrs.append('%s.v' %dRigLimbs[sMode]['class'].sGrpCtrl)
			lEnumIndex.append(dRigLimbs[sMode]['iIndex'])

		attributes.enumToMultiAttrs('outColorR', lAttrs, iEnumRange = len(lEnumIndex), lEnumIndex = lEnumIndex, sEnumObj = sCondition)
		#enumToMultiAttrs(sEnumAttr, lAttrs, iEnumRange = 2, lEnumIndex = None, lValRange = [[0,1]], sEnumObj = None)

		#### control connect out node
		sConnectOutCtrl = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = self._sSide, sPart = '%s%sConnectOutCtrl' %(self._sPart, self._sName), iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sGrpCtrl, bVis = True)
		constraints.constraint([lJnts[-1], sConnectOutCtrl], sType = 'parent', bForce = True, bMaintainOffset = True)

		lCtrls = sCtrlShape

		## write rig info
		sModuleNodes = ''
		sModuleIndex = ''
		for sMode in dRigLimbs.keys():
			sModuleNodes += '%s,' %dRigLimbs[sMode]['class'].sModuleNode
			sModuleIndex += '%d,' %dRigLimbs[sMode]['iIndex']

		sString_lJnts = self._convertListToString(lJnts)
		sString_lCtrls = self._convertListToString(lCtrls)
		lRigInfo = ['blendModeRig', sGrp, self._sConnectInJnt, self._sConnectInCtrl, lJnts[-1], sConnectOutCtrl, sString_lJnts, sString_lCtrls, sGrpCtrl, sModuleNodes[:-1], sModuleIndex[:-1]]
		lAttrs = ['sModuleType', 'sModuleNode', 'sConnectInJnt', 'sConnectInCtrl', 'sConnectOutJnt', 'sConnectOutCtrl', 'lJnts', 'lCtrls', 'sGrpCtrl', 'lModuleNodes', 'lModuleIndex']

		self._writeRigInfo(sGrp, lRigInfo, lAttrs)

		self._getRigInfo(sGrp)

	def _getRigInfo(self, sModuleNode):
		super(blendModeRig, self)._getRigInfo(sModuleNode)

		sModuleNodesString = cmds.getAttr('%s.lModuleNodes' %sModuleNode)
		self._lModuleNodes = sModuleNodesString.split(',')
		sModuleIndexString = cmds.getAttr('%s.lModuleIndex' %sModuleNode)
		lModuleIndex = sModuleIndexString.split(',')
		self._lModuleIndex = []
		for sIndex in lModuleIndex:
			self._lModuleIndex.append(int(sIndex))
