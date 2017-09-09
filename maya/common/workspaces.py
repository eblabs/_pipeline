## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
from shutil import copyfile, rmtree, copytree
import time
## libs Import
import files
reload(files)

## Vars
sPathServer = files.sPathServer
sPathLocal = files.sPathLocal

iBackup = files.iBackup
sFileType = files.sFileType
sFolderListName = files.sFolderListName

#### Functions
def createProject(sName):
	## create/write folder list
	sFolderListPath = os.path.join(sPathLocal, sFolderListName)
	if not os.path.exists(sFolderListPath):
		_createFolderListFile(sPathLocal)
	_writeFolderListFile(sPathLocal, sName)

	## create project
	sDirectory = os.path.join(sPathLocal, sName)
	files.createFolder(sDirectory)
	# create folder list
	_createFolderListFile(sDirectory)
	for sFolder in files.lProjectFolders:
		files.createFolder(os.path.join(sDirectory, sFolder))
		_writeFolderListFile(sDirectory, sFolder)
	setProject(sDirectory)
	return sDirectory

def setProject(sDirectory):
	cmds.workspace(dir = sDirectory)

def createAsset(sAsset, sProject = None):
	if not sProject:
		sDirectory = _getProject()
		sDirectory = os.path.abspath(sDirectory)
		if sPathLocal not in sDirectory:
			raise RuntimeError('This project is not set to the proper path, you need to save the project under %s to link to the server' %sPathLocal)
		sProject = files._getFoldersThroughPath(sDirectory)[-1]

	## create/write folder list
	sAssetDir, sAssetWipDir = _getAssetDirectory(sProject = sProject)
	sFolderListPath = os.path.join(sAssetDir, sFolderListName)
	if not os.path.exists(sFolderListPath):
		_createFolderListFile(sAssetDir)
	_writeFolderListFile(sAssetDir, sAsset)

	## create asset folder
	sAssetDir, sAssetWipDir = _getAssetDirectory(sProject = sProject, sAsset = sAsset)
	files.createFolder(sAssetDir)
	setProject(sAssetDir)

def createAssetType(sAsset, sProject = None, sType = 'model'):
	if not sProject:
		sDirectory = _getProject()
		sDirectory = os.path.abspath(sDirectory)
		if sPathLocal not in sDirectory:
			raise RuntimeError('This project is not set to the proper path, you need to save the project under %s to link to the server' %sPathLocal)
		sProject = files._getFoldersThroughPath(sDirectory)[-1]

	## create/write file list
	sAssetDir, sAssetWipDir = _getAssetDirectory(sProject = sProject, sAsset = sAsset)
	sFolderListPath = os.path.join(sAssetDir, sFolderListName)
	if not os.path.exists(sFolderListPath):
		_createFolderListFile(sAssetDir)
	_writeFolderListFile(sAssetDir, sType)

	#Create Type
	sAssetDir, sAssetWipDir = _getAssetDirectory(sProject = sProject, sAsset = sAsset, sType = sType)
	files.createFolder(sAssetDir)
	files.createFolder(sAssetWipDir)
	setProject(sAssetDir)

	_createVersionFile(sAsset, sType, sProject, sAssetDir)

def saveAsset(sAsset, sType, sProject, sTag = None, sComment = None):
	fStartTime = time.time()

	sDirectory, sWipDirectory = _getAssetDirectory(sProject = sProject, sAsset = sAsset, sType = sType)

	# check if wip folder exists, create folder if not exists
	files.createFolder(sWipDirectory)

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

	sFileDelete = '%s%s' %(dAssetInfo['assetInfo']['sCurrentVersionName'], dAssetInfo['assetInfo']['sFileType'])

	sFileName = '%s_%s_%s_v%03d' %(sAsset, sType, sTag, iVersionCurrent)
	dAssetInfo['assetInfo']['sCurrentVersionName'] = sFileName

	cmds.file(rename = os.path.join(sDirectory, '%s%s' %(sFileName, sFileType)))
	cmds.file(save = True, f = True)

	if iVersions >= iBackup:
		iMin = min(lVersions)
		sBackUpName = dVersions[iMin]['sVersionName']
		dVersions.pop(iMin, None)       
		os.remove(os.path.join(sWipDirectory, '%s%s' %(sBackUpName, sFileType)))

	dVersionCurrent = {iVersionCurrent: {'sVersionName': sFileName, 'sComment': sComment, 'sFileType': sFileType}}
	dVersions.update(dVersionCurrent)
	files.writeJsonFile(os.path.join(sDirectory, 'assetInfo.version'), dAssetInfo)

	copyfile(os.path.join(sDirectory, '%s%s'%(sFileName, sFileType)), os.path.join(sWipDirectory, '%s%s'%(sFileName, sFileType)))

	os.remove(os.path.join(sDirectory, sFileDelete))

	setProject(sDirectory)

	fEndTime = time.time()

	print 'asset saved at %s, took %f seconds' %(sDirectory, fEndTime - fStartTime)

