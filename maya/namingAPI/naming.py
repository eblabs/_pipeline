import namingDict

class oName(object):
	"""docstring for oName"""
	def __init__(self, *args, **kwargs):
		super(oName, self).__init__()
		## arguments
		self.sType = None
		self.sSide = None
		self.sRes = None
		self.sPart = None
		self.iIndex = None
		self.iSuffix = None

		if args:
			self.decomposeName(args[0])
		else:
			sType = kwargs.get('sType', None)
			sSide = kwargs.get('sSide', None)
			sRes = kwargs.get('sRes', None)
			sPart = kwargs.get('sPart', None)
			iIndex = kwargs.get('iIndex', None)
			iSuffix = kwargs.get('iSuffix', None)

			if sType:
				self.sType = getKeyFromNamePart(sType, 'type')
			if sSide:
				self.sSide = getKeyFromNamePart(sSide, 'side')
			if sRes:
				self.sRes = getKeyFromNamePart(sRes, 'resolution')
			if sPart:
				self.sPart = sPart
			if iIndex:
				self.iIndex = iIndex
			if iSuffix:
				self.iSuffix = iSuffix

	@property
	def sName(self):
		if not self.sPart or not self.sType:
			raise RuntimeError('The name entered is invalid')
		if sType:
			self.sType = getKeyFromNamePart(sType, 'type')
		if sSide:
			self.sSide = getKeyFromNamePart(sSide, 'side')
		if sRes:
			self.sRes = getKeyFromNamePart(sRes, 'resolution')
		sName = ''
		for sNamePart in [self.sType, self.sSide, self.sRes, self.sPart]:
			if sNamePart:
				sName += '%s_' %sNamePart
		for iNum in [self.iIndex, self.iSuffix]:
			if iNum:
				sName += '%03d_' %iNum
		return sName[:-1]

	def decomposeName(self, sName):
		lNameParts = sName.split('_')
		if len(lNameParts) == 6:
			sType = getKeyFromNamePart(lNameParts[0], 'type')
			sSide = getKeyFromNamePart(lNameParts[1], 'side')
			sRes = getKeyFromNamePart(lNameParts[2], 'resolution')
			sPart = lNameParts[3]
			iIndex = int(lNameParts[4])
			iSuffix = int(lNameParts[5])
		elif len(lNameParts) == 5:
			sType = getKeyFromNamePart(lNameParts[0], 'type')

			if lNameParts[4].isdigit() and lNameParts[3].isdigit():
				iIndex = int(lNameParts[3])
				iSuffix = int(lNameParts[4])
				sPart = lNameParts[2]
				sSide = getKeyFromNamePart(lNameParts[1], 'side')
				if sSide:
					sRes = None 
					sResValue = None
				else:
					sRes = getKeyFromNamePart(lNameParts[1], 'resolution')
			else:
				iIndex = int(lNameParts[4])
				sPart = lNameParts[3]
				sSide = getKeyFromNamePart(lNameParts[1], 'side')
				sRes = getKeyFromNamePart(lNameParts[2], 'resolution')
				iSuffix = None

		elif len(lNameParts) == 4:
			sType = getKeyFromNamePart(lNameParts[0], 'type')
			sSide = getKeyFromNamePart(lNameParts[1], 'side')
			iSuffix = None
			if lNameParts[3].isdigit():
				iIndex = int(lNameParts[3])
				sPart = lNameParts[2]
				sRes = None
				sResValue = None
			else:
				sSide = getKeyFromNamePart(lNameParts[1], 'side')
				sRes = getKeyFromNamePart(lNameParts[2], 'resolution')
				sPart = lNameParts[3]
				iIndex = None

		else:
			sType = getKeyFromNamePart(lNameParts[0], 'type')
			sPart = lNameParts[2]
			iIndex = None
			iSuffix = None
			sSide = getKeyFromNamePart(lNameParts[1], 'side')
			if sSide:
				sRes = None 
				sResValue = None
			else:
				sRes = getKeyFromNamePart(lNameParts[1], 'resolution')

		self.sType = sType
		self.sSide = sSide
		self.sRes = sRes
		self.sPart = sPart
		self.iIndex = iIndex
		self.iSuffix = iSuffix

	def getKeyFullName(self, sKey, sType):
		return getFullNameFromKey(sKey, sType)


# functions
def getKeyFromNamePart(sNamePart, sKeyType):
	if namingDict.dNameConvension[sKeyType].has_key(sNamePart):
		sKey = namingDict.dNameConvension[sKeyType][sNamePart]
	elif namingDict.dNameConvensionInverse[sKeyType].has_key(sNamePart):
		sKey = sNamePart
	else:
		sKey = None
	return sKey

def getFullNameFromKey(sKey, sKeyType):
	if namingDict.dNameConvensionInverse[sKeyType].has_key(sKey):
		sName = namingDict.dNameConvensionInverse[sKeyType][sKey]
	elif namingDict.dNameConvension[sKeyType].has_key(sKey):
		sName = sKey
	else:
		sName = None
	return sName