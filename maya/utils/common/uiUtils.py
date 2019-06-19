#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import OpenMayaUI
## maya doesn't have MQtUtil in api 2.0
import maya.OpenMayaUI as OpenMayaUI

## import PySide
try:
	from PySide2 import QtCore, QtGui
	from shiboken2 import wrapInstance 
except ImportError:
	from PySide import QtCore, QtGui
	from shiboken import wrapInstance

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#
class BaseWindow(QtGui.QWidget):
	"""class for Base Window in maya"""
	def __init__(self, **kwargs):
		super(BaseWindow, self).__init__()
		
		# get kwargs
		_parent = kwargs.get('parent', None)
		_title = kwargs.get('title', 'Window')
		_geo = kwargs.get('geometry', [100,100,100,100])
		
		# parent widget
		self.setParent(_parent)
		self.setWindowFlags(QtCore.Qt.Window)

		# set the object name
		self.setObjectName(_title.replace(' ', '') + '_uniqueId')
		self.setWindowTitle(_title)
		self.setGeometry(_geo[0], _geo[1], _geo[2], _geo[3])

		# initialize UI
		self.init_UI()	

	def init_UI(self):
		pass

#=================#
#    FUNCTION     #
#=================#
def get_maya_window():
	ptr = OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(ptr), QtGui.QMainWindow)
