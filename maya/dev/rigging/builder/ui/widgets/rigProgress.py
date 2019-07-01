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

#=================#
#      CLASS      #
#=================#
class RigProgress(QProgressBar):
	"""ProgressBar widget"""
	def __init__(self):
		super(RigProgress, self).__init__()
		
		self._pause = False
		self._error = False

		self.init_widget()

	def init_widget(self):
		self.setTextVisible(True)
		self._palette = QPalette()
		self._palette.setColor(QPalette.Highlight, 
						 	   QColor(0,161,62))
		self._palette.setColor(QPalette.Text, 
						 	   QColor(Qt.white))
		self._palette.setColor(QPalette.HighlightedText, 
						 	   QColor(Qt.black))
		self.setPalette(self._palette)
		self.setRange(0,100)

	def set_color(self):
		if self._error:
			# set to red
			self._palette.setColor(QPalette.Highlight, 
							 	   QColor(250, 40, 71))
		elif self._pause:
			# set to blue
			self._palette.setColor(QPalette.Highlight, 
						 	   QColor(77, 193, 232))
		else:
			# set to green
			self._palette.setColor(QPalette.Highlight, 
						 	   QColor(0,161,62))
		
		self.setPalette(self._palette)

