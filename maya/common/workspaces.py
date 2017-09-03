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

def createAsset(sAsset, sProject = None, sType = 'model'):
	if not sProject:
		sDirectory = _getProject()
		if sPathLocal not in sDirectory:
			raise RuntimeError('This project is not set to the proper path, you need to save the project under %s to link to the server' %sPathLocal)
		sProject = _getFoldersFromPath(sDirectory)[-1]
	sAssetDir, sAssetWipDir = _getAssetDirectory(sProject = sProject, sAsset = sAsset, sType = sType)
	_createFolder(sAssetDir)
	_createFolder(sAssetWipDir)
	cmds.workspace(dir = sAssetDir)

	_createVersionFile(sAsset, sType, sProject, sAssetDir)

def saveAsset(sAsset, sType, sProject, sTag = None, sComment = None):
	sStartTime = time.time()

	sDirectory, sWipDirectory = _getAssetDirectory(sProject = sProject, sAsset = sAsset, sType = sType)

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

	sFileName = '%s_%s_%s_v%03d' %(sAsset, sType, sTag, iVersionCurrent)
	dAssetInfo['assetInfo']['sCurrentVersionName'] = sFileName

	cmds.file(rename = os.path.join(sDirectory, '%s%s' %(sFileName, sFileType)))
	cmds.file(save = True, f = True)

	if iVersions >= iBackup:
		iMin = min(lVersions)
		sBackUpName = dVersions[iMin]['sVersionName']
		dVersions.pop(iMin, None)       
		cmds.remove(os.path.join(sWipDirectory, '%s%s' %(sBackUpName, sFileType)))

	dVersionCurrent = {iVersionCurrent: {'sVersionName': sFileName, 'sComment': sComment, 'sFileType': sFileType}}
	dVersions.update(dVersionCurrent)
	files.writeJsonFile(os.path.join(sDirectory, 'assetInfo.version'), dAssetInfo)

	copyfile(os.path.join(sDirectory, '%s%s'%(sFileName, sFileType)), os.path.join(sWipDirectory, '%s%s'%(sFileName, sFileType)))

	lFiles = files.getFilesFromPath(sDirectory, sType = sFileType)
	for sFile in lFiles:
		if sFile != '%s%s'%(sFileName, sFileType):
			os.remove(os.path.join(sDirectory, sFile))

	sEndTime = time.time()

	print 'asset saved at %s, took %f seconds' %(sDirectory, sEndTime - sStartTime)

def openAsset(sProject, sAsset, sType, iVersion = 0):
	sStartTime = time.time()

	sFilePath = _getAssetFile(sProject, sAsset, sType, iVersion = 0)
	if sFilePath:
		setProject(os.path.join(sPathLocal, sProject))
		cmds.file(sFilePath, open = True)     
	else:
		raise RuntimeError('%s did not exist' %sFilePath)

	sEndTime = time.time()

	print 'loaded %s, took %f seconds' %(sFilePath, sEndTime - sStartTime)

def renameProject(sProject, sName):
	sStartTime = time.time()
	# rename version file's sProject
	lVersionFiles = files.getFilesFromDirectoryAndSubDirectories(os.path.join(sPathLocal, sProject), sType = '.version')
	if lVersionFiles:
		for sVersionFile in lVersionFiles:
			dAssetInfo = files.readJsonFile(sVersionFile)
			dAssetInfo['assetInfo']['sProject'] = sName
			files.writeJsonFile(sVersionFile, dAssetInfo)
	# rename project
	os.rename(os.path.join(sPathLocal, sProject), os.path.join(sPathLocal, sName))

	sEndTime = time.time()
	print 'renamed %s to %s, took %f seconds' %(sProject, sName, sEndTime - sStartTime)


