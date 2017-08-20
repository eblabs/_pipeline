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
	mel.eval('setProject /"' + sDirectory + '/"')

def createAsset(sName, sType = 'model'):
	sDirectory = _getProject()
	if sPathLocal not in sDirectory:
		raise Exception('This project is not set to the proper path, you need to save the project under %s to link to the server' %sPathLocal)
	sAssetDir = os.path.join(sDirectory, 'assets')
	sAssetDir = os.path.join(sAssetDir, sName)
	sAssetWipDir = os.path.join(sAssetDir, 'wipFiles')
	_createFolder(sAssetDir)
	_createFolder(sAssetWipDir)



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
	sDirectory = cmds.workspace(q=True, directory=True)
	return sDirectory