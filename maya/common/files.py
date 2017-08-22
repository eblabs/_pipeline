## External Import
import json
import os

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
