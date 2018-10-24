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

rigSet = settingsDict['folderName']['rigSet']

# create rig set
def createRigSet(asset, project):
	pathAsset = assets.checkAssetExist(asset, project)
	if pathAsset:
		# asset exist, create rig set
		pathRigSet = os.path.join(pathAsset, rigSet)
		if not os.path.exists(pathRigSet):
			os.makedirs(pathRigSet)
			# create animation rig and deformation rig folder
			for key, rigFolderInfo in settingsDict['rigSet'].iteritems():
				pathRigFolder = os.path.join(pathRigSet, rigFolderInfo['name'])
				os.makedirs(pathRigFolder)
				# create version folder for rig
				assets.createVersionFolder(pathRigFolder)
				# create wip folder for rig
				assets.createWipFolder(pathRigFolder)
				# create publish info
				publishInfoFile = '{}.{}'.format(settingsDict['fileName']['publish'],
												 settingsDict['fileType']['publish'])
				pathPublishInfo = os.path.join(pathRigFolder, publishInfoFile)
				files.writeJsonFile(pathPublishInfo, {})

				# create data folders
				for dataKey in rigFolderInfo['data']:
					data = rigFolderInfo['data']['dataKey']
					pathData = os.path.join(pathRigFolder, data)
					os.makedirs(pathData)
					# create version folder for data
					assets.createVersionFolder(pathData)
					# create publish info
					publishInfoFile = '{}.{}'.format(settingsDict['fileName']['publish'],
												 settingsDict['fileType']['publish'])
					pathPublishInfo = os.path.join(pathData, publishInfoFile)
					files.writeJsonFile(pathPublishInfo, {})

			logger.info('Create rig set at {}'.format(pathRigSet))
			return pathRigSet
		else:
			logger.warn('Rig set already exists, skipped')
			return None
	else:
		logger.warn('Asset "{}" does not exist, skipped'.format(asset))
		return None

# check rig set exists
def checkRigSetExist(asset, project):
	pathAsset = assets.checkAssetExist(asset, project)
	if pathAsset:
		pathModelSet = os.path.join(pathAsset, rigSet)
		if os.path.exists(pathRigSet):
			return pathRigSet
		else:
			return None
	else:
		return None