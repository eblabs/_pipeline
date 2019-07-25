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


#=================#
#      CLASS      #
#=================#
class TestTask(task.Task):
	"""
	base class for testing

	"""
	def __init__(self, **kwargs):
		super(TestTask, self).__init__(**kwargs)
		self._task = 'dev.rigging.task.test.testTask'

	def register_kwargs(self):
		super(TestTask, self).register_kwargs()
		self.register_attribute('data', [], attrName='dataPath', shortName='d',
								select=False, template='str',
								hint='load data from following paths')

		self.register_attribute('joints', 5, attrName='jntNum', shortName='j',
								min=1, max=10, hint='joints number')

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