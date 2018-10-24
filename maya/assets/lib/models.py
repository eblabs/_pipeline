# -- import for debug
import logging
debugLevel = logging.INFO # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import os
import os

# -- import time
import time

# -- import lib
import assets
import lib.common.naming.naming as naming
import lib.common.files.files as files
import lib.common.transforms as transforms
# ---- import end ----

# -- global varible
dirname = os.path.abspath(os.path.dirname(__file__))
path_settings = os.path.join(dirname, 'settings.json')
settingsDict = files.readJsonFile(path_settings)

modelSet = settingsDict['folderName']['modelSet']

resolutions = naming.getKeys('resolution', returnType='longName')

# create model set
def createModelSet(asset, project):
	pathAsset = assets.checkAssetExist(asset, project)
	if pathAsset:
		# asset exist, create model set
		pathModelSet = os.path.join(pathAsset, modelSet)
		if not os.path.exists(pathModelSet):
			os.makedirs(pathModelSet)
			# create version folder for model set
			assets.createVersionFolder(pathModelSet)
			# create wip folder for model set
			assets.createWipFolder(pathModelSet)
			# create publish info
			publishInfoFile = '{}.{}'.format(settingsDict['fileName']['publish'],
											 settingsDict['fileType']['publish'])
			pathPublishInfo = os.path.join(pathModelSet, publishInfoFile)
			files.writeJsonFile(pathPublishInfo, {})

			logger.info('Create model set at {}'.format(pathModelSet))
			return pathModelSet
		else:
			logger.warn('Model set already exists, skipped')
			return None
	else:
		logger.warn('Asset "{}" does not exist, skipped'.format(asset))
		return None

# check model set exists
def checkModelSetExist(asset, project):
	pathAsset = assets.checkAssetExist(asset, project)
	if pathAsset:
		pathModelSet = os.path.join(pathAsset, modelSet)
		if os.path.exists(pathModelSet):
			return pathModelSet
		else:
			return None
	else:
		return None

# create resolution groups in scene
def prepareAssetScene(newScene=True):
	if newScene:
		cmds.file(f = True, new = True)

	# create master node
	NamingGrp = naming.Naming(type = 'modelGroup',
							  side = 'middle',
							  part = settingsDict['fileName']['modelSet'])
	modelGrp = NamingGrp.name
	if not cmds.objExists(modelGrp):
		modelGrp = transforms.createTransformNode(modelGrp, 
												  lockHide=['tx', 'ty', 'tz',
															'rx', 'ry', 'rz',
															'sx', 'sy', 'sz', 'v'])

	NamingGrp.type = 'group'
	for res in resolutions:
		NamingGrp.resolution = res
		if not cmds.objExists(NamingGrp.name):
			transforms.createTransformNode(NamingGrp.name, 
										   lockHide=['tx', 'ty', 'tz',
													 'rx', 'ry', 'rz',
													 'sx', 'sy', 'sz', 'v'],
										   parent = modelGrp)

# publish model
def publish(asset, project, comment=''):
	pathModelSet = checkModelSetExist(asset, project)
	if not pathModelSet:
		logger.warn('Model set does not exist, need create first, skipped')
		return False

	modelGrp = naming.Naming(type = 'modelGroup',
							 side = 'middle',
							 part = settingsDict['fileName']['modelSet']).name

	if not cmds.objExists(modelGrp):
		logger.warn('Model group: {} does not exist, can not publish'.format(modelGrp))
		return False

	# clean up resolution
	meshList = cmds.listRelatives(modelGrp, ad = True, type = 'mesh')
	if not meshList:
		# no mesh in model group
		logger.warn('No model found in model group, can not publish')
		return False

	startTime = time.time()

	childGrps = cmds.listRelatives(modelGrp, c = True)
	resList = []
	# each res
	for res in resolutions:
		resGrp = naming.Naming(type = 'group',
							   side = 'middle',
							   resolution = res,
							   part = settingsDict['fileName']['modelSet']).name
		if cmds.objExists(resGrp):
			meshList = cmds.listRelatives(resGrp, ad = True, type = 'mesh')
			parentGrp = cmds.listRelatives(resGrp, p = True)
			if meshList and parentGrp and parentGrp[0] == modelGrp:
				resList.append(res)
				childGrps.remove(resGrp)
			else:
				cmds.delete(resGrp)

	if childGrps:
		cmds.delete(childGrps)
				
	# export file
	modelSetFileType = settingsDict['fileType']['maya']
	modelSetFile = '{}.{}'.format(settingsDict['fileName']['modelSet'],
								  modelSetFileType)
	mayaFileType = settingsDict['mayaFileType'][modelSetFileType]
	pathModelFile = os.path.join(pathModelSet, modelSetFile)
	cmds.select(modelGrp)
	cmds.file(pathModelFile, force = True, type = mayaFileType, exportSelected = True)
	
	# update publish info
	publishInfoFile = '{}.{}'.format(settingsDict['fileName']['publish'],
									 settingsDict['fileType']['publish'])
	pathPublishInfo = os.path.join(pathModelSet, publishInfoFile)
	publishInfo = files.readJsonFile(pathPublishInfo)
	# template
	# {asset:
	#  project:
	#  version:
	#  resolutions:
	#  comment:}
	if publishInfo:
		version = publishInfo['version'] + 1
	else:
		version = 1
	publishInfoDict = {'asset': asset,
					   'project': project,
					   'version': version,
					   'resolutions': resList,
					   'comment': comment}
	# write publish info
	files.writeJsonFile(pathPublishInfo, publishInfoDict)

	# update versions
	pathVersionFolder = os.path.join(pathModelSet, settingsDict['folderName']['version'])
	assets.updateVersion(pathVersionFolder, pathModelFile, modelSetFileType, comment = comment)
	
	endTime = time.time()
	logger.info('Publish {} sucessfully at {}, took {} seconds'.format(modelSet, pathModelFile, endTime - startTime))

# import model
def importModel(asset, project):
	pathModelSet = checkModelSetExist(asset, project)
	modelSetFile = '{}.{}'.format(settingsDict['fileName']['modelSet'],
								  settingsDict['fileType']['maya'])
	pathModelFile = os.path.join(pathModelSet, modelSetFile)
	if os.path.exists(pathModelFile):
		cmds.file(pathModelFile, i = True)
		logger.info('Import Project: "{}", Asset: "{}" {} sucessfully'.format(project, asset, modelSet))
		return True
	else:
		logger.warn('Project: "{}", Asset: "{}" {} does not exist, skipped'.format(project, asset, modelSet))
		return False




	