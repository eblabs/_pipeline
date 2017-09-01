## External Import
import json
import os

## Vars
lAssetTypes = ['model', 'rig']

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

def getFileFromPath(sPath, sName, sType = None):
	lFiles = getFilesFromPath(sPath, sType = sType)
	sFileReturn = None
	if not sType:
		for sFile in lFiles:
			if sFile == sName:
				sFileReturn = sFile
				break
			elif '.' in sFile:
				if sFile.split('.')[0] == sName:
					sFileReturn = sFile
					break
	elif sType == 'folder':
		if sName in lFiles:
			sFileReturn = sName
	else:
		if '%s%s' %(sName, sType) in lFiles:
			sFileReturn = '%s%s' %(sName, sType)
	return sFileReturn

def getFilesFromDirectoryAndSubDirectories(sPath, sType = None):
	lFilesReturn = []
	for sPathEach, lSubDirectories, lFiles in os.walk(sPath):
		for sSubDirectory in lSubDirectories:
			if not sType or sType == 'folder':
				lFilesReturn.append(os.path.join(sPathEach, sSubDirectory))
		for sFile in lFiles:
			if not sType or sType == 'file':
				lFilesReturn.append(os.path.join(sPathEach, sFile))
			elif sType != 'folder':
				if sFile.endswith(sType):
					lFilesReturn.append(os.path.join(sPathEach, sFile))
	return lFilesReturn

			


#### sub Functions
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
