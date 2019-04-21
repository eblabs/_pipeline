## External Import
import maya.cmds as cmds
import maya.mel as mel

## Build Script Import
import baseCore
reload(baseCore)
import common.workspaces as workspaces
import common.attributes as attributes
import namingAPI.naming as naming
import modelingAPI.models as models
import modelingAPI.meshes as meshes
import riggingAPI.rigComponents as rigComponents

## baseHierarchy build script
class baseHierarchy(baseCore.baseCore):
	"""docstring for baseHierarchy"""
	def __init__(self):
		super(baseHierarchy, self).__init__()

		#self.generateRigData()

	def rigData(self):
		super(baseHierarchy, self).rigData()
		dData = {
						'dModel': {
									'sProject': None,
									'sAsset': None,
									},

						'dBlueprint':{
										'sProject': None,
										'sAsset': None,
										},

						'lRigGeometry':[
										{
											'sProject': None,
											'sAsset': None,
											},
										],

						'lGeoHierarchy':[
											{
												'sProject': None,
												'sAsset': None,
												},
										],

						'lDeformer': [
										{
											'sProject': None,
											'sAsset': None,
											},
										],

						'lControlShape': [
											{
												'sProject': None,
												'sAsset': None,
												},
											]

						}

		self.dRigData.update(dData)

	def importFunctions(self):
		super(baseHierarchy, self).importFunctions()

		## Pre Build
		self.registerFunction(
								mFunction = self.createNewScene,
								sName = 'Create New Scene',
								sParent = 'Pre Build',
								)

		self.registerFunction(
								mFunction = self.importModel,
								sName = 'Import Model',
								sParent = 'Pre Build',
								)

		self.registerFunction(
								mFunction = self.buildBaseRigNodes,
								sName = 'Build Base Rig Nodes',
								sParent = 'Pre Build',
								)

		self.registerFunction(
								mFunction = self.importBlueprint,
								sName = 'Import Blueprint',
								sParent = 'Pre Build',
								)

		self.registerFunction(
								mFunction = self.importRigGeometry,
								sName = 'Import Rig Geometry',
								sParent = 'Pre Build',
								)

		# Build

		# Post Build
		self.registerFunction(
								mFunction = self.importGeoHierarchy,
								sName = 'Import Geo Hierarchy',
								sParent = 'Post Build',
								)

		self.registerFunction(
								mFunction = self.importDeformer,
								sName = 'Import Deformer',
								sParent = 'Post Build',
								)

		self.registerFunction(
								mFunction = self.importControlShape,
								sName = 'Import Control Shape',
								sParent = 'Post Build'
								)
		
	def createNewScene(self):
		workspaces.createNewScene()
		return True

	def importModel(self):
		bReturn = rigComponents.importModel(self.dRigData['dModel'], self.sProject, self.sAsset)
		self.sModel = self.sAsset
		lChilds = cmds.listRelatives(self.sAsset, c = True, type = 'transform')
		self.lRes = []
		for sChild in lChilds:
			lMeshes = meshes.getMeshesFromGrp(sChild)
			if lMeshes:
				oNameGrp = naming.oName(sChild)
				if oNameGrp.sRes not in self.lRes:
					self.lRes.append(oNameGrp.sRes)

		return bReturn

	def buildBaseRigNodes(self):
		## create master node
		sMaster = transforms.createTransformNode('master', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
		####### add attrs
		sEnumName = ''
		for sRes in self.lRes:
			sEnumName += '%s:' %sRes
		sEnumName = sEnumName[:-1]
		cmds.addAttr(sMaster, ln = 'resolution', at = 'enum', enumName = sEnumName, keyable = False, dv = 0)
		cmds.setAttr('%s.resolution' %sMaster, channelBox = True)
		for sAttr in ['geometry', 'joints', 'controls', 'rigNodes', 'rigGeometry']:
			if sAttr == 'geometry':
				iVal = 3
			elif sAttr == 'controls':
				iVal = 0
			else:
				iVal = 1
			cmds.addAttr(sMaster, ln = sAttr, at = 'enum', enumName = 'on:off:template:reference', keyable = False, dv = iVal)
			cmds.setAttr('%s.%s' %(sMaster, sAttr), channelBox = True)

		cmds.addAttr(sMaster, ln = 'geoDeformMove', nn = 'Geo Deform/Move', at = 'long', min = 0, max = 1, dv =0, keyable = False)
		cmds.setAttr('%s.geoDeformMove' %sMaster, channelBox = True)

		## create control, do not touch group
		sControl = transforms.createTransformNode('controls', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sMaster)
		sDoNotTouch = transforms.createTransformNode('doNotTouch', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sMaster)	

		## create geometry groups
		sGeometry = transforms.createTransformNode('geometry', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sDoNotTouch)
		for sRes in self.lRes:
			sResGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sRes, sPart = 'geo').sName
			sResGrp = transforms.createTransformNode(sResGrp, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sGeometry)
			for sPart in ['xtrs', 'def']:
				sGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sRes, sPart = sPart).sName
				sGrp = transforms.createTransformNode(sGrp, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sResGrp)

		## create joint group
		sJoint = transforms.createTransformNode('joints', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sDoNotTouch)
		for sGrp in ['defJoints', 'rigJoints']:
			transforms.createTransformNode(sGrp, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sJoint)
		
		## create rigNode groups
		sRigNode = transforms.createTransformNode('rigNodes', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sDoNotTouch)
		for sPart in ['transform', 'origin']:
			sGrp = naming.oName(sType = 'group', sSide = 'middle', sPart = 'rigNodes%s' %sPart.title()).sName
			sGrp = transforms.createTransformNode(sGrp, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sRigNode)

		## create rigGeometry groups
		sRigGeometry = transforms.createTransformNode('rigGeometry', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sDoNotTouch)
		for sRes in self.lRes:
			sResGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sRes, sPart = 'rigGeometry').sName
			sResGrp = transforms.createTransformNode(sResGrp, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sRigGeometry)
			for sPart in ['transform', 'origin']:
				sGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sRes, sPart = 'rigGeometry%s' %sPart.title()).sName
				sGrp = transforms.createTransformNode(sGrp, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sParent = sResGrp)
				cmds.setAttr('%s.v' %sGrp, 0)

		## Vis connections
		### resolution
		lAttr = []
		for sRes in self.lRes:
			sResGeoGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sRes, sPart = 'geo').sName
			sResRigGeoGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sRes, sPart = 'rigGeometry').sName
			lAttr.append('%s.v' %sResGeoGrp)
			attributes.connectAttrs(['%s.v' %sResGeoGrp], ['%s.v' %sResRigGeoGrp], bForce = True)
		attributes.enumToMultiAttrs('resolution', lAttr, iEnumRange = len(self.lRes), lValRange = [[0,1]], sEnumObj = sMaster)

		### geometry joints controls rigNodes
		lGrps = [sGeometry, sJoint, sControl, sRigNode, sRigGeometry]
		for i, sAttr in enumerate(['geometry', 'joints', 'controls', 'rigNodes', 'rigGeometry']):
			sConditionVis = naming.oName(sType = 'condition', sSide = 'middle', sPart = '%sVis' %sAttr).sName
			cmds.createNode('condition', name = sConditionVis)
			cmds.connectAttr('%s.%s' %(sMaster, sAttr), '%s.firstTerm' %sConditionVis)
			cmds.setAttr('%s.secondTerm' %sConditionVis, 1)
			cmds.setAttr('%s.colorIfTrueR' %sConditionVis, 0)
			cmds.setAttr('%s.colorIfFalseR' %sConditionVis, 1)
			attributes.connectAttrs(['%s.outColor' %sConditionVis], ['%s.v' %lGrps[i]], bForce = True)
			cmds.setAttr('%s.overrideEnabled' %lGrps[i], 1)
			attributes.enumToSingleAttrs(sAttr, ['%s.overrideDisplayType' %lGrps[i]], iEnumRange = 4, lValRange = [[0,0],[0,0],[0,1],[0,2]], sEnumObj = sMaster)

		## create ctrls
		fWidth, fHeight, fDepth = transforms.getBoundingBoxInfo(self.sAsset)
		fCtrlSize = fWidth * fDepth * 1.2
		### world ctrl
		sParentCtrl = sControl
		lCtrlShape = [['circle', 'yellow'], ['triangle', 'royal heath'], ['triangle', 'royal purple']]
		for i, sCtrlName in enumerate(['world', 'layout', 'local']):
			oCtrl = controls.create(sCtrlName, sSide = 'middle', iIndex = None, bSub = False, iStacks = 1, sParent = sParentCtrl, sPos = None, sShape = lCtrlShape[i][0], fSize = fCtrlSize, sColor = lCtrlShape[i][1], lLockHideAttrs = ['sx', 'sy', 'sz', 'v'])
			cmds.addAttr(oCtrl.sName, ln = 'rigScale', at = 'float', dv = 1, keyable = True)
			attributes.connectAttrs(['%s.rigScale' %oCtrl.sName, '%s.rigScale' %oCtrl.sName, '%s.rigScale' %oCtrl.sName,], ['%s.sx' %oCtrl.sName, '%s.sy' %oCtrl.sName, '%s.sz' %oCtrl.sName], bForce = True)
			sParentCtrl = oCtrl.sName
			fCtrlSize *= 0.85

		sCtrlLocal = sParentCtrl

		## connect ctrl with grps
		### geo grp
		for sRes in self.lRes:
			for sPart in ['xtrs', 'def']:
				sGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sRes, sPart = sPart).sName
				lConstraints = constraints.constraint([sCtrlLocal, sGrp], sType = 'all', bForce = True)
				if sPart == 'def':
					for sConstraint in lConstraints:
						sWeightAttr = constraints.getWeightAliasList(sConstraint)[0]
						attributes.connectAttrs(['%s.geoDeformMove' %sMaster], ['%s.%s' %(sConstraint, sWeightAttr)], bForce = True)

		### joints
		lConstraints = constraints.constraint([sCtrlLocal, sJoint], sType = 'all', bForce = True)
		for sConstraint in lConstraints:
			sWeightAttr = constraints.getWeightAliasList(sConstraint)[0]
			attributes.connectAttrs(['%s.geoDeformMove' %sMaster], ['%s.%s' %(sConstraint, sWeightAttr)], bForce = True)

		### rigNodes
		sGrp = naming.oName(sType = 'group', sSide = 'middle', sPart = 'rigNodesTransform').sName
		lConstraints = constraints.constraint([sCtrlLocal, sGrp], sType = 'all', bForce = True)

		### rig geometry
		for sRes in self.lRes:
			sGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sRes, sPart = 'rigGeometryTransform').sName
			lConstraints = constraints.constraint([sCtrlLocal, sGrp], sType = 'all', bForce = True)


	def importBlueprint(self):
		bReturn = rigComponents.importBlueprint(self.dRigData['dBlueprint'], self.sProject, self.sAsset)
		return bReturn

	def importRigGeometry(self):
		bReturn = rigComponents.importRigGeometry(self.dRigData['lRigGeometry'], self.sProject, self.sAsset)
		return bReturn

	def importGeoHierarchy(self):
		bReturn = rigComponents.importGeoHierarchy(self.dRigData['lGeoHierarchy'], self.sProject, self.sAsset)
		return bReturn

	def importDeformer(self):
		bReturn = rigComponents.importDeformer(self.dRigData['lDeformer'], self.sProject, self.sAsset)
		return bReturn

	def importControlShape(self):
		bReturn = rigComponents.importControlShape(self.dRigData['lControlShape'], self.sProject, self.sAsset)
		return bReturn
		