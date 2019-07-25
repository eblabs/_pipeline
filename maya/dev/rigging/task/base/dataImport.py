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
class DataImport(task.Task):
	"""
	base class for dataImport
	
	used for tasks need import data from path
	(misc, model etc)
	
	Kwargs:
		data(list): list of data path
		type(list): list of data type

	"""
	def __init__(self, **kwargs):
		super(DataImport, self).__init__(**kwargs)
		self._task = 'dev.rigging.task.base.dataImport'

	def register_kwargs(self):
		super(DataImport, self).register_kwargs()

		self.register_attribute('data', [], attrName='dataPath', shortName='d',
								select=False, template='str',
								hint='import data from following paths')


		self.register_attribute('type', ['ma', 'mb', 'obj'], attrName='fileExt',
								select=False, template='str',
								hint='import following type of data')

	def get_data(self):
		self._data = []
		for path in self.dataPath:
			if os.path.isfile(path):
				# check extension
				ext = os.path.splitext(path)[-1].lower()
				if ext in self.fileExt and path not in self._data:
					self._data.append(path)
			elif os.path.isdir(path):
				filePaths = files.get_files_from_path(path, extension=self.fileExt)
				for p in filePaths:
					if p not in self._data:
						self._data.append(p)

	def import_data(self):
		for f in self._data:
			cmds.file(f, i=True)

	def pre_build(self):
		super(DataImport, self).pre_build()
		self.get_data()
		self.import_data()