#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import utils
import utils.common.files as files
import utils.common.logUtils as logUtils

## import task
import dev.rigging.task.core.task as task

#=================#
#   GLOBAL VARS   #
#=================#
logger = logUtils.get_logger()

#=================#
#      CLASS      #
#=================#
class DataLoad(task.Task):
	"""
	base class for dataLoad
	
	used for tasks need load data from files
	(deformers, controlShapes etc)

	all tasks with load data function should inherit from this class
	
	self._dataType(str): json/numpy/cPickle
						 determine which load function to use

	Kwargs:
		data(list): list of data path

	"""
	def __init__(self, **kwargs):
		super(DataLoad, self).__init__(**kwargs)
		self._task = 'dev.rigging.task.base.dataLoad'
		self._dataType = 'json'

	def register_kwargs(self):
		super(DataLoad, self).register_kwargs()

		self.register_attribute('data', [], attrName='dataPath', shortName='d',
								select=False, template='str',
								hint='load data from following paths')

	def get_load_method(self):
		if self._dataType == 'json':
			self.loadMethod = files.read_json_file
		elif self._dataType == 'numpy':
			self.loadMethod = files.read_numpy_file
		elif self._dataType == 'cPickle':
			self.loadMethod = files.read_cPickle_file

	def get_data(self):
		self._data = {}
		for path in self.dataPath:
			dataLoad = self.loadMethod(path)
			for key, item in dataLoad.iteritems():
				if key not in self._data:
					self._data.update({key: item})

	def pre_build(self):
		super(DataLoad, self).pre_build()
		self.get_load_method()
		self.get_data()



