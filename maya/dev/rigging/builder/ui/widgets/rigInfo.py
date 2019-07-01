#=================#
# IMPORT PACKAGES #
#=================#

# import system packages
import sys
import os

# import PySide
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

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

TT_PROJECT = 'Set Project'
TT_ASSET = 'Set Asset'
TT_RIG = 'Set Rig Type'

#=================#
#      CLASS      #
#=================#
class RigInfo(QWidget):
	"""
	class for rig info widget
	
	user use this widget to get rig info for building
	"""
	def __init__(self):
		super(RigInfo, self).__init__()
		
		self.init_widget()

	def init_widget(self):
		layout_base = QVBoxLayout()
		self.setLayout(layout_base)

		for section, tip in zip(['project', 'asset', 'rig'],
								[TT_PROJECT, TT_ASSET, TT_RIG]):
			# QLineEdit
			lineEdit_section = LineEdit(name=section, toolTip=tip)
			# add obj to class for further use
			setattr(self, 'lineEdit_'+section, lineEdit_section)

			# add section to base layout
			layout_base.addWidget(lineEdit_section)

		# so it won't focus on QLineEidt when startup
		self.setFocus()

		
class LineEdit(QLineEdit):
	"""lineEdit for each rig info section"""
	def __init__(self, name='', toolTip=''):
		super(LineEdit, self).__init__()
		
		self._name = name
		self._toolTip = toolTip

		self.init_widget()

	def init_widget(self):
		self.setFrame(False)
		self.setAlignment(Qt.AlignCenter)
		self.setStyleSheet('border-radius: 4px')
		self.setPlaceholderText(self._name.title())
		if self._toolTip:
			self.setToolTip(self._toolTip)

		