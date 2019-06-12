#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import maya packages
import maya.cmds as cmds

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger, TASK_PATH

#=================#
#      CLASS      #
#=================#
class Task(object):
	"""base class for Task"""
	def __init__(self, **kwargs):
		super(Task, self).__init__()
		self._name = 'task'
		self._task = TASK_PATH+'.task'
		
		self.register_attributes(kwargs)

	@ property
	def name(self):
		return self._name

	@ property
	def task(self):
		return self._task

	@name.setter
	def name(self, taskName):
		self._name = taskName
	
	def register_attributes(self, kwargs):
		self.register_kwargs()
		self.register_inputs(kwargs)

	def register_kwargs(self):
		self._kwargs = {}

	def register_inputs(self, kwargs):
		for key, val in self._kwargs.iteritems():
			if len(val) > 2:
				shortName = val[2]
			else:
				shortName = None
			attrVal = variables.kwargs(val[0], val[1], kwargs, shortName=shortName)
			self.__setattr__('_'+key, attrVal)

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

