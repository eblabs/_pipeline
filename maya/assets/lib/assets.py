# -- import for debug
import logging
debugLevel = logging.INFO # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import os
import os

# -- import shutil
from shutil import copyfile

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import lib.common.files.files as files
# ---- import end ----

# -- global varible
dirname = os.path.abspath(os.path.dirname(__file__))
path_settings = os.path.join(dirname, 'settings.json')
settingsDict = files.readJsonFile(path_settings)

path_work = settingsDict['path']['work']

# create project folder
def createProject(project):
	pathProject = os.path.join(path_work, project)
	if not os.path.exists(pathProject):
		os.makedirs(pathProject)
		logger.info('Create project "{}" at {}'.format(project, pathProject))
		return pathProject
	else:
		logger.warn('Project "{}" already exists, skipped'.format(project))
		return None

# check if project exist
def checkProjectExist(project):
	pathProject = os.path.join(path_work, project)
	if os.path.exists(pathProject):
		return pathProject
	else:
		return None

# create asset folder
def createAsset(asset, project):
	pathProject = checkProjectExist(project)
	if pathProject:
		# project exist, create asset folder
		pathAsset = os.path.join(pathProject, asset)
		if not os.path.exists(pathAsset):
			os.makedirs(pathAsset)
			logger.info('Create asset "{}" at {}'.format(asset, pathAsset))
			return pathAsset
		else:
			logger.warn('Asset "{}" already exists, skipped'.format(asset))
			return None
	else:
		logger.warn('Project "{}" does not exist, skipped'.format(project))
		return None

# check asset exist
def checkAssetExist(asset, project):
	pathAsset = os.path.join(path_work, project, asset)
	if os.path.exists(pathAsset):
		return pathAsset
	else:
		return None

# create version folder
def createVersionFolder(path):
	pathVersion = os.path.join(path, settingsDict['folderName']['version'])
	os.makedirs(pathVersion)
	# create versionInfo file
	versionInfoFile = '{}.{}'.format(settingsDict['fileName']['version'],
									 settingsDict['fileType']['version'])
	pathVersion = os.path.join(pathVersion, versionInfoFile)
	files.writeJsonFile(pathVersion, {})

# update versions
def updateVersion(pathVersionFolder, pathFile, fileType, comment=''):
	# template
	# {'version_001': {'fileType': 'mb', 'comment': 'initial'}}
	versionLimit = settingsDict['versionLimit']
	versionInfoFile = '{}.{}'.format(settingsDict['fileName']['version'],
									 settingsDict['fileType']['version'])
	pathVersionFile = os.path.join(pathVersionFolder, versionInfoFile)
	versionInfo = files.readJsonFile(pathVersionFile)
	if versionInfo:
		keys = versionInfo.keys()
		keys.sort()
		version = len(keys) + 1
		if version > versionLimit:
			# remove the earliest version
			keyRemove = keys[0]
			fileRemove = keyRemove + '.' + versionInfo[keyRemove]['fileType']
			pathFileRemove = os.path.join(pathVersionFolder, fileRemove)
			if os.path.exists(pathFileRemove):
				os.remove(pathFileRemove)
			versionInfo.pop(keyRemove)
	else:
		version = 1
	versionInfo.update({'version_{:03d}'.format(version): {'fileType': fileType,
														   'comment': comment}})
	files.writeJsonFile(pathVersionFile, versionInfo)
	fileUpdate = 'version_{:03d}.{}'.format(version, fileType)
	pathFileUpdate = os.path.join(pathVersionFolder, fileUpdate)
	copyfile(pathFile, pathFileUpdate)

# create wip folder
def createWipFolder(path):
	pathWip = os.path.join(path, settingsDict['folderName']['wip'])
	os.makedirs(pathWip)
