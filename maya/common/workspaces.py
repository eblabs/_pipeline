## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
from shutil import copyfile
import time
## libs Import
import files

## Vars
import getpass
sUser = getpass.getuser()
sPathServer = 'C:/Users/%s/Dropbox/_works/' %sUser
sPathLocal = 'C:/_works/maya/'

iBackup = 20
sFileType = '.mb'

#### Functions
def createProject(sName):
	sDirectory = os.path.join(sPathLocal, sName)
	_createFolder(sDirectory)
	setProject(sDirectory)
	_createProjectFiles(sDirectory)
	return sDirectory

def setProject(sDirectory):
	mel.eval('setProject \"' + sDirectory + '\"')
	cmds.workspace(sDirectory, openWorkspace=True)

def createAsset(sAsset, sType = 'model'):
	sDirectory = _getProject()
	if sPathLocal not in sDirectory:
		raise RuntimeError('This project is not set to the proper path, you need to save the project under %s to link to the server' %sPathLocal)
	sProject = _getFoldersFromPath(sDirectory)[-1]
	sAssetDir = os.path.join(sDirectory, 'assets')
	sAssetDir = os.path.join(sAssetDir, sAsset)
	sAssetDir = os.path.join(sAssetDir, sType)
	sAssetWipDir = os.path.join(sAssetDir, 'wipFiles')
	_createFolder(sAssetDir)
	_createFolder(sAssetWipDir)
	cmds.workspace(dir = sAssetDir)

	_createVersionFile(sAsset, sType, sProject, sAssetDir)

def saveAsset(sAsset, sType, sProject, sTag = None, sComment = None):
	sStartTime = time.time()

	sDirectory, sWipDirectory = _getAssetDirectory(sAsset, sType, sProject)

	# check if wip folder exists, create folder if not exists
	_createFolder(sWipDirectory)

	# check if versionInfo file exists, create one if not
	if not os.path.isfile(os.path.join(sDirectory, 'assetInfo.version')):
		_createVersionFile(sAsset, sType, sProject, sDirectory)
		cmds.warning('assetInfo.version did not exist, created the file')

	dAssetInfo = files.readJsonFile(os.path.join(sDirectory, 'assetInfo.version'))

	dVersions = dAssetInfo['versionInfo']
	if dVersions:
		lVersions = dVersions.keys()
		iVersions = len(lVersions)
	else:
		lVersions = None
		iVersions = 0

	if sTag != None:
		sTag = files._convertStringToCamelcase(sTag)
	else:
		sTag = 'initial'

	if not sComment:
		sComment = 'initial'
	iVersionCurrent = iVersions + 1

	sFileName = '%s_%s_%s_v%03d%s' %(sAsset, sType, sTag, iVersionCurrent, sFileType)

	cmds.file(rename = os.path.join(sDirectory, sFileName))
	cmds.file(save = True, f = True)

	if iVersions >= iBackup:
		iMin = min(lVersions)
		sBackUpName = dVersions[iMin]['sVersionName']
		dVersions.pop(iMin, None)		
		cmds.remove(os.path.join(sWipDirectory, sBackUpName))

	dVersionCurrent = {iVersionCurrent: {'sVersionName': sFileName, 'sComment': sComment}}
	dVersions.update(dVersionCurrent)
	files.writeJsonFile(os.path.join(sDirectory, 'assetInfo.version'), dAssetInfo)

	copyfile(os.path.join(sDirectory, sFileName), os.path.join(sWipDirectory, sFileName))

	lFiles = os.listdir(sDirectory)
	for sFile in lFiles:
		if sFileType in sFile and sFile != sFileName:
			os.remove(os.path.join(sDirectory, sFile))

	sEndTime = time.time()

	print 'asset saved at %s, took %f seconds' %(sDirectory, sEndTime - sStartTime)

def openAsset(sAsset, sType, sProject, iVersion = 0):
	sStartTime = time.time()

	sDirectory, sWipDirectory = _getAssetDirectory(sAsset, sType, sProject)
	if not os.path.isfile(os.path.join(sDirectory, 'assetInfo.version')):
		raise RuntimeError('assetInfo.version does not exist in %s, can not read the asset' %(sAsset, os.path.abspath(sDirectory)))
	dAssetInfo = files.readJsonFile(os.path.join(sDirectory, 'assetInfo.version'))
	if iVersion == 0:
		sFileName = dAssetInfo['assetInfo']['sCurrentVersionName']
	else:
		sFileName = dAssetInfo['versionInfo'][iVersion]['sVersionName']
		sDirectory = sWipDirectory
	if os.path.isfile(os.path.join(sDirectory, sFileName)):
		setProject(os.path.join(sPathLocal, sProject))
		cmds.file(os.path.join(sDirectory, sFileName), open = True)		
	else:
		raise RuntimeError('%s did not exist in %s' %(sFileName, sDirectory))

	sEndTime = time.time()

	print 'loaded %s from %s, took %f seconds' %(sFileName, sDirectory, sEndTime - sStartTime)





#### sub functions
def _createFolder(sDirectory):
	if not os.path.exists(sDirectory):
		os.makedirs(sDirectory)
		cmds.warning('%s did not exist, created the folders' %sDirectory)

def _createProjectFiles(sProjectDir):
	lFiles = cmds.workspace(q = True, fileRuleList = True)
	for sFile in lFiles:
		sFileDir= cmds.workspace(fileRuleEntry = sFile)
		sFileDir = os.path.join(sProjectDir, sFileDir)
		_createFolder(sFileDir)

def _getProject(rootDirectory = True):
	sDirectory = cmds.workspace(q=True, directory=True, rd = rootDirectory)
	return sDirectory

def _getFoldersFromPath(sPath):
	sPathDir = os.path.dirname(sPath)
	sPathDir = os.path.abspath(sPathDir)
	lFolders = sPathDir.split('\\')
	return lFolders

def _createVersionFile(sAsset, sType, sProject, sDirectory):
	dAssetInfo = {
	'assetInfo':{'sAsset': sAsset, 'sType': sType, 'sProject': sProject, 'sCurrentVersionName': None},
	'versionInfo':{}
	}

	files.writeJsonFile(os.path.join(sDirectory, 'assetInfo.version'), dAssetInfo)

def _getAssetDirectory(sAsset, sType, sProject):
	sDirectory = sPathLocal
	for sFolder in [sProject, 'assets', sAsset, sType]:
		sDirectory = os.path.join(sDirectory, sFolder)
	sWipDirectory = os.path.join(sDirectory, 'wipFiles')
	return sDirectory, sWipDirectory