# -- import for debug
import logging
debugLevel = logging.INFO # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import os
import os

# -- import shutil
from shutil import copyfile, copytree

# -- import datetime
import datetime

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

# list all project
def listAllProject():
	projects = files.getFilesFromPath(path_work, type = 'folder')
	return projects

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

# list all assets
def listAllAsset(project):
	pathProject = checkProjectExist(project)
	if pathProject:
		assets = files.getFilesFromPath(pathProject, type = 'folder')
	else:
		assets = None
	return assets

# create component folder
def createVersionFolder(path):
	for folder in ['publish', 'version', 'wip']:
		pathFolder = os.path.join(path, settingsDict['folderName'][folder])
		os.makedirs(pathFolder)
	# create versionInfo file
	versionInfoFile = '{}.{}'.format(settingsDict['fileName']['version'],
									 settingsDict['fileType']['version'])
	pathVersion = os.path.join(path, settingsDict['folderName']['version'], versionInfoFile)
	files.writeJsonFile(pathVersion, {})
	# create publish file
	publishInfoFile = '{}.{}'.format(settingsDict['fileName']['publish'],
									 settingsDict['fileType']['publish'])
	pathPublishInfo = os.path.join(path, publishInfoFile)
	files.writeJsonFile(pathPublishInfo, {})

# update publish info
def updatePublishInfo(path, comment='', data=None):
	# version template
	# {'version_001': {'comment': 'initial'}}
	# publish template
	# {**data, comment: "", version: 1}

	# assume file already published (different between each component)
	# update publish info
	publishInfoFile = '{}.{}'.format(settingsDict['fileName']['publish'],
									 settingsDict['fileType']['publish'])
	pathPublishInfo = os.path.join(path, publishInfoFile)
	publishInfo = files.readJsonFile(pathPublishInfo)

	# get version
	if publishInfo:
		version = publishInfo['version'] + 1
	else:
		version = 1

	# get current time
	currentTime = datetime.datetime.now()
	publishInfo = {'version': version,
				   'comment': comment,
				   'date': currentTime.strftime("%Y-%m-%d %H:%M")}
	publishInfo.update(data)
	files.writeJsonFile(pathPublishInfo, publishInfo)

	versionLimit = settingsDict['versionLimit']
	versionInfoFile = '{}.{}'.format(settingsDict['fileName']['version'],
									 settingsDict['fileType']['version'])
	pathVersionFolder = os.path.join(path, settingsDict['folderName']['version'])
	pathVersionFile = os.path.join(pathVersionFolder, versionInfoFile)
	versionInfo = files.readJsonFile(pathVersionFile)
	if versionInfo:
		keys = versionInfo.keys()
		keys.sort()
		version = len(keys) + 1
		if version > versionLimit:
			# remove the earliest version
			pathFileRemove = os.path.join(pathVersionFolder, keys[0])
			if os.path.exists(pathFileRemove):
				os.remove(pathFileRemove)
			versionInfo.pop(keys[0])
	else:
		version = 1
	versionInfo.update({'version_{:03d}'.format(version): {'comment': comment}})
	files.writeJsonFile(pathVersionFile, versionInfo)
	versionUpdate = 'version_{:03d}'.format(version)
	pathPublishFolder = os.path.join(path, settingsDict['folderName']['publish'])
	pathVersionUpdate = os.path.join(pathVersionFolder, versionUpdate)
	copytree(pathPublishFolder, pathVersionUpdate)

