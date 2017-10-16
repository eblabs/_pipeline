## External Import
import maya.cmds as cmds
import maya.mel as mel

## Build Script Import
import baseCore
import common.workspaces as workspaces
import common.attributes as attributes
import namingAPI.namingDict as namingDict
import namingAPI.naming as naming
import riggingAPI.rigComponents as rigComponents

## baseHierarchy build script
class baseHierarchy(baseCore.baseCore):
	"""docstring for baseHierarchy"""
	def __init__(self):
		super(baseHierarchy, self).__init__()

		self.generateRigData()

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
								'mFunction': self.createNewScene,
								'sName': 'Create New Scene',
								'sSection': 'Pre Build',
								)

		self.registerFunction(
								'mFunction': self.importModel,
								'sName': 'Import Model',
								'sSection': 'Pre Build',
								)

		self.registerFunction(
								'mFunction': self.buildBaseRigNodes,
								'sName': 'Build Base Rig Nodes',
								'sSection': 'Pre Build',
								)

		self.registerFunction(
								'mFunction': self.importBlueprint,
								'sName': 'Import Blueprint',
								'sSection': 'Pre Build',
								)

		self.registerFunction(
								'mFunction': self.importRigGeometry,
								'sName': 'Import Rig Geometry',
								'sSection': 'Pre Build',
								)

		# Build

		# Post Build
		self.registerFunction(
								'mFunction': self.importGeoHierarchy,
								'sName': 'Import Geo Hierarchy',
								'sSection': 'Post Build',
								)

		self.registerFunction(
								'mFunction': self.importDeformer,
								'sName': 'Import Deformer',
								'sSection': 'Post Build',
								)

		self.registerFunction(
								'mFunction': self.importControlShape,
								'sName': 'Import Control Shape',
								'sSection': 'Post Build'
								)
		
	def createNewScene(self):
		workspaces.createNewScene()
		return True

	def importModel(self):
		bReturn = rigComponents.importModel(self.dRigData['dModel'], self.sProject, self.sAsset)
		return bReturn

	def buildBaseRigNodes(self):
		## create master node
		sMaster = transforms.createTransformNode('master', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
		####### add attrs
		lResKeys = ['high', 'middle', 'low', 'proxy', 'simulation']
		sEnumName = ''
		for sResKey in lResKeys:
			sEnumName += '%s:' %namingDict.dNameConvension['resolution'][sResKey]
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

		cmds.addAttr(sMaster, ln = 'skelOrigin', at = 'long', min = 0, max = 1, dv =1, keyable = False)
		cmds.setAttr('%s.skelOrigin' %sMaster, channelBox = True)

		## create control, do not touch group
		sControl = transforms.createTransformNode('controls', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sMaster)
		sDoNotTouch = transforms.createTransformNode('doNotTouch', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sMaster)	

		## create geometry groups
		sGeometry = transforms.createTransformNode('geometry', lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sDoNotTouch)
		for sResKey in lResKeys:
			sResGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sResKey, sPart = 'geo').sName
			sResGrp = transforms.createTransformNode(sResGrp, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sGeometry)
			for sPart in ['xtrs', 'def']:
				sGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sResKey, sPart = sPart).sName
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
		for sResKey in lResKeys:
			sResGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sResKey, sPart = 'rigGeometry').sName
			sResGrp = transforms.createTransformNode(sResGrp, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sRigGeometry)
			for sPart in ['transform', 'origin']:
				sGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sResKey, sPart = 'rigGeometry%s' %sPart.title()).sName
				sGrp = transforms.createTransformNode(sGrp, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sResGrp)


		## Vis connections
		### resolution
		lAttr = []
		for sResKey in lResKeys:
			sResGeoGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sResKey, sPart = 'geo').sName
			sResRigGeoGrp = naming.oName(sType = 'group', sSide = 'middle', sRes = sResKey, sPart = 'rigGeometry').sName
			lAttr.append('%s.v' %sResGeoGrp)
			attributes.connectAttrs(['%s.v' %sResGeoGrp], ['%s.v' %sResRigGeoGrp], bForce = True)
		attributes.enumToMultiAttrs('resolution', lAttr, iEnumRange = len(lResKeys), lValRange = [[0,1]], sEnumObj = sMaster)

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
		