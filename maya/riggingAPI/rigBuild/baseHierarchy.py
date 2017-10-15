## External Import
import maya.cmds as cmds
import maya.mel as mel

## Build Script Import
import baseCore
import common.workspaces as workspaces

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
		dModel = self.rigData['dModel']
		workspaces.loadAsset(dModel['sProject'], dModel['sAsset'], 'model', sLoadType = 'import')
		return True

	def buildBaseRigNodes(self):
		pass

	def importBlueprint(self):
		pass

	def importRigGeometry(self):
		pass

	def importGeoHierarchy(self):
		pass

	def importDeformer(self):
		pass

	def importControlShape(self):
		pass
		