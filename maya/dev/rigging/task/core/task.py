#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import OrderedDict
from collections import OrderedDict 

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.variables as variables

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

	def run(self):
		pass

	def register_kwargs(self):
		self._kwargs = {}
		self._kwargs_ui = OrderedDict()

	def register_single_kwargs(self, longName, **kwargs):
		'''
		Args:
			longName(str): kwarg key name
		Kwargs:	
			shortName(str)[None]: kwarg short name
			defaultValue[None]: default value
			attributeName(str)['']: attribute name in class, will use longName if not any
			uiKwargs(dict)[{}]: kwargs for ui base on PROPERTY_ITEMS.py
		'''
		shortName = kwargs.get('shortName', '')
		defaultVal = kwargs.get('defaultValue', None)
		attrName = kwargs.get('attributeName', '')
		uiKwargs = kwargs.get('uiKwargs', {})

		kwargInfo, kwargInfo_ui = variables.register_single_kwarg(longName, defaultValue=defaultVal, 
								  shortName=shortName, attributeName=attrName, uiKwargs=uiKwargs)
		
		self._kwargs.update(kwargInfo)
		self._kwargs_ui.update(kwargInfo_ui)

	def register_inputs(self, kwargs):
		for key, val in self._kwargs.iteritems():
			attrVal = variables.kwargs(val[0], val[1], kwargs, shortName=val[2])
			setattr(self, '_'+key, attrVal)

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

