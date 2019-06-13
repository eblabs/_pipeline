#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

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
class NewScene(task.Task):
	"""create new scene"""
	def __init__(self):
		super(NewScene, self).__init__()
		self._task = TASK_PATH+'.newScene'

	def run(self):
		super(NewScene, self).run()
		cmds.file(f=True, new=True)

