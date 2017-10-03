## External Import
import maya.cmds as cmds
import json
import os
from shutil import rmtree
import cPickle
## Vars
lAssetTypes = ['model', 'rig']
import getpass
sUser = getpass.getuser()
sPathServer = os.path.abspath('C:/Users/%s/Dropbox/_works/maya/' %sUser)
sPathLocal = os.path.abspath('C:/_works/maya/')

iBackup = 20
sFileType = '.mb'
sFolderListName = 'folders.folderList'
lProjectFolders = ['assets']
dRiggingComponents = {
						'buildScript': '.py', 
						'blueprint': '.blueprint', 
						'rigGeometry': sFileType, 
						'geoHierarchy': '.geoHierarchy', 
						'deformer': '.deformer', 
						'controlShape': '.ctrlShape',
					}

#### Functions

#------------ custom file functions -----------
def writeJsonFile(sPath, data):
	with open(sPath, 'w') as sOutfile:
		json.dump(data, sOutfile)
	file.close(sOutfile)

def readJsonFile(sPath):
	with open(sPath, 'r') as sInfile:
		data = json.load(sInfile)
	file.close(sInfile)
	return data

def writePickleFile(sPath, data):
	sOutfile = open(sPath, 'wb')
	cPickle.dump(data, sOutfile, cPickle.HIGHEST_PROTOCOL)
	sOutfile.close()

def readPickleFile(sPath):
	sInfile = open(sPath, 'rb')
	data = cPickle.load(sInfile)
	sInfile.close()
	return data
#------------ custom file functions End -----------

#------------ folder & path functions -----------
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


def getFilesFromPath(sPath, sType = None):
	lFiles = os.listdir(sPath)
	os.chdir(sPath)
	lFilesReturn = []
	if not sType:
		lFilesReturn = lFiles
	else:
		for sFile in lFiles:
			if sType == 'folder':
				if not os.path.isfile(sFile):
					lFilesReturn.append(sFile)
			elif sType == 'file':
				if os.path.isfile(sFile):
					lFilesReturn.append(sFile)
			else:
				if sFile.endswith(sType):
					lFilesReturn.append(sFile)
	return lFilesReturn
#------------ folder & path functions End -----------

#------------ maya files functions -----------
def exportNodes(lNodes, sPath):
	cmds.select(lNodes)
	if sPath.endswith('.mb'):
		sFileTypeLong = 'mayaBinary'
	elif sPath.endswith('.ma'):
		sFileTypeLong = 'mayaAscii'
	cmds.file(sPath, type = sFileTypeLong, pr = True, es = True)

def importMayaFile(sPath, sNamespace = None):
	if sNamespace:
		cmds.file(sPath, i = True, namespace = sNamespace)
	else:
		cmds.file(sPath, i = True)

#------------ maya files functions -----------

#### sub Functions
def _getFoldersThroughPath(sPath):	
	sPathDir = os.path.abspath(sPath)
	sPathBase = os.path.basename(sPathDir)
	sPathDir = os.path.dirname(sPathDir)
	lFolders = sPathDir.split('\\')
	lFolders.append(sPathBase)
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
