## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json

## Vars
import getpass
sUser = getpass.getuser()
sPathServer = 'C:/Users/%s/Dropbox/_works/' %sUser
sPathLocal = 'C:/_works/maya/'

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

	dAssetInfo = {
	'assetInfo':{'sName': sName, 'sType': sType},
	'versionInfo':{}
	}

	writeJsonFile(os.path.join(sAssetDir, 'assetInfo.version'), dAssetInfo)

def writeJsonFile(sPath, data):
	with open(sPath, 'w') as sOutfile:
		json.dump(data, sOutfile)
	file.close(sOutfile)

def readJsonFile(sPath):
	if not os.path.exists(sPath):
		raise RuntimeError('The file is not exist')
	with open(sPath, 'r') as sInfile:
		data = json.loads(sInfile)
	file.close(sInfile)
	return data



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

def _getProject():
	sDirectory = cmds.workspace(q=True, directory=True, rd = True)
	return sDirectory