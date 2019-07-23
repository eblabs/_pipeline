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
class Callback(task.Task):
	"""
	base class for callback
	
	used for tasks need callback
	
	self.builder: pass the builder object so the vars can be used

	Kwargs:
		preBuild(str): pre build section code
		build(str): build section code
		postBuild(str): post build section code

	"""
	def __init__(self, **kwargs):
		super(Callback, self).__init__(**kwargs)
		self._task = TASK_PATH+'.callback'
		self.builder = None

	def register_kwargs(self):
		super(Callback, self).register_kwargs()
		self.register_single_kwargs('preBuild', 
									shortName='pre', 
									attributeName='callback_pre', 
									uiKwargs={'type': 'callback'})

		self.register_single_kwargs('build',
									attributeName='callback_build', 
									uiKwargs={'type': 'callback'})

		self.register_single_kwargs('postBuild', 
									shortName='post', 
									attributeName='callback_post', 
									uiKwargs={'type': 'callback'})

	def pre_build(self):
		super(Callback, self).pre_build()
		if self._callback_pre:
			exec(self._callback_pre)

	def build(self):
		super(Callback, self).build()
		if self._callback_build:
			exec(self._callback_build)

	def post_build(self):
		super(Callback, self).post_build()
		if self._callback_post:
			exec(self._callback_post)



