#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import maya packages
import maya.cmds as cmds

## import utils
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
class NewScene(task.Task):
	"""create new scene"""
	def __init__(self):
		super(NewScene, self).__init__()
		self._task = 'dev.rigging.task.base.newScene'

	def pre_build(self):
		super(NewScene, self).pre_build()
		cmds.file(f=True, new=True)

