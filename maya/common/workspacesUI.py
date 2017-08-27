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
import files
reload(files)
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
		self.QLayoutBase = QtGui.QHBoxLayout(self)
		self.setLayout(self.QLayoutBase)

		## Project
		QLayout_projectList, QSourceModel_project, self.QProxyModel_project, self.QFilterEdit_project = self.setBaseLayout('Projects')
		self.rebuildListModel(QSourceModel_project, workspaces.sPathLocal, sType = 'folder')
		self.QFilterEdit_project.textChanged.connect(self.filterRegExpChanged_project)

		## Asset
		QLayout_assetList, QSourceModel_asset, self.QProxyModel_asset, self.QFilterEdit_asset = self.setBaseLayout('Assets')


	def setBaseLayout(self, sName, bFilter = True):
		#Layout
		QLayout = QtGui.QVBoxLayout()
		self.QLayoutBase.addLayout(QLayout)

		##List Layout
		QLayout_list = QtGui.QVBoxLayout()
		QLayout.addLayout(QLayout_list)

		label = QtGui.QLabel('%s:' %sName)
		QLayout_list.addWidget(label)

		#### filter
		if bFilter:
			QFilterEdit = QtGui.QLineEdit()
			QLayout_list.addWidget(QFilterEdit)
		else:
			QFilterEdit = None
		#### List
		QSourceModel = QtGui.QStandardItemModel()
		if bFilter:
			QProxyModel = QtGui.QSortFilterProxyModel()
			QProxyModel.setDynamicSortFilter(True)
			QProxyModel.setSourceModel(QSourceModel)
		else:
			QProxyModel = None

		QListView = QtGui.QListView()
		if bFilter:
			QListView.setModel(QProxyModel)
		else:
			QListView.setModel(QSourceModel)
		QLayout_list.addWidget(QListView)

		return QLayout_list, QSourceModel, QProxyModel, QFilterEdit

	def rebuildListModel(self, QModel, sPath, sType = 'folder'):
		lFiles = files.getFilesFromPath(sPath, sType = sType)
		if len(lFiles) > 1: lFiles.sort()
		for sFile in lFiles:
			sFile_item = QtGui.QStandardItem(sFile)
			QModel.appendRow(sFile_item)

	def filterRegExpChanged_project(self):
		regExp = QtCore.QRegExp(self.QFilterEdit_project.text(), QtCore.Qt.CaseInsensitive)
		self.QProxyModel_project.setFilterRegExp(regExp)

## List widget
class fileListView(QtGui.QListView):
	def __init__(self, type, parent=None):
		super(fileListView, self).__init__(parent)

## Functions
def getMayaWindow():
	ptr = OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(ptr), QtGui.QMainWindow)

