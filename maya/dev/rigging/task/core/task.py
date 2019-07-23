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

## import PySide widgets
try:
	from PySide2.QtWidgets import *
except ImportError:
	from PySide.QtGui import *

## import utils
import utils.common.variables as variables
import dev.rigging.utils.kwargsUtils as kwargsUtils
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

		self.register_attributes(**kwargs)

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

	def register_attributes(self, **kwargs):
		self.register_kwargs()
		self.register_inputs(**kwargs)

	def register_kwargs(self):
		self._kwargs = {}
		self._kwargs_ui = OrderedDict()

	def register_float_attribute(self, name, attrName=None, shortName=None, value=None, 
								 minValue=None, maxValue=None, tip=None):
		'''
		add float attribute to task
		'''
		# set value if None
		if not value:
			value = 0.0
		# check range
		rangeValue = [minValue, maxValue]
		if minValue and maxValue and minValue > maxValue:
			rangeValue = [maxValue, minValue]
		if rangeValue[0] and rangeValue[0] > value:
			value = rangeValue[0]
		if rangeValue[1] and rangeValue[1] < value:
			value = rangeValue[1]

		kwargInfo_ui = {name: {'value': float(value),
							   'min': rangeValue[0],
							   'max': rangeValue[1],
							   'tip': tip,
							   'widget': QDoubleSpinBox}}
		self._register_custom_attribute([name, float(value), attrName, shortName], kwargInfo_ui)

	def register_int_attribute(self, name, attrName=None, shortName=None, value=None, 
							   minValue=None, maxValue=None, tip=None):
		'''
		add int attribute to task
		'''
		# set value if None
		if not value:
			value = 0
		# check range
		rangeValue = [minValue, maxValue]
		if minValue and maxValue and minValue > maxValue:
			rangeValue = [maxValue, minValue]
		if rangeValue[0] and rangeValue[0] > value:
			value = rangeValue[0]
		if rangeValue[1] and rangeValue[1] < value:
			value = rangeValue[1]

		kwargInfo_ui = {name: {'value': int(value),
							   'min': rangeValue[0],
							   'max': rangeValue[1],
							   'tip': tip,
							   'widget': QSpinBox}}

		self._register_custom_attribute([name, int(value), attrName, shortName], kwargInfo_ui)

	def register_string_attribute(self, name, attrName=None, shortName=None, value='', 
								  select=True, tip=None):
		'''
		add string attribute to task
		'''

		kwargInfo_ui = {name: {'value': str(value),
							   'select': select,
							   'tip': tip,
							   'widget': QLineEdit}}
							   
		self._register_custom_attribute([name, str(value), attrName, shortName], kwargInfo_ui)

	def register_bool_attribute(self, name, attrName=None, shortName=None, value=False,
								tip=None):
		'''
		add bool attribute to task
		'''
		# set value

		kwargInfo_ui = {name: {'value': value,
							   'widget': QComboBox}}

		self._register_custom_attribute([name, value, attrName, shortName], kwargInfo_ui)

	def register_enum_attribute(self, name, attrName=None, shortName=None, value=None, 
								enum=[], tip=None):
		'''
		add enum attribute to task
		'''

		kwargInfo_ui = {name: {'value': value,
							   'enum': enum,
							   'widget': QComboBox}}

		self._register_custom_attribute([name, value, attrName, shortName], kwargInfo_ui)

	def register_list_attribute(self, name, attrName=None, shortName=None, value=[], 
								select=True, template='', tip=None):
		'''
		add list attribute to task
		'''

		kwargInfo_ui = {name: {'value': value,
							   'select': select,
							   'template': template,
							   'widget': QLineEdit}}

		self._register_custom_attribute([name, value, attrName, shortName], kwargInfo_ui)

	def register_inputs(self, **kwargs):
		for key, val in self._kwargs.iteritems():
			attrVal = variables.kwargs(val[0], val[1], kwargs, shortName=val[2])
			self.__setattr__(key, attrVal)

	def _register_custom_attribute(self, kwargInfo, kwargInfo_ui):
		'''
		add custom attribute to task
		'''
		if not kwargInfo[2]:
			key = kwargInfo[0]
		else:
			key = kwargInfo[2]

		self._kwargs.update({key: [kwargInfo[0], kwargInfo[1], kwargInfo[3]]})

		self._kwargs_ui.update(kwargInfo_ui)

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

