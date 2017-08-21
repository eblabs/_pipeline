## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
from shutil import copyfile
## libs Import
import files

## Vars
import getpass
sUser = getpass.getuser()
sPathServer = 'C:/Users/%s/Dropbox/_works/' %sUser
sPathLocal = 'C:/_works/maya/'

iBackup = 20
sFileType = 'mb'

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

def createAsset(sName, sType = 'model'):
	sDirectory = _getProject()
	if sPathLocal not in sDirectory:
		raise RuntimeError('This project is not set to the proper path, you need to save the project under %s to link to the server' %sPathLocal)
	sAssetDir = os.path.join(sDirectory, 'assets')
	sAssetDir = os.path.join(sAssetDir, sName)
	sAssetDir = os.path.join(sAssetDir, sType)
	sAssetWipDir = os.path.join(sAssetDir, 'wipFiles')
	_createFolder(sAssetDir)
	_createFolder(sAssetWipDir)
	cmds.workspace(dir = sAssetDir)

	dAssetInfo = {
	'assetInfo':{'sName': sName, 'sType': sType},
	'versionInfo':{}
	}

	files.writeJsonFile(os.path.join(sAssetDir, 'assetInfo.version'), dAssetInfo)

def saveAsset(sTag = None, sComment = None):
	sDirectory = _getProject(rootDirectory = False)
	sWipDirectory = os.path.join(sDirectory, 'wipFiles')
	dAssetInfo = files.readJsonFile(os.path.join(sDirectory, 'assetInfo.version'))

	sName = dAssetInfo['assetInfo']['sName']
	sType = dAssetInfo['assetInfo']['sType']
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
		sTag = 'update'

	if not sComment:
		sComment = 'update'
	iVersionCurrent = iVersions + 1

	sFileName = '%s_%s_%s_v%03d.%s' %(sName, sType, sTag, iVersionCurrent, sFileType)

	cmds.file(rename = os.path.join(sDirectory, sFileName))
	cmds.file(save = True, f = True)

	if iVersions >= iBackup:
		iMin = min(lVersions)
		sBackUpName = dVersions[iMin]['sAssetName']
		dVersions.pop(iMin, None)		
		cmds.remove(os.path.join(sWipDirectory, sBackUpName))

	dVersionCurrent = {iVersionCurrent: {'sAssetName': sFileName, 'sComment': sComment}}
	dVersions.update(dVersionCurrent)
	files.writeJsonFile(os.path.join(sDirectory, 'assetInfo.version'), dAssetInfo)

	copyfile(os.path.join(sDirectory, sFileName), os.path.join(sWipDirectory, sFileName))

	lFiles = os.listdir(sDirectory)
	for sFile in lFiles:
		if '.mb' in sFile and sFile != sFileName:
			os.remove(os.path.join(sDirectory, sFile))





#### sub functions
def _createFolder(sDirectory):
	if not os.path.exists(sDirectory):
		os.makedirs(sDirectory)

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
	lFolders = sPathDir.split('/')
	return lFolders