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
		self._data = []
		self._tasks = {}
		self._hierarchy = []
		
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
		_taskInfo = {_name: {'task': _task,
							 'parent': _parent,
							 'kwargs': _kwargs}}

		# get index
		if isinstance(_index, basestring):
			for i, t in enumerate(self._data):
				key = t.keys()[0]
				if _index == key:
					_index = i+1
					break
			if isinstance(_index, basestring):
				_index = len(self._data)

		self._data.insert(_index, _taskInfo)
		self._tasks.update({_name: {'task': _task,
									'kwargs': _kwargs}})

	def registertion(self):
		'''
		register all the task to the builder
		'''
		pass

	def _insert_child(self, tree, data):
		'''
		insert child to parent task as a tree hierarchy
		'''
		key = data.keys()[0]
		item = data[key]
		if 'parent' in item and item['parent']:
			parentTask = item['parent']
			for treeData in tree:
				keyTree = treeData.keys()[0]
				itemTree = treeData[keyTree]
				if parentTask == keyTree:
					itemTree['children'].append({key: {'children': []}})
					return True
				else:
					isParent = get_child(itemTree['children'], data)
					if isParent:
						return True
		else:
			tree.append({key: {'children': []}})

	def _build_task_tree(self):
		'''
		build task tree hierarchy
		'''
		for d in self._data:
			self._insert_child(self._hierarchy, d)




