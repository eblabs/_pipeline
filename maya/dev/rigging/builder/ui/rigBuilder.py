#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import PySide
try:
	from PySide2.QtCore import *
	from PySide2.QtGui import *
	from PySide2.QtWidgets import *
	from PySide2 import __version__
	from shiboken2 import wrapInstance
except ImportError:
	from PySide.QtCore import *
	from PySide.QtGui import *
	from PySide import __version__
	from shiboken import wrapInstance

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.uiUtils as uiUtils

## import widgets
import widgets.treeWidget as treeWidget
import widgets.propertyEditor as propertyEditor
import widgets.buttonShelf as buttonShelf

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
		'''
		rig builder layout
		'''

		# base layout
		layout_base = QHBoxLayout(self)
		self.setLayout(layout_base)

		# left frame
		frame_left = QFrame(layout_base)
		frame_left.setFixedWidth(300)

		# left layout
		layout_left = QVBoxLayout(frame_left)



		