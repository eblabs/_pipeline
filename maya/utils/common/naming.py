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
class Type(object):
	"""Type class to acess type varibles"""
	def __init__(self):
		pass

class Side(object):
	"""Side class to acess side varibles"""
	def __init__(self):
		pass

class Resolution(object):
	"""Resolution class to acess resolution varibles"""
	def __init__(self):
		pass

# add static attrs for above classes base on dictionary
for key, item in DATA_CONFIG.iteritems():
	Obj = getattr(sys.modules[__name__], key.title())
	for nameLong, nameShort in item.iteritems():
		setattr(Obj, nameLong, nameShort)

class Namer(object):
	"""
	class to compose/decompose name base on naming convention

	"""

	# shortcuts for inputs
	shortcuts = {'type':        'typ',
				 'side':        'sid',
				 'resolution':  'res',
				 'description': 'des',
				 'index':       'idx',
				 'suffix':      'sfx'}

	def __init__(self, *args,**kwargs):
		"""
		Args:
			name(str): decompose the given name
		Kwargs:
			for compose name with given parts

			type/typ(str): name's type
			side/sid(str): name's side
			resolution/res(str): name's resolution
			description/des(str): name's description
			index/idx(str): name's index
			suffix/sfx(str): name's suffix

		Properties:
			type/typ(str)
			side/sid(str)
			resolution/res(str)
			description/des(str)
			index/idx(str)
			suffix/sfx(str)
			name(str)
		"""

		self.__name = ''

		if args:
			self.__decompose_name(args[0])
		else:
			for key, item in self.shortcuts.iteritems():
				val_short = kwargs.get(item, None)
				val_long = kwargs.get(key, None)
				if val_long:
					val_short = val_long
				setattr(self, '_Namer__'+key, val_short)

			self.__compose_name()

	# property
	@property
	def type(self):
		return self.__get_name(self.__type,
							   'type',
							   returnType='long')
	@property
	def typ(self):
		return self.__get_name(self.__type,
							   'type',
							   returnType='long')

	@property
	def side(self):
		return self.__get_name(self.__side,
							   'side',
							   returnType='long')
	@property
	def sid(self):
		return self.__get_name(self.__side,
							   'side',
							   returnType='long')

	@property
	def resolution(self):
		return self.__get_name(self.__resolution,
							   'resolution',
							   returnType='long')
	@property
	def res(self):
		return self.__get_name(self.__resolution,
							   'resolution',
							   returnType='long')

	@property
	def description(self):
		return self.__description

	@property
	def des(self):
		return self.__description

	@property
	def index(self):
		return self.__index

	@property
	def idx(self):
		return self.__index

	@property
	def suffix(self):
		return self.__suffix

	@property
	def sfx(self):
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
	@typ.setter
	def typ(self, key):
		self.__type = self.__get_name(key, 
									  'type',
									  returnType='long')
	@side.setter
	def side(self, key):
		self.__side = self.__get_name(key, 
									  'side',
									  returnType='long')
	@sid.setter
	def sid(self, key):
		self.__side = self.__get_name(key, 
									  'side',
									  returnType='long')
	@resolution.setter
	def resolution(self, key):
		self.__resolution = self.__get_name(key, 
									 'resolution',
									 returnType='long')
	@res.setter
	def res(self, key):
		self.__resolution = self.__get_name(key, 
									 'resolution',
									 returnType='long')
	@description.setter
	def description(self, key):
		if key:
			self.__description = key
		else:
			self.__description = None

	@des.setter
	def des(self, key):
		if key:
			self.__description = key
		else:
			self.__description = None

	@index.setter
	def index(self, num):
		if isinstance(num, int) and num >= 0:
			self.__index = int(num)
		else:
			self.__index = None

	@idx.setter
	def idx(self, num):
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

	@sfx.setter
	def sfx(self, num):
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
			self.__resolution(str): name's resolution
			self.__description(str): name's description
			self.__index(str): name's index
			self.__suffix(str): name's suffix
		"""
		self.__type = None
		self.__side = None
		self.__resolution = None
		self.__description = None
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
				# name only contains type side and des
				self.__description = self.__get_name(nameSplit[2])
			
			elif splitNum == 4:
				# name contains type side des and res/index
				self.__resolution = self.__get_name(nameSplit[2], 'resolution', returnType='long')
				if self.__resolution:
					self.__description = nameSplit[3]
				else:
					self.__description = nameSplit[2]
					self.__index = int(nameSplit[3])

			elif splitNum == 5:
				# name contains type side des index and res/suffix
				self.__resolution = self.__get_name(nameSplit[2], 'resolution', returnType='long')
				if self.__resolution:
					self.__description = nameSplit[3]
					self.__index = int(nameSplit[4])
				else:
					self.__description = nameSplit[2]
					self.__index = int(nameSplit[3])
					self.__suffix = int(nameSplit[4])

			elif splitNum == 6:
				# name contains type side res des index and suffix
				self.__resolution = self.__get_name(nameSplit[2], 'resolution', returnType='long')
				if not self.__resolution:
					Logger.error('Resolution is invalid')
				self.__description = nameSplit[3]
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
			self.__resolution(str): name's resolution
			self.__description(str): name's description
			self.__index(str): name's index
			self.__suffix(str): name's suffix

		Returns:
			self.__name(str): composed name
		"""
		self.__name = ''

		if self.__type:
			# check if the name has side and des
			if self.__side and self.__description:
				for key, keyType in zip([self.__type, self.__side, self.__resolution], 
							 ['type', 'side', 'resolution']):
					if key:
						key = self.__get_name(key, keyType, returnType='short')
						self.__name+=key+'_'
				self.__name+=self.__description+'_'
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

#=================#
#    FUNCTION     #
#=================#