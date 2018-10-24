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
	def __init__(self, *args,**kwargs):
		super(Naming, self).__init__()
		self.__name = '' # the output name
		
		if args:
			self.__decomposeName(args[0])
		else:
			type = kwargs.get('type', None)
			side = kwargs.get('side', None)
			res = kwargs.get('resolution', None)
			part = kwargs.get('part', None)
			index = kwargs.get('index', None)
			suffix = kwargs.get('suffix', None)

			# get keys short name from dictionary
			self.__type = getName(type, 'type', returnType = 'shortName')
			self.__side = getName(side, 'side', returnType = 'shortName')
			self.__res = getName(res, 'resolution', returnType = 'shortName')
			self.__part = part
			self.__index = index
			self.__suffix = suffix

			self.__composeName()

	def __str__(self):
		# return the class name
		return self.__name

	@property
	def type(self): 
		return self.__type

	@property
	def typeLongName(self):
		longName = getName(self.__type, 'type', returnType = 'longName')
		return longName

	@property
	def side(self):
		return self.__side

	@property
	def sideLongName(self):
		longName = getName(self.__side, 'side', returnType = 'longName')
		return longName

	@property
	def resolution(self):
		return self.__res

	@property
	def resolutionLongName(self):
		longName = getName(self.__res, 'resolution', returnType = 'longName')
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
		self.__type = getName(key, 'type', returnType = 'shortName')

	@side.setter
	def side(self, key):
		self.__side = getName(key, 'side', returnType = 'shortName')

	@resolution.setter
	def resolution(self, key):
		self.__res = getName(key, 'resolution', returnType = 'shortName')

	@part.setter
	def part(self, key):
		if key:
			self.__part = key
		else:
			self.__part = None

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

			if getName(nameSplitList[2], 'resolution', returnType='longName'):
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

			if getName(nameSplitList[2], 'resolution', returnType='longName'):
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
		self.__name = ''
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
			raise RuntimeError()

# get name function
def getName(key, type, returnType='shortName'):
	'''
	this function will return the short or long name of the given key
	base on the naming dictionary

	parameters:
	key(string): given name for the name (type/side/res)
	type(string): given key of the dictionary (type/side/resolution)
	returnType(string): shortName/longName
	'''
	if key in namingDict.nameDict[type]:
		# value is the long name, find short name
		longName = key
		shortName = namingDict.nameDict[type][key]

	elif key in namingDict.nameInverseDict[type]:
		# value is the short name, find long name
		shortName = key
		longName = namingDict.nameInverseDict[type][key]
	else:
		shortName = None
		longName = None

	if returnType == 'shortName':
		name = shortName
	else:
		name = longName

	return name

# get all keys from dictionary
def getKeys(type, returnType='longName'):
	if type in namingDict.nameDict:
		if returnType == 'longName':
			keyList = namingDict.nameDict[type].keys()
		else:
			keyList = namingDict.nameInverseDict[type].keys()
	else:
		keyList = []
	return keyList