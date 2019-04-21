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

rigGrp = settingsDict['folderName']['rigGroup']

# create rig set
def createRigGroup(project, asset):
	pathAsset = assets.checkAssetExist(asset, project)
	if pathAsset:
		# asset exist, create rig set
		pathRigGrp = os.path.join(pathAsset, rigGrp)
		if not os.path.exists(pathRigGrp):
			os.makedirs(pathRigGrp)

			# create animation rig (one rig group must include animation rig)
			pathAnimationRig = os.path.join(pathRigGrp, 
							settingsDict['rigGroup']['rigs']['animationRig']['name'])
			os.makedirs(pathAnimationRig)
			# create version folder for rig
			assets.createVersionFolder(pathAnimationRig)

			# create data folders
			pathAnimationRigData = os.path.join(pathAnimationRig, 
									settingsDict['folderName']['rigData'])
			os.makedirs(pathAnimationRigData)
			dataDict = settingsDict['rigGroup']['rigs']['animationRig']['data']
			dataDict.update(settingsDict['rigGroup']['common']['data'])
			for dataKey in dataDict:
				dataFolder = dataDict[dataKey]
				pathData = os.path.join(pathAnimationRigData, dataFolder)
				os.makedirs(pathData)
				# create version folder for data
				assets.createVersionFolder(pathData)

			logger.info('Create rig group at {}'.format(pathRigGrp))
			return pathRigGrp
		else:
			logger.warn('Rig group already exists, skipped')
			return None
	else:
		logger.warn('Asset "{}" does not exist, skipped'.format(asset))
		return None

# check rig group exists
def checkRigGroupExist(project, asset, rig=None):
	pathAsset = assets.checkAssetExist(asset, project)
	if pathAsset:
		pathRigGrp = os.path.join(pathAsset, rigGrp)
		if rig:
			pathRigGrp = os.path.join(pathRigGrp, rig)
		if os.path.exists(pathRigGrp):
			return pathRigGrp
		else:
			return None
	else:
		return None

# create rig
def createRig(project, asset, rig, rigType='animationRig'):
	pathRigGrp = checkRigGroupExist(project, asset, rig=None)
	if pathRigGrp:
		pathRig = os.path.join(pathRigGrp, rig)
		if not os.path.exists(pathRig):
			# create rig folder
			os.makedirs(pathRig)

			# create rig info dict
			rigInfoDict = {'name': rig,
						   'type': rigType,
						   'data': []}

			# create version folder for rig
			assets.createVersionFolder(pathRig)
			# create data folder
			pathRigData = os.path.join(pathRig, 
									settingsDict['folderName']['rigData'])
			os.makedirs(pathRigData)
			dataList = settingsDict['rigData'][rigType]
			dataList += settingsDict['rigData']['common']

			rigInfoDict.update({'data': dataList})

			for data in dataList:
				pathData = os.path.join(pathRigData, data)
				os.makedirs(pathData)
				assets.createVersionFolder(pathData)

			rigInfoFile = '{}.{}'.format(settingsDict['fileName']['rigInfo'],
										 settingsDict['fileType']['rigInfo'])

			pathRigInfo = os.path.join(pathRig, rigInfoFile)
			files.writeJsonFile(pathRigInfo, rigInfoDict)
			logger.info('Create {} at {}'.format(rig, pathRig))
		else:
			logger.info('{} already exists, skipped'.format(rig))
	else:
		logger.info('Rig Group does not exist, skipped')

# get rigs
def getRigs(project, asset):
	pathRigGrp = checkRigGroupExist(asset, project)
	if pathRigGrp:
		rigs = files.getFilesFromPath(pathRigGrp, type = 'folder')
		return rigs
	else:
		logger.warn('No rig group found at {}, skipped'.format(pathRigGrp))
		return None

# get rig info
def getRigInfo(project, asset, rig):
	pathRig = checkRigGroupExist(project, asset, rig=rig)
	if pathRig:
		rigInfoFile = '{}.{}'.format(settingsDict['fileName']['rigInfo'],
									 settingsDict['fileType']['rigInfo'])
		rigInfoDict = files.readJsonFile(rigInfoFile)
		return rigInfoDict
	else:
		logger.warn('{} does not exist, skipped'.format(rig))
		return None

# list rig types
def listRigTypes():
	rigTypes = settingsDict['rigType']
	return rigTypes

# get data folder path
def getDataFolderPath(project, asset, rig, data, mode='publish', version=0):
	pathRig = checkRigGroupExist(project, asset, rig=rig)
	if pathRig:
		rigDataFolder = settingsDict['folderName']['rigData']
		pathRigData = os.path.join(pathRig, rigDataFolder, data)
		if os.path.exists(pathRigData):
			fileFolder = settingsDict['folderName'][mode]
			pathFile = os.path.join(pathRigData, fileFolder)
			if mode == 'version' and version >= 0:
				pathFile = os.path.join(pathFile, 'version_{:03d}'.format(version))
			return pathFile
		else:
			logger.info('{} does not have {}, skipped'.format(rig, data))
			return None
	else:
		logger.info('Asset "{}" does not exist, skipped'.format(asset))
		return None

# get data path
def getDataPath(project, asset, rig, data, files=[], fileType=[], mode='publish', version=0):
	pathFilesReturn = []
	pathFile = getDataFolderPath(project, asset, rig, data, mode = mode, version = version)
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
		return None