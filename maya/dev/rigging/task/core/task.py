#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import OrderedDict
from collections import OrderedDict 

## import PySide widgets
try:
	from PySide2.QtWidgets import *
except ImportError:
	from PySide.QtGui import *

## import utils
import utils.common.variables as variables
import utils.common.logUtils as logUtils

#=================#
#   GLOBAL VARS   #
#=================#
logger = logUtils.get_logger()

# property items
import dev.rigging.task
PROPERTY_ITEMS = dev.rigging.task.PROPERTY_ITEMS

#=================#
#      CLASS      #
#=================#
class Task(object):
	"""base class for Task"""
	def __init__(self, **kwargs):
		super(Task, self).__init__()
		self._name = 'task'
		self._task = 'dev.rigging.task.core.task'

		self.register_attrs(**kwargs)

	@ property
	def name(self):
		return self._name

	@ property
	def task(self):
		return self._task

	@name.setter
	def name(self, taskName):
		self._name = taskName

	def pre_build(self):
		pass

	def build(self):
		pass

	def post_build(self):
		pass	

	def register_attrs(self, **kwargs):
		self.register_kwargs()
		self.register_inputs(**kwargs)

	def register_kwargs(self):
		self._kwargs = {}
		self._kwargs_ui = OrderedDict()

	def register_inputs(self, **kwargs):
		for key, val in self._kwargs.iteritems():
			attrVal = variables.kwargs(val[0], val[1], kwargs, shortName=val[2])
			self.__setattr__(key, attrVal)

	def register_attribute(self, name, value, attrName=None, shortName=None, attrType=None, **kwargs):
		'''
		register attribute to the task, and ui will pick up the infomation

		Args:
			name(str): attribute name in kwargs
			value: attribute value (function read type by the value, don't use None)
		Kwargs:
			attrName(str): attribute name in class
			shortName(str): attribute short name
			attrType(str): if it has more complicate ui info need from PROPERTY_ITEMS
			min(float/int): min value
			max(float/int): max value
			select(bool): if right click can add/set selection
			enum(list): enum options
			template: list/dict childs template
			hint(str): attribute's hint
		'''
		if not attrType:
			if value in [True, False]:
				attrType = 'bool'
			elif isinstance(value, float):
				attrType = 'float'
			elif isinstance(value, int):
				attrType = 'int'
			elif isinstance(value, list):
				attrType = 'list'
			elif isinstance(value, dict):
				attrType = 'dict'
			elif isinstance(value, basestring):
				attrType = 'str'

		kwargInfo_ui = PROPERTY_ITEMS[attrType].copy()
		kwargInfo_ui.update(kwargs)

		if attrType in ['float', 'int']:
			rangeValue = [kwargInfo_ui['min'], kwargInfo_ui['max']]
			if rangeValue[0] != None and rangeValue[1] != None:
				rangeValue.sort()
				kwargInfo_ui['min'] = rangeValue[0]
				kwargInfo_ui['max'] = rangeValue[1]

			if rangeValue[0] != None and rangeValue[0] > value:
				value = rangeValue[0]
			if rangeValue[1] != None and rangeValue[1] < value:
				value = rangeValue[1]

		kwargInfo_ui['value'] = value

		self._register_attr_to_task([name, value, attrName, shortName], kwargInfo_ui)

	def _register_attr_to_task(self, kwargInfo, kwargInfo_ui):
		'''
		add custom attribute to task
		'''
		if not kwargInfo[2]:
			key = kwargInfo[0]
		else:
			key = kwargInfo[2]

		self._kwargs.update({key: [kwargInfo[0], kwargInfo[1], kwargInfo[3]]})

		self._kwargs_ui.update({kwargInfo[0]:kwargInfo_ui})

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

