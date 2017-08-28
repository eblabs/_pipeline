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
		QLayout_projectList, QSourceModel_project, self.QProxyModel_project, self.QFilterEdit_project, self.QListView_project = self._setBaseLayout('Projects')
		self.rebuildListModel(QSourceModel_project, workspaces.sPathLocal, sType = 'folder')
		self.QFilterEdit_project.textChanged.connect(self._filterRegExpChanged_project)
		self.QListView_project.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.QListView_project.connect(self.QListView_project, QtCore.SIGNAL("customContextMenuRequested(QPoint)" ), self.listItemRightClicked_project)
		## Asset
		QLayout_assetList, self.QSourceModel_asset, self.QProxyModel_asset, self.QFilterEdit_asset, self.QListView_asset = self._setBaseLayout('Assets')
		QSelectionModel_asset = self.QListView_project.selectionModel()
		QSelectionModel_asset.currentChanged.connect(self.listItemClick_asset)
		self.QFilterEdit_asset.textChanged.connect(self._filterRegExpChanged_asset)

	def rebuildListModel(self, QModel, sPath, sType = 'folder'):
		QModel.clear()
		lFiles = files.getFilesFromPath(sPath, sType = sType)
		if len(lFiles) > 1: lFiles.sort()
		for sFile in lFiles:
			sFile_item = QtGui.QStandardItem(sFile)
			QModel.appendRow(sFile_item)

	def listItemClick_asset(self):
		currentItem = self.QListView_project.currentIndex().data()
		if currentItem:
			sPath = os.path.join(workspaces.sPathLocal, str(currentItem))
			sPath = os.path.join(sPath, 'assets')
			if os.path.exists(sPath):
				self.rebuildListModel(self.QSourceModel_asset, sPath)
			else:
				self.QSourceModel_asset.clear()
		else:
			self.QSourceModel_asset.clear()

	def listItemRightClicked_project(self, QPos):
		QListMenu= QtGui.QMenu(self)
		QMenuItem_create = QListMenu.addAction("Create")
		QMenuItem_rename = QListMenu.addAction("Rename")
		QMenuItem_delete = QListMenu.addAction("Delete")
		#self.connect(menu_item_rename, QtCore.SIGNAL("triggered()"), self.renameItem) 
		#self.connect(menu_item_delete, QtCore.SIGNAL("triggered()"), self.menuItemClicked) 

		parentPosition = self.QListView_project.mapToGlobal(QtCore.QPoint(0, 0))        
		QListMenu.move(parentPosition + QPos)

		try:
			currentItem = self.QListView_project.currentIndex().data()
			if not currentItem:
				QMenuItem_rename.setEnabled(False)
				QMenuItem_delete.setEnabled(False)			
			QListMenu.show() 
		except:
			pass

	def _setBaseLayout(self, sName, bFilter = True):
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

		#QListView = QtGui.QListView()
		QListView = fileListView()
		if bFilter:
			QListView.setModel(QProxyModel)
		else:
			QListView.setModel(QSourceModel)
		QLayout_list.addWidget(QListView)

		return QLayout_list, QSourceModel, QProxyModel, QFilterEdit, QListView

	def _filterRegExpChanged_project(self):
		regExp = QtCore.QRegExp(self.QFilterEdit_project.text(), QtCore.Qt.CaseInsensitive)
		self.QProxyModel_project.setFilterRegExp(regExp)

	def _filterRegExpChanged_asset(self):
		regExp = QtCore.QRegExp(self.QFilterEdit_asset.text(), QtCore.Qt.CaseInsensitive)
		self.QProxyModel_asset.setFilterRegExp(regExp)

## List widget
class fileListView(QtGui.QListView):
	def __init__(self, parent=None):
		super(fileListView, self).__init__(parent)

	def keyPressEvent(self, event):
		if (event.key() == QtCore.Qt.Key_Escape and
			event.modifiers() == QtCore.Qt.NoModifier):
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		else:
			QtGui.QListView.keyPressEvent(self, event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		QtGui.QListView.mousePressEvent(self, event)

## Functions
def getMayaWindow():
	ptr = OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(ptr), QtGui.QMainWindow)

