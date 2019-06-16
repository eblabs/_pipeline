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
import utils.common.modules as modules
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
class Builder(object):
	"""
	base template for all the build script
	"""
	def __init__(self):
		super(Builder, self).__init__()
		self._tasks = []
		
	def register_task(self, **kwargs):
		'''
		register task to build script

		Kwargs:
			name(str): task name
			task(method): task function
			index(str/int): register task at specific index
							if given string, it will register after the given task
			parent(str): parent task to the given task
			kwargs(dict): task kwargs
		'''

		# get kwargs
		_name = variables.kwargs('name', '', kwargs, shortName='n')
		_task = variables.kwargs('task', None, kwargs, shortName='tsk')
		_index = variables.kwargs('index', None, kwargs, shortName='i')
		_parent = variables.kwargs('parent', '', kwargs, shortName='p')
		_kwargs = variables.kwargs('kwargs', {}, kwargs)

		# add to task list
		_taskInfo = {'name': {'task': _task,
							  'index': _index,
							  'parent': _parent,
							  'kwargs': _kwargs}}
		self._tasks.append(_taskInfo)

	def registertion(self):
		'''
		register all the task to the builder
		'''
		pass



