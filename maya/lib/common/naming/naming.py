# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import namingDict # all the name read from this file

# ---- import end ----

class Naming(object):
	"""
	class to compose name in correct format
	type_side_(resolution)_part_(index)_(suffix)
	"""
	@staticmethod
	def getKeyFullNameFromDict(value, shortDic, longDic):
		'''
		this function will return the short and long name of the given key
		base on the naming dictionary

		parameters:
		value(string): given name for the name (type/side/res)
		shortDic(dictionary): dictionary for short names (longName: short)
		longDic(dictionary): dictionary for long names (shotName: long)
		'''
		if value in shortDic:
			# value is the long name, find short name
			longName = value
			shortName = shortDic[value]

		elif value in longDic:
			# value is the short name, find long name
			shortName = value
			longName = longDic[value]

		else:
			# value is not in the dictionary, return None
			logger.warn('{} is not in the dictionary'.format(value))

			shortName = None
			longName = None

		return shortName, longName

	def __init__(self, *args,**kwargs):
		super(Naming, self).__init__()
		self.__name = '' # the output name
		
		if args:
			self.__decomposeName(args[0])
		else:
			type = kwargs.get('type', None)
			side = kwargs.get('side', None)
			res = kwargs.get('res', None)
			part = kwargs.get('part', None)
			index = kwargs.get('index', None)
			suffix = kwargs.get('suffix', None)

			# get keys short name from dictionary
			self.__type, longName = self.getKeyFullNameFromDict(type, 
									namingDict.dNameConvension['type'], 
									namingDict.dNameConvensionInverse['type'])

			self.__side, longName = self.getKeyFullNameFromDict(side, 
									namingDict.dNameConvension['side'], 
									namingDict.dNameConvensionInverse['side'])

			self.__res, longName = self.getKeyFullNameFromDict(res, 
								namingDict.dNameConvension['resolution'], 
								namingDict.dNameConvensionInverse['resolution'])

			self.__part = part
			self.__index = index
			self.__suffix = suffix

	def __str__(self):
		# return the class name
		return self.__name

	@property
	def type(self): 
		return self.__type

	@property
	def typeLongName(self):
		shortName, longName = self.getKeyFullNameFromDict(self.__type, 
									namingDict.dNameConvension['type'], 
									namingDict.dNameConvensionInverse['type'])
		return longName

	@property
	def side(self):
		return self.__side

	@property
	def sideLongName(self):
		shortName, longName = self.getKeyFullNameFromDict(self.__side, 
									namingDict.dNameConvension['side'], 
									namingDict.dNameConvensionInverse['side'])
		return longName

	@property
	def resolution(self):
		return self.__res

	@property
	def resolutionLongName(self):
		shortName, longName = self.getKeyFullNameFromDict(self.__res, 
								namingDict.dNameConvension['resolution'], 
								namingDict.dNameConvensionInverse['resolution'])
		return longName

	@property
	def part(self):
		return self.__part

	@property
	def index(self):
		return self.__index

	@property
	def suffix(self):
		return self.__suffix

	@property
	def name(self):
		self.__composeName()
		return self.__name

	@type.setter
	def type(self, key):
		shortName, longName = self.getKeyFullNameFromDict(key, 
									namingDict.dNameConvension['type'], 
									namingDict.dNameConvensionInverse['type'])
		self.__type = shortName

	@side.setter
	def side(self, key):
		shortName, longName = self.getKeyFullNameFromDict(key, 
									namingDict.dNameConvension['side'], 
									namingDict.dNameConvensionInverse['side'])
		self.__side = shortName

	@resolution.setter
	def resolution(self, key):
		shortName, longName = self.getKeyFullNameFromDict(key, 
								namingDict.dNameConvension['resolution'], 
								namingDict.dNameConvensionInverse['resolution'])
		self.__res = shortName

	@sPart.setter
	def sPart(self, sKey):
		if sKey:
			self.__sPart = sKey
		else:
			self.__sPart = None

	@index.setter
	def index(self, num):
		if isinstance(num, int) and num >= 0:
			self.__index = num
		else:
			self.__index = None

	@suffix.setter
	def suffix(self, num):
		if isinstance(num, int) and num >= 0:
			self.__suffix = num
		else:
			self.__suffix = None

	def __decomposeName(self, name):
		nameSplitList = name.split('_') #split the name by '_'

		splitNum = len(nameSplitList) # check how many parts are splitted
		
		self.__type = nameSplitList[0] # type is mandatory

		if splitNum == 3:
			# the name only has type side and part
			self.__side = nameSplitList[1]
			self.__res = None
			self.__part = nameSplitList[2]
			self.__index = None
			self.__suffix = None

		elif splitNum == 4:
			# the name has type side part, and either res or index
			self.__side = nameSplitList[1]

			if nameSplitList[2] in namingDict.dNameConvensionInverse['resolution']:
				# the name contains res
				self.__res = nameSplitList[2]
				self.__part = nameSplitList[3]
				self.__index = None
				self.__suffix = None

			else:
				# the name has index
				self.__res = None
				self.__part = nameSplitList[2]
				self.__index = int(nameSplitList[3])
				self.__suffix = None

		elif splitNum == 5:
			# the name doesn't have either res or suffix
			self.__side = nameSplitList[1]

			if nameSplitList[2] in namingDict.dNameConvensionInverse['resolution']:
				# the name contains res
				self.__res = nameSplitList[2]
				self.__part = nameSplitList[3]
				self.__index = int(nameSplitList[4])
				self.__suffix = None

			else:
				# the name has suffix
				self.__res = None
				self.__part = nameSplitList[2]
				self.__index = int(nameSplitList[3])
				self.__suffix = int(nameSplitList[4])

		elif splitNum == 6:
			# the name contains everything
			self.__side = nameSplitList[1]
			self.__res = nameSplitList[2]
			self.__part = nameSplitList[3]
			self.__index = int(nameSplitList[4])
			self.__suffix = int(nameSplitList[5])

		elif splitNum == 1:
			# the name only has type, like 'master'
			self.__side = None
			self.__res = None
			self.__part = None
			self.__index = None
			self.__suffix = None

		else:
			# the name is invalid
			logger.error('The name is invalid')

	def __composeName(self):
		if self.__type:
			# check if the name has type
			if self.__side and self.__part:
				# the name contains at least three main factors

				for key in [self.__type, 
							 self.__side, 
							 self.__res, 
							 self.__part]:
					# add all valuable key
					if key:
						self.__name += '{}_'.format(key)

				for num in [self.__index, self.__suffix]:
					# add all valuable number
					if num:
						self.__name += '{:03d}_'.format(num)

				self.__name = self.__name[:-1] # remove the last '_'

			else:
				# the name missed key factors, ignore everything except type
				self.__name = self.__type

		else:
			# the name is invalid, should at least has type
			logger.error('The name is invalid, should at least has type')