def loadAsset(sProject, sAsset, sType, iVersion = 0, sLoadType = 'open', sNamespace = None):
	fStartTime = time.time()

	sFilePath = _getAssetFile(sProject, sAsset, sType, iVersion = iVersion)
	sProjectPath = os.path.abspath(sFilePath)
	sProjectPath = os.path.dirname(sProjectPath)
	if sFilePath:
		setProject(sProjectPath)
		if sLoadType == 'open':
			cmds.file(new = True, force = True ) 
			cmds.file(sFilePath, open = True)
		elif sLoadType == 'import':
			if sNamespace == None:
				cmds.file(sFilePath, i = True)
			else:
				cmds.file(sFilePath, i = True, namespace = sNamespace)
		else:
			if sNamespace == None:
				sNamespace = ''
			cmds.file(sFilePath, r = True, namespace = sNamespace)    
	else:
		raise RuntimeError('%s did not exist' %sFilePath)

	fEndTime = time.time()

	print 'loaded %s, took %f seconds' %(sFilePath, fEndTime - fStartTime)

def renameProject(sProject, sName):
	fStartTime = time.time()
	# rename version file's sProject
	lVersionFiles = _getVersionFiles(sProject)
	if lVersionFiles:
		for sVersionFile in lVersionFiles:
			dAssetInfo = files.readJsonFile(sVersionFile)
			dAssetInfo['assetInfo']['sProject'] = sName
			files.writeJsonFile(sVersionFile, dAssetInfo)
	# rename project
	os.rename(os.path.join(sPathLocal, sProject), os.path.join(sPathLocal, sName))

	# write file list
	_writeFolderListFile(sPathLocal, sName, sReplace = sProject)

	fEndTime = time.time()
	print 'renamed %s to %s, took %f seconds' %(sProject, sName, fEndTime - fStartTime)


def renameAsset(sProject, sAsset, sName):
	fStartTime = time.time()

	#rename asset
	sDirectory, sWipDirectory = _getAssetDirectory(sProject = sProject, sAsset = sAsset)
	lAssetTypes = _getFoldersFromFolderList(sDirectory)
	lVersionFiles = _getVersionFiles(sProject, sAsset = sAsset)
	for sVersionFile in lVersionFiles:
		sDirectoryAsset = os.path.dirname(sVersionFile)
		sWipDirectoryAsset = os.path.join(sDirectoryAsset, 'wipFiles')

		dAssetInfo = files.readJsonFile(sVersionFile)
		sCurrentVersion = None
		lVersions = []
		if dAssetInfo['assetInfo']['sCurrentVersionName']:
			sCurrentVersion = dAssetInfo['assetInfo']['sCurrentVersionName']
			dAssetInfo['assetInfo']['sCurrentVersionName'] = dAssetInfo['assetInfo']['sCurrentVersionName'].replace(sAsset, sName)
			
		dAssetInfo['assetInfo']['sAsset'] = sName
		if dAssetInfo['versionInfo']:
			for iVersion in dAssetInfo['versionInfo'].keys():
				dAssetInfo['versionInfo'][iVersion]['sVersionName'] = dAssetInfo['versionInfo'][iVersion]['sVersionName'].replace(sAsset, sName)
				lVersions.append(dAssetInfo['versionInfo'][iVersion]['sVersionName'])
		files.writeJsonFile(sVersionFile, dAssetInfo)

		for sVersion in lVersions:
			os.rename(os.path.join(sWipDirectoryAsset, sVersion), os.path.join(sWipDirectoryAsset, sVersion.replace(sAsset, sName)))
		if sCurrentVersion:
			os.rename(os.path.join(sDirectoryAsset, sCurrentVersion), os.path.join(sDirectoryAsset, sCurrentVersion.replace(sAsset, sName)))

	# rename folder
	sDirectoryProject,sWipDirectory = _getAssetDirectory(sProject = sProject)
	os.rename(sDirectory, os.path.join(sDirectoryProject, sName))

	# write file list
	sDirectory, sWipDirectory = _getAssetDirectory(sProject = sProject)
	_writeFolderListFile(sDirectory, sName, sReplace = sAsset)

	fEndTime = time.time()
	print 'renamed %s to %s, took %f seconds' %(sAsset, sName, fEndTime - fStartTime)

def checkCurrentSceneModified():
	bModified = cmds.file(q=True, modified=True)
	return bModified

