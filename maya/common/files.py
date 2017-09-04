## External Import
import maya.cmds as cmds
import json
import os
from shutil import rmtree
## Vars
lAssetTypes = ['model', 'rig']
import getpass
sUser = getpass.getuser()
sPathServer = os.path.abspath('C:/Users/%s/Dropbox/_works/' %sUser)
sPathLocal = os.path.abspath('C:/_works/maya/')

iBackup = 20
sFileType = '.mb'
sFolderListName = 'folders.folderList'
lProjectFolders = ['assets']

#### Functions
def writeJsonFile(sPath, data):
	with open(sPath, 'w') as sOutfile:
		json.dump(data, sOutfile)
	file.close(sOutfile)

def readJsonFile(sPath):
	if not os.path.exists(sPath):
		raise RuntimeError('The file is not exist')
	with open(sPath, 'r') as sInfile:
		data = json.load(sInfile)
	file.close(sInfile)
	return data

def createFolder(sDirectory):
	if not os.path.exists(sDirectory):
		os.makedirs(sDirectory)
		cmds.warning('%s did not exist, created the folders' %sDirectory)

def openFolderFromPath(sPath):
	if os.path.exists(sPath):
		os.startfile(sPath)
	else:
		cmds.warning('%s does not exist' %sPath)

def deleteFolderFromPath(sPath):
	shutil.rmtree(sPath)
	print 'Delete %s sucessfully' %sPath

	
#### sub Functions

def _getFoldersThroughPath(sPath):
	sPathDir = os.path.dirname(sPath)
	sPathDir = os.path.abspath(sPathDir)
	lFolders = sPathDir.split('\\')
	return lFolders

def _getBaseFileFromPath(sPath):
	sPathDir = os.path.abspath(sPath)
	sFile = os.path.basename(sPathDir)
	return sFile

def _convertStringToCamelcase(sString):
	if '_' in sString:
		sStringParts = sString.split('_')
		sString = ''
		for sPart in sStringParts:
			sString += sPart[0].upper() + sPart[1:]
	if ' ' in sString:
		sStringParts = sString.split(' ')
		sString = ''
		for sPart in sStringParts:
			sString += sPart[0].upper() + sPart[1:]
	sString = sString[0].lower() + sString[1:]
	return sString
