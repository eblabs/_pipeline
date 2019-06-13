#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.files as files

## import task
import task

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger, TASK_PATH

#=================#
#      CLASS      #
#=================#
class DataLoad(task.Task):
	"""
	base class for dataLoad
	
	used for tasks need load data from files
	(deformers, controlShapes etc)
	
	self._dataType(str): json/numpy/cPickle
						 determine which load function to use

	Kwargs:
		data(list): list of data path

	"""
	def __init__(self, **kwargs):
		super(DataLoad, self).__init__(**kwargs)
		self._task = TASK_PATH+'.dataLoad'
		self._dataType = 'json'

	def register_kwargs(self):
		super(DataLoad, self).register_kwargs()
		self._kwargs.update({'dataPath': {'data', [], 'd'}})

	def get_load_method(self):
		if self._dataType == 'json':
			self.loadMethod = files.read_json_file
		elif self._dataType == 'numpy':
			self.loadMethod = files.read_numpy_file
		elif self._dataType == 'cPickle':
			self.loadMethod = files.read_cPickle_file

	def get_data(self):
		self._data = {}
		for path in self._dataPath:
			dataLoad = self.loadMethod(path)
			for key, item in dataLoad.iteritems():
				if key not in self._data:
					self._data.update({key: item})

	def run(self):
		super(DataLoad, self).run()
		self.get_load_method()
		self.get_data()



