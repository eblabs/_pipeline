#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os
import time
## import maya packages
import maya.cmds as cmds

## import task
import dev.rigging.task.core.task as task

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger, TASK_PATH

#=================#
#      CLASS      #
#=================#
class TestTask(task.Task):
	"""
	base class for testing

	"""
	def __init__(self, **kwargs):
		super(TestTask, self).__init__(**kwargs)
		self._task = TASK_PATH+'.testTasl'

	def register_kwargs(self):
		super(TestTask, self).register_kwargs()
		self.register_single_kwargs('data', 
									shortName='d', 
									attributeName='dataPath', 
									uiKwargs={'type': 'strPath'})

		self.register_single_kwargs('joints', 
									shortName='j', 
									attributeName='jntNum', 
									uiKwargs={'type': 'int',
											  'min': 1,
											  'max': 10})

	def pre_build(self):
		super(TestTask, self).pre_build()
		print '--------- Test Task Pre Build ---------'
		for i in range(10):
			time.sleep(0.1)
			print i

	def build(self):
		super(TestTask, self).build()
		print '--------- Test Task Build ---------'
		for i in range(10):
			time.sleep(0.1)
			print i

	def post_build(self):
		super(TestTask, self).post_build()
		print '--------- Test Task Post Build ---------'
		for i in range(10):
			time.sleep(0.1)
			print i