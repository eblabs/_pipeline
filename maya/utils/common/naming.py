#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import utils
import files

#=================#
#   GLOBAL VARS   #
#=================#
from . import PATH_CONFIG, Logger
FILE_CONFIG = os.path.join(PATH_CONFIG, 'NAME_CONVENTION.cfg')
DATA_CONFIG = files.read_json_file(FILE_CONFIG)

DATA_INVERSE = {}
for key, item in DATA_CONFIG.iteritems():
	DATA_INVERSE.update({key:{v: k for k, v in item.iteritems()}})
#=================#
#      CLASS      #
#=================#

class Namer(object):
	"""
	class contains naming functions, include naming class and naming conventions

	"""
	class Naming(object):
		"""
		class to compose/decompose name base on naming convention
		"""
		def __init__(self, *args,**kwargs):

			self.__name = ''

			if args:
				self.__decompose_name(args[0])
			else:
				self.__type = kwargs.get('type', None)
				self.__side = kwargs.get('side', None)
				self.__res = kwargs.get('resolution', None)
				self.__part = kwargs.get('part', None)
				self.__index = kwargs.get('index', None)
				self.__suffix = kwargs.get('suffix', None)

				self.__compose_name()

		# property
		@property
		def type(self):
			return self.__get_name(self.__type,
								   'type',
								   returnType='long')

		@property
		def side(self):
			return self.__get_name(self.__side,
								   'side',
								   returnType='long')

		@property
		def resolution(self):
			return self.__get_name(self.__res,
								   'resolution',
								   returnType='long')

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
			self.__compose_name()
			return self.__name

		# set atters
		@type.setter
		def type(self, key):
			self.__type = self.__get_name(key, 
										  'type',
										  returnType='long')
		@side.setter
		def side(self, key):
			self.__side = self.__get_name(key, 
										  'side',
										  returnType='long')
		@resolution.setter
		def resolution(self, key):
			self.__res = self.__get_name(key, 
										 'resolution',
										 returnType='long')
		@part.setter
		def part(self, key):
			if key:
				self.__part = key
			else:
				self.__part = None

		@index.setter
		def index(self, num):
			if isinstance(num, int) and num >= 0:
				self.__index = int(num)
			else:
				self.__index = None

		@suffix.setter
		def suffix(self, num):
			if isinstance(num, int) and num >= 0:
				self.__suffix = int(num)
			else:
				self.__suffix = None

		def __decompose_name(self, name):
			"""
			decompose name to get each parts name individually

			Args:
				name(str): name for decompose

			Returns:
				self.__type(str): name's type
				self.__side(str): name's side
				self.__res(str): name's resolution
				self.__part(str): name's part
				self.__index(str): name's index
				self.__suffix(str): name's suffix
			"""
			self.__type = None
			self.__side = None
			self.__res = None
			self.__part = None
			self.__index = None
			self.__suffix = None

			nameSplit = name.split('_') #split name parts by '_'

			splitNum = len(nameSplit) # check how many parts

			self.__type = self.__get_name(nameSplit[0], 'type', returnType='long')
			
			if not self.__type:
				Logger.error('Type is invalid')

			if splitNum > 2:
				self.__side = self.__get_name(nameSplit[1], 'side', returnType='long')
				if not self.__side:
					Logger.error('Side is invalid')

				if splitNum == 3:
					# name only contains type side and part
					self.__part = self.__get_name(nameSplit[2])
				
				elif splitNum == 4:
					# name contains type side part and res/index
					self.__res = self.__get_name(nameSplit[2], 'resolution', returnType='long')
					if self.__res:
						self.__part = nameSplit[3]
					else:
						self.__part = nameSplit[2]
						self.__index = int(nameSplit[3])

				elif splitNum == 5:
					# name contains type side part index and res/suffix
					self.__res = self.__get_name(nameSplit[2], 'resolution', returnType='long')
					if self.__res:
						self.__part = nameSplit[3]
						self.__index = int(nameSplit[4])
					else:
						self.__part = nameSplit[2]
						self.__index = int(nameSplit[3])
						self.__suffix = int(nameSplit[4])

				elif splitNum == 6:
					# name contains type side res part index and suffix
					self.__res = self.__get_name(nameSplit[2], 'resolution', returnType='long')
					if not self.__res:
						Logger.error('Resolution is invalid')
					self.__part = nameSplit[3]
					self.__index = nameSplit[4]
					self.__suffix = nameSplit[5]

				else:
					Logger.error('{} is invalid'.format(name))

			elif splitNum == 2:
				Logger.error('{} is invalid'.format(name))

		def __compose_name(self):
			"""
			compose name with given parts
			pattern: type_side_(resolution)_part_index_suffix

			Args:
				self.__type(str): name's type
				self.__side(str): name's side
				self.__res(str): name's resolution
				self.__part(str): name's part
				self.__index(str): name's index
				self.__suffix(str): name's suffix

			Returns:
				self.__name(str): composed name
			"""
			self.__name = ''

			if self.__type:
				# check if the name has side and part
				if self.__side and self.__part:
					for key, keyType in zip([self.__type, self.__side, self.__res], 
								 ['type', 'side', 'resolution']):
						if key:
							key = self.__get_name(key, keyType, returnType='short')
							self.__name+=key+'_'
					self.__name+=self.__part+'_'
					for i in [self.__index, self.__suffix]:
						if i != None:
							self.__name+='{:03d}_'.format(int(i))
					self.__name = self.__name[:-1] # remove the last '_'
				else:
					self.__name = self.__get_name(self.__type, 'type', returnType='short') # name only contains type ('master')
			else:
				# the name is invalid, should at least has type
				Logger.error('Name is invalid, should at least has Type')

		def __get_name(self, key, type, returnType='short'):
			"""
			get the name from the NAME_CONVENTION config file

			Args:
				key(str): naming's type's name ('group'/'jnt' etc..)
				type(str): naming's type ('type'/'resolution'/'side') 
				returnType(str): short/long, return the short name or full name

			Returns:
				name(str): name from the NAME_CONVENTION config file
			"""
			if key in DATA_CONFIG[type]:
				longName = key
				shortName = DATA_CONFIG[type][key]
			elif key in DATA_INVERSE[type]:
				longName = DATA_INVERSE[type][key]
				shortName = key
			else:
				longName = None
				shortName = None

			if returnType == 'short':
				name = shortName
			else:
				name = longName

			return name

	def __init__(self, *args,**kwargs):
		super(Namer, self).__init__()
		
		# initialize name convention
		for key, items in DATA_CONFIG.iteritems():
			setattr(self, key.title(), Objectview(items))

		self.Naming = Namer.Naming

class Objectview(object):
	"""
	Create an object contains dictionary as attrs
	"""
	def __init__(self, kwargs):
		self.__dict__ = kwargs


#=================#
#    FUNCTION     #
#=================#