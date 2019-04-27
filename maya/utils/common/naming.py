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
	compose/decompose name base on naming convention

	"""
	def __init__(self, *args,**kwargs):
		super(Namer, self).__init__()
		
		# initialize name convention
		for key, items in DATA_CONFIG.iteritems():
			setattr(self, key.title(), Objectview(items))

	def __decompose_name(self, name):
		"""
		decompose name to get each parts name individually

		Args:
			name(str): name for decompose
		"""
		pass

	def __compose_name(self, type, side, res, part, index, suffix):
		"""
		compose name with given parts
		pattern: type_side_(resolution)_part_index_suffix

		Args:
			type(str): name's type
			side(str): name's side
			res(str): name's resolution
			part(str): name's part
			index(str): name's index
			suffix(str): name's suffix

		Returns:
			name(str): composed name
		"""
		name = ''

		if type:
			# check if the name has side and part
			if side and part:
				for k in [type, side, res, part]:
					if k:
						name+=k+'_'
				for i in [index, suffix]:
					if i != None:
						name+='{:03d}_'.format(i)
				name = name[:-1] # remove the last '_'
			else:
				name = type # name only contains type ('master')
		else:
			# the name is invalid, should at least has type
			Logger.error('Name is invalid, should at least has Type')

		return name

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

class Objectview(object):
	"""
	Create an object contains dictionary as attrs
	"""
	def __init__(self, kwargs):
		self.__dict__ = kwargs


#=================#
#    FUNCTION     #
#=================#