## import
import maya.cmds as cmds
import maya.mel as mel
## import libs
import common.transforms as transforms
import namingAPI.naming as naming
import common.attributes as attributes
import riggingAPI.controls as controls
import riggingAPI.constraints as constraints
class baseRigNode(object):
	"""docstring for baseRig"""
	def __init__(self):
		super(baseRigNode, self).__init__()
		self.lRes = ['high', 'mid', 'low', 'proxy', 'sim']

	def create(self):
		self.__baseNode()
		self.__baseControls()
		
	def __baseNode(self):
		sMaster = transforms.createTransformNode('master', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
		## add attr
		### resolution
		sEnumRes = ''
		for sRes in self.lRes:
			sEnumRes += '%s:' %sRes
		sEnumRes = sEnumRes[:-1] 
		cmds.addAttr(sMaster, ln = 'resolution', at = 'enum', enumName = sEnumRes, keyable = False, dv = 0)
		cmds.setAttr('%s.resolution' %sMaster, channelBox = True)
		### geometry
		cmds.addAttr(sMaster, ln = 'geometries', at = 'enum', enumName = 'on:off:tempelate:reference', keyable = False, dv = 3)
		cmds.setAttr('%s.geometries' %sMaster, channelBox = True)
		### joints
		cmds.addAttr(sMaster, ln = 'joints', at = 'enum', enumName = 'on:off:tempelate:reference', keyable = False, dv = 1)
		cmds.setAttr('%s.joints' %sMaster, channelBox = True)
		### controls
		cmds.addAttr(sMaster, ln = 'controls', at = 'long', min = 0, max = 1, keyable = False, dv = 1)
		cmds.setAttr('%s.controls' %sMaster, channelBox = True)
		### rigs
		cmds.addAttr(sMaster, ln = 'rigs', at = 'long', min = 0, max = 1, keyable = False, dv = 0)
		cmds.setAttr('%s.rigs' %sMaster, channelBox = True)

		## add groups
		sDoNotTouch = transforms.createTransformNode('doNotTouch', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sMaster)
		sControls = transforms.createTransformNode('controls', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sMaster)

		sGeometry = transforms.createTransformNode('geometries', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sDoNotTouch)
		sRigGeometry = transforms.createTransformNode('rigGeometries', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sDoNotTouch)	
		sJoints = transforms.createTransformNode('joints', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sDoNotTouch)
		sRigs = transforms.createTransformNode('rigs', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sDoNotTouch)
		sRigsShow = transforms.createTransformNode('rigsShow', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sRigs)
		sRigsHide = transforms.createTransformNode('rigsHide', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sRigs)
		
		## connect attrs
		lGrps = [sGeometry, sJoints]
		for i, sAttr in enumerate(['geometries', 'joints']):
			sConditionVis = naming.oName(sType = 'condition', sSide = 'middle', sPart = '%sVis' %sAttr).sName
			cmds.createNode('condition', name = sConditionVis)
			cmds.connectAttr('%s.%s' %(sMaster, sAttr), '%s.firstTerm' %sConditionVis)
			cmds.setAttr('%s.secondTerm' %sConditionVis, 1)
			cmds.setAttr('%s.colorIfTrueR' %sConditionVis, 0)
			cmds.setAttr('%s.colorIfFalseR' %sConditionVis, 1)
			attributes.connectAttrs(['%s.outColorR' %sConditionVis], ['%s.v' %lGrps[i]], bForce = True)
			cmds.setAttr('%s.overrideEnabled' %lGrps[i], 1)
			attributes.enumToSingleAttrs(sAttr, ['%s.overrideDisplayType' %lGrps[i]], iEnumRange = 4, lValRange = [[0,0],[0,0],[0,1],[0,2]], sEnumObj = sMaster)
		attributes.connectAttrs(['%s.controls' %sMaster], ['%s.v' %sControls], bForce = True)
		attributes.connectAttrs(['%s.rigs' %sMaster], ['%s.v' %sRigsHide], bForce = True)

		## create res grp for geometry and rig geometry
		lVisAttrs = []
		lValRange = []
		for sRes in self.lRes:
			sGrpGeo = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = 'm', sRes = sRes, sPart = 'geometries').sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = 'geometries')
			sGrpXtrs = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = 'm', sRes = sRes, sPart = 'xtrs').sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sGrpGeo)
			sGrpDef = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = 'm', sRes = sRes, sPart = 'def').sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sGrpGeo)
			sGrpRigGeo = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = 'm', sRes = sRes, sPart = 'rigGeometries').sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = 'rigGeometries')
			attributes.connectAttrs(['%s.v' %sGrpGeo], ['%s.v' %sGrpRigGeo], bForce = True)
			lVisAttrs.append('%s.v' %sGrpGeo)
			lValRange.append([0,1])

		attributes.enumToMultiAttrs('resolution', lVisAttrs, iEnumRange = len(self.lRes), lValRange = lValRange, sEnumObj = sMaster)

		## create def joints grp and rig joints grp
		sDefJoints = transforms.createTransformNode('defJoints', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sJoints)
		sRigJoints = transforms.createTransformNode('rigJoints', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sParent = sJoints)
		cmds.addAttr(sMaster, ln = 'rigJointsVis', at = 'bool')
		cmds.connectAttr('%s.rigJointsVis' %sMaster, '%s.v' %sRigJoints)
		cmds.setAttr('%s.v' %sRigJoints, keyable = False, lock = True, channelBox = False)

	def __baseControls(self):
		## world control
		oCtrl_world = controls.create('world', sSide = 'middle', iStacks = 1, sParent = 'controls', sShape = 'circle', fSize = 10, sColor = 'yellow', lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		## layout control
		oCtrl_layout = controls.create('layout', sSide = 'middle', iStacks = 1, sParent = oCtrl_world.sOutput, sShape = 'triangle', fSize = 9.5, sColor = 'royal heath', lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		## local control
		oCtrl_local = controls.create('local', sSide = 'middle', iStacks = 1, sParent = oCtrl_layout.sOutput, sShape = 'triangle', fSize = 7.5, sColor = 'royal purple', lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
		#### connect scale
		for sCtrl in [oCtrl_world.sName, oCtrl_layout.sName, oCtrl_local.sName]:
			cmds.addAttr(sCtrl, ln = 'rigScale', at = 'float', dv = 1, min = 0, keyable = True)
			attributes.connectAttrs(['%s.rigScale' %sCtrl, '%s.rigScale' %sCtrl, '%s.rigScale' %sCtrl,], ['%s.sx' %sCtrl, '%s.sy' %sCtrl, '%s.sz' %sCtrl], bForce = True)

		#### connect with xtrs
		for sRes in self.lRes:
			sGrpXtrs = naming.oName(sType = 'grp', sSide = 'm', sRes = sRes, sPart = 'xtrs').sName
			constraints.constraint([oCtrl_local.sName, sGrpXtrs], sType = 'all', bMaintainOffset = False, bForce = True)

			

			