def renameAsset(sAsset, sProject, sName):
	sStartTime = time.time()

	sDirectory = _getAssetDirectory(sProject = sProject, sAsset = sAsset)
	lAssetTypes = files.getFilesFromPath(sDirectory, sType = 'folder')
	if lAssetTypes:
		for sAssetType in lAssetTypes:
			sDirectoryAsset = os.path.join(sDirectory, sAssetType)
			if os.path.isfile(os.path.join(sDirectoryAsset, 'assetInfo.version')):
				dAssetInfo = files.readJsonFile(os.path.join(sDirectoryAsset, 'assetInfo.version'))
				# rename version file
				if dAssetInfo['assetInfo']['sCurrentVersionName']:
					dAssetInfo['assetInfo']['sCurrentVersionName'] = dAssetInfo['assetInfo']['sCurrentVersionName'].replace(sAsset, sName)
					dAssetInfo['assetInfo']['sAsset'] = sName

				if dAssetInfo['versionInfo']:
					for iVersion in dAssetInfo['versionInfo'].keys():
						dAssetInfo['versionInfo'][iVersion]['sVersionName'] = dAssetInfo['versionInfo'][iVersion]['sVersionName'].replace(sAsset, sName)
				files.writeJsonFile(os.path.join(sDirectoryAsset, 'assetInfo.version'), dAssetInfo)

				# rename wip files
				sWipDirectory = os.path.join(sDirectoryAsset, 'wipFiles')
				if sWipDirectory:
					lFiles = files.getFilesFromPath(sWipDirectory, sType = sFileType)
					for sFile in lFiles:
						os.rename(os.path.join(sWipDirectory, sFile), os.path.join(sWipDirectory, sFile.replace(sAsset, sName)))
					# rename file
					lFiles = files.getFilesFromPath(sDirectoryAsset, sType = sFileType)
					for sFile in lFiles:
						os.rename(os.path.join(sDirectory, sFile), os.path.join(sDirectory, sFile.replace(sAsset, sName)))
	# rename folder
	sDirectory = _getAssetDirectory(sProject = sProject)
	os.rename(sDirectoryAsset, os.path.join(sDirectory, sName))

	sEndTime = time.time()
	print 'renamed %s to %s, took %f seconds' %(sAsset, sName, sEndTime - sStartTime)




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
	'assetInfo':{'sAsset': sAsset, 'sType': sType, 'sProject': sProject, 'sCurrentVersionName': None, 'sFileType': sFileType},
	'versionInfo':{}
	}

	files.writeJsonFile(os.path.join(sDirectory, 'assetInfo.version'), dAssetInfo)

def _getAssetDirectory(sProject = None, sAsset = None, sType = None):
	sDirectory = sPathLocal
	if sProject:
		for sFolder in [sProject, 'assets', sAsset, sType]:
			if sFolder:
				sDirectory = os.path.join(sDirectory, sFolder)
	if sProject and sAsset and sType:
		sWipDirectory = os.path.join(sDirectory, 'wipFiles')
	else:
		sWipDirectory = None
	return sDirectory, sWipDirectory

def _getAssetFile(sProject, sAsset, sType, iVersion = 0):
	sDirectory, sWipDirectory = _getAssetDirectory(sProject = sProject, sAsset = sAsset, sType = sType)
	if not os.path.isfile(os.path.join(sDirectory, 'assetInfo.version')):
		raise RuntimeError('assetInfo.version does not exist in %s, can not read the asset' %(sAsset, os.path.abspath(sDirectory)))
	dAssetInfo = files.readJsonFile(os.path.join(sDirectory, 'assetInfo.version'))
	if iVersion == 0:
		sFileName = '%s%s' %(dAssetInfo['assetInfo']['sCurrentVersionName'], dAssetInfo['assetInfo']['sFileType'])
	else:
		sFileName = '%s%s' %(dAssetInfo['versionInfo'][iVersion]['sVersionName'], dAssetInfo['assetInfo']['sFileType'])
		sDirectory = sWipDirectory
	if os.path.isfile(os.path.join(sDirectory, sFileName)):
		sFilePath = os.path.join(sDirectory, sFileName)
		#setProject(os.path.join(sPathLocal, sProject))
		#cmds.file(os.path.join(sDirectory, sFileName), open = True)     
	else:
		sFilePath = None
	return sFilePath
