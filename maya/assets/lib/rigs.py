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

# -- import glob
import glob

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
				pathRigDataFolder = os.path.join(pathRigFolder, settingsDict['folderName']['rigData'])
				os.makedirs(pathRigDataFolder)
				dataDict = rigFolderInfo['data']
				dataDict.update(settingsDict['rigSet']['common']['data'])
				for dataKey in dataDict:
					dataFolder = dataDict[dataKey]
					pathData = os.path.join(pathRigDataFolder, dataFolder)
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
def checkRigSetExist(asset, project, rig=None):
	pathAsset = assets.checkAssetExist(asset, project)
	if pathAsset:
		pathRigSet = os.path.join(pathAsset, rigSet)
		if rig:
			rig = settingsDict['rigSet']['sets'][rig]['name']
			pathRigSet = os.path.join(pathRigSet, rig)
		if os.path.exists(pathRigSet):
			return pathRigSet
		else:
			return None
	else:
		return None

# get rigs
def getRigs(asset, project):
	pathRigSet = checkRigSetExist(asset, project)
	if pathRigSet:
		rigs = files.getFilesFromPath(pathRigSet, type = 'folder')
		return rigs
	else:
		logger.warn('No rigSet found at {}, skipped'.format(pathRigSet))
		return None

# get data folder path
def getDataFolderPath(data, rig, asset, project, mode='publish', version=0):
	pathRig = checkRigSetExist(asset, project, rig = rig)
	if pathRig:
		rigDataFolder = settingsDict['folderName']['rigData']
		pathRigData = os.path.join(pathRig, rigDataFolder)
		if data in settingsDict['rigSet']['common']['data']:
			dataFolder = settingsDict['rigSet']['common']['data'][data]
		else:
			dataFolder = settingsDict['rigSet']['sets'][rig]['data'][data]
		pathData = os.path.join(pathRigData, dataFolder)
		fileFolder = settingsDict['folderName'][mode]
		pathFile = os.path.join(pathData, fileFolder)
		if mode == 'version' and version >= 0:
			pathFile = os.path.join(pathFile, 'version_{:03d}'.format(version))
		return pathFile
	else:
		logger.info('Asset "{}" does not exist, skipped'.format(asset))
		return None

# get data path
def getDataPath(data, rig, asset, project, files=[], fileType=[], mode='publish', version=0):
	pathFilesReturn = []
	pathFile = getDataFolderPath(data, rig, asset, project, mode = mode, version = version)
	if pathFile:		
		if files:
			for f in files:
				pathFileEach = os.path.join(pathFile, f)
				if os.path.exists(pathFileEach):
					pathFilesReturn.append(pathFileEach)
				else:
					logger.info('Can not find file from path: {}, skipped'.format(pathFileEach))
		else:
			# go over each file in the folder
			if fileType:
				for t in fileType:
					pathFileSearch = os.path.join(pathFile, '*.' + t)
					files = glob.glob(pathFileSearch)
					pathFilesReturn += files
			else:
				pathFileSearch = os.path.join(pathFile, '*.*')
				files = glob.glob(pathFileSearch)
				pathFilesReturn += files
		
		if pathFilesReturn:
			return pathFilesReturn
		else:
			logger.info('Can not find file from path: {}, skipped'.format(pathFile))
			return None
	else:
		logger.info('Asset "{}" does not exist, skipped'.format(asset))
		return None