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
			for key, rigFolderInfo in settingsDict['rigSet']['sets'].iteritems():
				pathRigFolder = os.path.join(pathRigSet, rigFolderInfo['name'])
				os.makedirs(pathRigFolder)
				# create version folder for rig
				assets.createVersionFolder(pathRigFolder)

				# create data folders
				dataDict = rigFolderInfo['data']
				dataDict.update(settingsDict['rigSet']['common']['data'])
				for dataKey in dataDict:
					dataFolder = dataDict[dataKey]
					pathData = os.path.join(pathRigFolder, dataFolder)
					os.makedirs(pathData)
					# create version folder for data
					assets.createVersionFolder(pathData)
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

# get data path
def getDataPath(file, data, rigSet, asset, project, mode='publish', version=0):
	pathRig = checkRigSetExist(asset, project)
	if pathRig:
		rigSetFolder = settingsDict['rigSet']['sets'][rigSet]['name']
		pathRigSet = os.path.join(pathRig, rigSetFolder)
		dataFolder = settingsDict['rigSet']['sets'][rigSet]['data'][data]
		pathData = os.path.join(pathRigSet, dataFolder)
		fileFolder = settingsDict['folderName'][mode]
		pathFile = os.path.join(pathData, fileFolder)
		if mode == 'version':
			pathFile = os.path.join(pathFile, 'version_{:03d}'.format(version))
		pathFile = os.path.join(pathFile, file)
		if os.path.exists(pathFile):
			return pathFile
		else:
			logger.info('Can not find file from path: {}, skipped'.format(pathFile))
			return None
	else:
		logger.info('Asset "{}" does not exist, skipped'.format(asset))
		return None