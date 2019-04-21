## component info functions

def composeListToString(lList):
	sString = ''
	if lList:
		for sItem in lList:
			sString += '%s,' %str(sItem)
		sString = sString[:-1]
	else:
		sString = ''
	return sString

def decomposeStringToStrList(sString):
	if sString:
		lList = sString.split(',')
	else:
		lList = None
	return lList

def decomposeStringToIntList(sString):
	lList = []
	if sString:
		for sStr in sString.split(','):
			lList.append(int(sStr))
	else:
		lList = None
	return lList