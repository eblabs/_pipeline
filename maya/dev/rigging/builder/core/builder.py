#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import inspect
import inspect

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
		_display = variables.kwargs('display', '', kwargs, shortName='dis')
		_task = variables.kwargs('task', None, kwargs, shortName='tsk')
		_index = variables.kwargs('index', len(self._tasks), kwargs, shortName='i')
		_parent = variables.kwargs('parent', '', kwargs, shortName='p')
		_kwargs = variables.kwargs('kwargs', {}, kwargs)
		_section = variables.kwargs('section', 'post', kwargs)
		if 'pre' in _section.lower():
			_section = 'pre'
		elif 'post' in _section.lower():
			_section = 'post'
		else:
			_section = 'build'

		if not _display:
			_display = _name

		# get task
		if inspect.ismethod(_task):
			# in class method, get method name for ui display
			_taskName = _task.__name__
			_taskKwargs = _kwargs
		else:
			# imported task, get task object
			_taskName = _task
			taskImport, taskFunc = modules.import_module(_task)
			_task = getattr(taskImport, taskFunc)
			_taskKwargs = _task()._kwargs_ui
			for key, item in _kwargs.iteritems():
				_taskKwargs.update({key: item})

		# add task info to class as attribute
		_taskInfo = {'task': _task,
					 'taskName': _taskName,
					 'display': _display,
					 'taskKwargs': _taskKwargs,
					 'parent': _parent,
					 'section': _section}

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
		taskInfo_add = {task:{'task': taskInfo['task'],
							  'taskName': taskInfo['taskName'],
						 	  'display': taskInfo['display'],
						 	  'taskKwargs': taskInfo['taskKwargs'],
						 	  'section': taskInfo['section'],
							  'children': []}}
		if parent:
			for hieInfo in hierarchy:
				key = hieInfo.keys()[0]
				if parent == key:
					hieInfo[parent]['children'].append(taskInfo_add)
					return True
				else:
					isParent = self._add_child(hieInfo[key]['children'], task)
		else:
			hierarchy.append(taskInfo_add)

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


