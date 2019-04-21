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

# -- import shutil
from shutil import copyfile

# -- import lib
import assets
reload(assets)
import lib.common.naming.naming as naming
import lib.common.files.files as files
import lib.common.transforms as transforms
# ---- import end ----

# -- global varible
dirname = os.path.abspath(os.path.dirname(__file__))
path_settings = os.path.join(dirname, 'settings.json')
settingsDict = files.readJsonFile(path_settings)

modelGrp = settingsDict['folderName']['modelGroup']

resolutions = naming.getKeys('resolution', returnType='longName')

# create model set
def createModelGroup(asset, project):
	pathAsset = assets.checkAssetExist(asset, project)
	if pathAsset:
		# asset exist, create model set
		pathModelGrp = os.path.join(pathAsset, modelGrp)
		if not os.path.exists(pathModelGrp):
			os.makedirs(pathModelGrp)
			# create publish info and version folders
			assets.createVersionFolder(pathModelGrp)
			logger.info('Create model group at {}'.format(pathModelGrp))
			return pathModelGrp
		else:
			logger.warn('Model group already exists, skipped')
			return None
	else:
		logger.warn('Asset "{}" does not exist, skipped'.format(asset))
		return None

# check model group exists
def checkModelGroupExist(asset, project):
	pathAsset = assets.checkAssetExist(asset, project)
	if pathAsset:
		pathModelGrp = os.path.join(pathAsset, modelGrp)
		if os.path.exists(pathModelGrp):
			return pathModelGrp
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
							  part = settingsDict['fileName']['modelGroup'])
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