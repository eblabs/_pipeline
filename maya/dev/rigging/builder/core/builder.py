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
		self._taskInfos = {}
		
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
		_index = variables.kwargs('index', len(self._tasks), kwargs, shortName='i')
		_parent = variables.kwargs('parent', '', kwargs, shortName='p')
		_kwargs = variables.kwargs('kwargs', {}, kwargs)

		# add task info to class as attribute
		_taskInfo = {'Task': _task,
					 'kwargs': _kwargs,
					 'parent': _parent}
		# import module
		if isinstance(_task, basestring):
			taskImport, taskFunc = modules.import_module(_task)
			_Task = getattr(taskImport, taskFunc)
			_taskInfo['Task'] = _Task

		self._taskInfos.update({_name: _taskInfo})

		# get index
		if isinstance(_index, basestring):
			if _index in self._tasks:
				_index = self._tasks.index(_index) + 1

		self._tasks.insert(_index, _name)

	def registertion(self):
		'''
		register all the task to the builder
		'''
		pass

	def tree_hierarchy(self):
		hierarchy = []
		for task in self._tasks:
			self._add_child(hierarchy, task)
		return hierarchy

	def _add_child(self, hierarchy, task):
		taskInfo = self._get_task_info(task)
		parent = taskInfo['parent']
		if parent:
			for hieInfo in hierarchy:
				key = hieInfo.keys()[0]
				if parent == key:
					hieInfo[parent]['children'].append({task: {'children': []}})
					return True
				else:
					isParent = self._add_child(hieInfo[key]['children'], task)
		else:
			hierarchy.append({task:{'children': []}})

	def _get_task_info(self, task):
		taskInfo = self._taskInfos[task]
		return taskInfo

	def _add_attr_from_dict(self, attrDict):
		'''
		add class attributes from given dictionary
		'''
		for key, val in attrDict.iteritems():
			setattr(self, key, val)

	def _add_obj_attr(self, attr, attrDict):
		attrSplit = attr.split('.')
		attrParent = self
		if len(attrSplit) > 1:
			for a in attrSplit[:-1]:
				attrParent = getattr(attrParent, a)
		setattr(attrParent, attrSplit[-1], Objectview(attrDict))

#=================#
#    SUB CLASS    #
#=================#

class Objectview(object):
	def __init__(self, kwargs):
		self.__dict__ = kwargs


