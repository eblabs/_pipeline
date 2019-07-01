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
class DataImport(task.Task):
	"""
	base class for dataImport
	
	used for tasks need import data from path
	(misc, model etc)
	
	Kwargs:
		data(list): list of data path

	"""
	def __init__(self, **kwargs):
		super(DataImport, self).__init__(**kwargs)
		self._task = TASK_PATH+'.dataImport'
		self._fileExt = ['ma', 'mb', 'obj']

	def register_kwargs(self):
		super(DataImport, self).register_kwargs()
		self.register_single_kwargs('data', 
									shortName='d', 
									attributeName='dataPath', 
									uiKwargs={'type': 'strPath'})

	def get_data(self):
		self._data = []
		for path in self._dataPath:
			if os.path.isfile(path):
				# check extension
				ext = os.path.splitext(path)[-1].lower()
				if ext in self._fileExt and path not in self._data:
					self._data.append(path)
			elif os.path.isdir(path):
				filePaths = files.get_files_from_path(path, extension=self._fileExt)
				for p in filePaths:
					if p not in self._data:
						self._data.append(p)

	def import_data(self):
		for f in self._data:
			cmds.file(f, i=True)

	def run(self):
		super(DataImport, self).run()
		self.get_data()
		self.import_data()