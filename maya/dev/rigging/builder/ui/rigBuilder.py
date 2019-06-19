#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.uiUtils as uiUtils

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#

class RigBuilder(uiUtils.BaseWindow):
	"""class for RigBuilder UI"""
	def __init__(self, **kwargs):
		super(RigBuilder, self).__init__(**kwargs)
		
	def init_UI(self):
		super(RigBuilder, self).init_UI()
		