## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI
import os
try:
	from PySide import QtGui
	from PySide import QtCore
	from shiboken import wrapInstance
except:
	from PyQt4 import QtGui
	from PyQt4 import QtCore
	from sip import wrapinstance as wrapInstance

## libs Import
import workspaces

## Assets Manager UI
class assetsManagerUI(QtGui.QWidget):
	"""docstring for assetsManagerUI"""
	def __init__(self, sParent = None):
		super(assetsManagerUI, self).__init__()
		
		#Parent widget under Maya main window        
		self.setParent(sParent)       
		self.setWindowFlags(QtCore.Qt.Window)

		#Set the object name     
		self.setObjectName('assetsManager_uniqueId')        
		self.setWindowTitle('Assets Manager')        
		self.setGeometry(100, 100, 600, 300) 
		self.initUI()  

	def initUI(self):
		QLayout = QtGui.QHBoxLayout(self)
		self.setLayout(QLayout)

		#Project Layout
		QLayout_project = QtGui.QVBoxLayout()
		QLayout.addLayout(QLayout_project)

		## create/check out button
		QLayout_projectButton = QtGui.QHBoxLayout()
		QLayout_project.addLayout(QLayout_projectButton)

		btn = QtGui.QPushButton('New Project')
		QLayout_projectButton.addWidget(btn)
		btn = QtGui.QPushButton('Check out')
		QLayout_projectButton.addWidget(btn)

		## Projects List
		QLayout_projectList = QtGui.QVBoxLayout()
		QLayout_project.addLayout(QLayout_projectList)

		label = QtGui.QLabel('Projects:')
		QLayout_projectList.addWidget(label)
		


## Functions
def getMayaWindow():
	ptr = OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(ptr), QtGui.QMainWindow)

