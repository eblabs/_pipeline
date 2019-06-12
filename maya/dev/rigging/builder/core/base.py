#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.naming as naming
import utils.common.variables as variables
import utils.common.transforms as transforms
import utils.common.attributes as attributes
import utils.common.hierarchy as hierarchy
import utils.common.nodeUtils as nodeUtils
import utils.rigging.constraints as constraints

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#
class Base(object):
	"""
	base template for all the build script
	"""
	def __init__(self):
		super(Base, self).__init__()
		
		self._preBuild = []
		self._build = []
		self._postBuild = []

	def register_task(self, **kwargs):
		'''
		register task to build script

		Kwargs:
			name(str): task dispay name
			task(method): task function
			section(str): register task to section
						 'PreBuild', 'Build', 'PostBuild'
			index(str/int): register task at specific index
							if given string, it will register after the given task
			parent(str): parent task to the given task
		'''

		# get kwargs
		name = variables.kwargs('name', '', kwargs, shortName='n')
		task = variables.kwargs('task', None, kwargs, shortName='tsk')
		section = variables.kwargs('section', '', kwargs, shortName='s')
		index = variables.kwargs('index', None, kwargs, shortName='i')
		parent = variables.kwargs('parent', '', kwargs, shortName='p')

		# get section list
		if section.lower() == 'prebuild':
			section = self._preBuild
		elif section.lower() == 'build':
			section = self._build
		else:
			section = self._postbuild

		# get index
		if isinstance(index, basestring):
			if index in section:
				index = section.index(index)+1
			else:
				index = len(section)
		elif isinstance(index, int):
			pass
		else:
			index = len(section)

		# add to section
		section.insert(index, {'name': name,
							   'task': task,
							   'parent': parent})

	def registertion(self):
		'''
		register all the task to the builder
		'''
		pass


