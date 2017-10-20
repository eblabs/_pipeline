import namingDict
reload(namingDict)
class oName(object):
	"""docstring for oName"""
	def __init__(self, *args, **kwargs):
		super(oName, self).__init__()

		if args:
			self.decomposeName(args[0])
		else:
			sType = kwargs.get('sType', None)
			sSide = kwargs.get('sSide', None)
			sRes = kwargs.get('sRes', None)
			sPart = kwargs.get('sPart', None)
			iIndex = kwargs.get('iIndex', None)
			iSuffix = kwargs.get('iSuffix', None)


			self.__sType = getKeyFromNamePart(sType, 'type')

			self.__sSide = getKeyFromNamePart(sSide, 'side')

			self.__sRes = getKeyFromNamePart(sRes, 'resolution')

			self.sPart = sPart

			self.iIndex = iIndex

			self.iSuffix = iSuffix

	@property
	def sType(self):
		return self.__sType

	@property
	def sSide(self):
		return self.__sSide

	@property
	def sRes(self):
		return self.__sRes

	@sType.setter
	def sType(self, sKey):
		if sKey:
			sName = getKeyFromNamePart(sKey, 'type')
		else:
			sName = None
		self.__sType = sName

	@sSide.setter
	def sSide(self, sKey):
		if sKey:
			sName = getKeyFromNamePart(sKey, 'side')
		else:
			sName = None
		self.__sSide = sName

	@sRes.setter
	def sRes(self, sKey):
		if sKey:
			sName = getKeyFromNamePart(sKey, 'resolution')
		else:
			sName = None
		self.__sRes = sName

	@property
	def sTypeKey(self):
		if self.__sType:
			sKey = getFullNameFromKey(self.__sType, 'type')
		else:
			sKey = None
		return sKey

	@property
	def sSideKey(self):
		if self.__sSide:
			sKey = getFullNameFromKey(self.__sSide, 'side')
		else:
			sKey = None
		return sKey

	@property
	def sResKey(self):
		if self.__sRes:
			sKey = getFullNameFromKey(self.__sRes, 'resolution')
		else:
			sKey = None
		return sKey

	@property
	def sName(self):
		sName = self.composeName(self.__sType, self.__sSide, self.__sRes, self.sPart, self.iIndex, self.iSuffix)
		return sName

	def composeName(self, sType, sSide, sRes, sPart, iIndex, iSuffix):
		if not sPart:
			raise RuntimeError('The name entered is invalid')
		elif not sType:
			if sSide or sRes or iIndex or iSuffix:
				raise RuntimeError('The name entered is invalid')
		elif not sRes and not sSide:
			raise RuntimeError('The name entered is invalid')
		sName = ''
		for sNamePart in [sType, sSide, sRes, sPart]:
			if sNamePart:
				sName += '%s_' %sNamePart
		for iNum in [iIndex, iSuffix]:
			if iNum:
				sName += '%03d_' %iNum
		return sName[:-1]

	def decomposeName(self, sName):
		lNameParts = sName.split('_')
		if len(lNameParts) > 1:
			self.__sType = getKeyFromNamePart(lNameParts[0], 'type')
			if len(lNameParts) == 6:			
				self.__sSide = getKeyFromNamePart(lNameParts[1], 'side')
				self.__sRes = getKeyFromNamePart(lNameParts[2], 'resolution')
				self.sPart = lNameParts[3]
				self.iIndex = int(lNameParts[4])
				self.iSuffix = int(lNameParts[5])
			elif len(lNameParts) == 5:
				if lNameParts[4].isdigit() and lNameParts[3].isdigit():
					self.iIndex = int(lNameParts[3])
					self.iSuffix = int(lNameParts[4])
					self.sPart = lNameParts[2]
					self.__sSide = getKeyFromNamePart(lNameParts[1], 'side')
					if self.sSide:
						self.__sRes = None 
					else:
						self.__sRes = getKeyFromNamePart(lNameParts[1], 'resolution')
				else:
					self.iIndex = int(lNameParts[4])
					self.sPart = lNameParts[3]
					self.__sSide = getKeyFromNamePart(lNameParts[1], 'side')
					self.__sRes = getKeyFromNamePart(lNameParts[2], 'resolution')
					self.iSuffix = None

			elif len(lNameParts) == 4:
				self.__sSide = getKeyFromNamePart(lNameParts[1], 'side')
				self.iSuffix = None
				if lNameParts[3].isdigit():
					self.iIndex = int(lNameParts[3])
					self.sPart = lNameParts[2]
					self.__sRes = None
				else:
					self.__sSide = getKeyFromNamePart(lNameParts[1], 'side')
					self.__sRes = getKeyFromNamePart(lNameParts[2], 'resolution')
					self.sPart = lNameParts[3]
					self.iIndex = None

			elif len(lNameParts) == 3:
				self.sPart = lNameParts[2]
				self.iIndex = None
				self.iSuffix = None
				self.__sSide = getKeyFromNamePart(lNameParts[1], 'side')
				if self.__sSide:
					self.__sRes = None 
				else:
					self.__sRes = getKeyFromNamePart(lNameParts[1], 'resolution')
			else:
				raise RuntimeError('name is not valid')
		else:
			self.sPart = lNameParts[0]
			self.__sType = None
			self.__sSide = None
			self.__sRes = None
			self.iIndex = None
			self.iSuffix = None
		

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