def syncAsset(sProject, sAsset, sType, sMode = 'server'):
	fStartTime = time.time()

	if sMode == 'server':
		sPathSync = sPathServer
		sPathSource = sPathLocal
		sModeSource = 'local'
	else:
		sPathSync = sPathLocal
		sPathSource = sPathServer
		sModeSource = 'server'
	syncFolder(sPathSync, sPathSource, sProject)

	if sAsset:
		sPathAsset = os.path.join(sPathSync, sProject)
		sPathAsset = os.path.join(sPathAsset, 'assets')
		files.createFolder(sPathAsset)
		sPathSourceAsset = os.path.join(sPathSource, sProject)
		sPathSourceAsset = os.path.join(sPathSourceAsset, 'assets')
		syncFolder(sPathAsset, sPathSourceAsset, sAsset)

		if sType:
			sPathType = os.path.join(sPathAsset, sAsset)
			sPathSourceType = os.path.join(sPathSourceAsset, sAsset)
			syncFolder(sPathType, sPathSourceType, sType)
			if os.path.exists(os.path.join(sPathType, sType)):
				rmtree(os.path.join(sPathType, sType))

				sPathTypeSync, sPathTemp = _getAssetDirectory(sProject = sProject, sAsset = sAsset, sType = sType, sMode = sModeSource)
				copytree(sPathTypeSync, os.path.join(sPathType, sType))

	fEndTime = time.time()
	sSyncName = ''
	for sName in [sProject, sAsset, sType]:
		if sName:
			sSyncName += '%s'sName
			if sName != sType:
				sSyncName += '\\'
	print 'synced %s, took %f seconds' %(sSyncName, fEndTime - fStartTime)



def syncFolder(sPath, sPathSource, sFolder):
	lFoldersSource = _getFoldersFromFolderList(sPathSource, bCreate = False)
	if sFolder in lFoldersSource:
		lFolders = _getFoldersFromFolderList(sPath, bCreate = True)
		if sFolder not in lFolders:
			files.createFolder(os.path.join(sPath, sFolder))
			_writeFolderListFile(sPath, sFolder)




#### sub functions
def _createProjectFiles(sProjectDir):
	lFiles = cmds.workspace(q = True, fileRuleList = True)
	for sFile in lFiles:
		sFileDir= cmds.workspace(fileRuleEntry = sFile)
		sFileDir = os.path.join(sProjectDir, sFileDir)
		files.createFolder(sFileDir)

def _getProject(rootDirectory = True):
	sDirectory = cmds.workspace(q=True, directory=True, rd = rootDirectory)
	return sDirectory

def _createVersionFile(sAsset, sType, sProject, sDirectory):
	dAssetInfo = {
	'assetInfo':{'sAsset': sAsset, 'sType': sType, 'sProject': sProject, 'sCurrentVersionName': None, 'sFileType': sFileType},
	'versionInfo':{}
	}

	files.writeJsonFile(os.path.join(sDirectory, 'assetInfo.version'), dAssetInfo)

def _getAssetDirectory(sProject = None, sAsset = None, sType = None, sMode = 'local'):
	if sMode == 'local':
		sDirectory = sPathLocal
	else:
		sDirectory = sPathServer
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

def _createFolderListFile(sPath):
	sFolderListPath = os.path.join(sPath, sFolderListName)
	lFolders = []
	files.writeJsonFile(sFolderListPath, lFolders)

def _writeFolderListFile(sPath, sName, sReplace = None, bRemove = False):
	sFolderListPath = os.path.join(sPath, sFolderListName)
	lFolders = files.readJsonFile(sFolderListPath)
	if not bRemove:
		if sReplace:
			lFolders.remove(sReplace)
		lFolders.append(sName)
	else:
		lFolders.remove(sName)
	lFolders.sort()
	files.writeJsonFile(sFolderListPath, lFolders)

def _deleteWorkspaceFolderFromPath(sPath, sFolder):
	sFolderListPath = os.path.join(sPath, sFolderListName)
	_writeFolderListFile(sPath, sFolder, bRemove = True)
	files.deleteFolderFromPath(os.path.join(sPath, sFolder))

def _getFoldersFromFolderList(sPath, bCreate = False):
	sFolderListPath = os.path.join(sPath, sFolderListName)
	if not os.path.exists(sFolderListPath):
		lFolders = []
		if bCreate:
			_createFolderListFile(sPath)
	else:
		lFolders = files.readJsonFile(sFolderListPath)
	return lFolders

def _getVersionFiles(sProject, sAsset = None, sType = None):
	lReturn = []
	sDir, sTemp = _getAssetDirectory(sProject = sProject, sAsset = sAsset, sType = sType)
	if sAsset and sType:
		sVersionFilePath = os.path.join(sDir, 'assetInfo.version')
		if os.path.exists(sVersionFilePath):
			lReturn.append(sVersionFilePath)
	elif sAsset:
		lFolders = _getFoldersFromFolderList(sDir)
		for sFolder in lFolders:
			sDirType = os.path.join(sDir, sFolder)
			sVersionFilePath = os.path.join(sDirType, 'assetInfo.version')
			if os.path.exists(sVersionFilePath):
				lReturn.append(sVersionFilePath)
	else:
		lFolders = _getFoldersFromFolderList(sDir)
		for sFolder in lFolders:
			sDirAsset = os.path.join(sDir, sFolder)
			lFoldersAsset = _getFoldersFromFolderList(sDirAsset)
			for sFolderAsset in lFoldersAsset:
				sDirType = os.path.join(sDirAsset, sFolderAsset)
				sVersionFilePath = os.path.join(sDirType, 'assetInfo.version')
				if os.path.exists(sVersionFilePath):
					lReturn.append(sVersionFilePath)
	return lReturn




