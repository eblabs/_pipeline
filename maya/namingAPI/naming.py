import namingDict

class oName(object):
	"""docstring for oName"""
	def __init__(self, *args, **kwargs):
		super(oName, self).__init__()

		if args:
			self._decomposeName(args[0])
		else:
			sType = kwargs.get('sType', None)
			sSide = kwargs.get('sSide', None)
			sRes = kwargs.get('sRes', None)
			sPart = kwargs.get('sPart', None)
			iIndex = kwargs.get('iIndex', None)
			iSuffix = kwargs.get('iSuffix', None)

			if sType:
				self._sType = sType
			if sSide:
				self._sSide = sSide
			if sRes:
				self._sRes = sRes
			if sPart:
				self.sPart = sPart
			if iIndex:
				self.iIndex = iIndex
			if iSuffix:
				self.iSuffix = iSuffix

	@property
	def sType(self):
		return self._sType

	@property
	def sSide(self):
		return self._sSide

	@property
	def sRes(self):
		return self._sRes

	@sType.setter
	def sType(self, sKey):
		if sKey:
			sName = getKeyFromNamePart(sKey, 'type')
		else:
			sName = None
		self._sType = sName

	@sSide.setter
	def sSide(self, sKey):
		if sKey:
			sName = getKeyFromNamePart(sKey, 'side')
		else:
			sName = None
		self._sSide = sName

	@sRes.setter
	def sRes(self, sKey):
		if sKey:
			sName = getKeyFromNamePart(sKey, 'resolution')
		else:
			sName = None
		self._sRes = sName

	@property
	def sTypeKey(self):
		if self._sType:
			sKey = getFullNameFromKey(self._sType, 'type')
		else:
			sKey = None
		return sKey

	@property
	def sSideKey(self):
		if self._sSide:
			sKey = getFullNameFromKey(self._sSide, 'side')
		else:
			sKey = None
		return sKey

	@property
	def sResKey(self):
		if self._sRes:
			sKey = getFullNameFromKey(self._sRes, 'resolution')
		else:
			sKey = None
		return sKey

	@property
	def sName(self):
		if not self.sPart or not self._sType:
			raise RuntimeError('The name entered is invalid')
		sName = ''
		for sNamePart in [self._sType, self._sSide, self._sRes, self.sPart]:
			if sNamePart:
				sName += '%s_' %sNamePart
		for iNum in [self.iIndex, self.iSuffix]:
			if iNum:
				sName += '%03d_' %iNum
		return sName[:-1]

	def _decomposeName(self, sName):
		lNameParts = sName.split('_')
		self._sType = getKeyFromNamePart(lNameParts[0], 'type')
		if len(lNameParts) == 6:			
			self._sSide = getKeyFromNamePart(lNameParts[1], 'side')
			self._sRes = getKeyFromNamePart(lNameParts[2], 'resolution')
			self.sPart = lNameParts[3]
			self.iIndex = int(lNameParts[4])
			self.iSuffix = int(lNameParts[5])
		elif len(lNameParts) == 5:
			if lNameParts[4].isdigit() and lNameParts[3].isdigit():
				self.iIndex = int(lNameParts[3])
				self.iSuffix = int(lNameParts[4])
				self.sPart = lNameParts[2]
				self._sSide = getKeyFromNamePart(lNameParts[1], 'side')
				if self.sSide:
					self._sRes = None 
				else:
					self._sRes = getKeyFromNamePart(lNameParts[1], 'resolution')
			else:
				self.iIndex = int(lNameParts[4])
				self.sPart = lNameParts[3]
				self._sSide = getKeyFromNamePart(lNameParts[1], 'side')
				self._sRes = getKeyFromNamePart(lNameParts[2], 'resolution')
				self.iSuffix = None

		elif len(lNameParts) == 4:
			self._sSide = getKeyFromNamePart(lNameParts[1], 'side')
			self.iSuffix = None
			if lNameParts[3].isdigit():
				self.iIndex = int(lNameParts[3])
				self.sPart = lNameParts[2]
				self._sRes = None
			else:
				self._sSide = getKeyFromNamePart(lNameParts[1], 'side')
				self._sRes = getKeyFromNamePart(lNameParts[2], 'resolution')
				self.sPart = lNameParts[3]
				self.iIndex = None

		else:
			self.sPart = lNameParts[2]
			self.iIndex = None
			self.iSuffix = None
			self._sSide = getKeyFromNamePart(lNameParts[1], 'side')
			if self._sSide:
				self._sRes = None 
			else:
				self._sRes = getKeyFromNamePart(lNameParts[1], 'resolution')

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