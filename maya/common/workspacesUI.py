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
		self.setGeometry(100, 100, 1000, 500) 
		self.initUI()

	def initUI(self):
		QLayoutBase = QtGui.QHBoxLayout(self)
		self.setLayout(QLayoutBase)

		## Project Layout
		self.oLayout_project = assetsManagerBaseLayout(QLayoutBase)
		self.oLayout_project.initUI()
		self.oLayout_project.rebuildListModel()

		## Asset Layout
		self.oLayout_asset = assetsManagerBaseLayout(QLayoutBase)
		self.oLayout_asset.sName = 'Assets'
		self.oLayout_asset.oLayout = self.oLayout_project
		self.oLayout_asset.bListItemClick = True
		self.oLayout_asset.initUI()

		## File Layout
		self._fileLayout(QLayoutBase)
		
	def _fileLayout(self, QLayoutBase):
		QLayout = QtGui.QVBoxLayout()
		QLayoutBase.addLayout(QLayout)

		QLabel = QtGui.QLabel('File:')
		QLayout.addWidget(QLabel)

		## type enum
		QLayout_fileType = QtGui.QHBoxLayout()
		QLayout.addLayout(QLayout_fileType)
		self.QComboBox_file = QtGui.QComboBox()
		self.QComboBox_file.setMaximumWidth(80)
		#### add asset type
		for sType in files.lAssetTypes:
			self.QComboBox_file.addItem(sType.title())
		QLayout_fileType.addWidget(self.QComboBox_file)

		#### file
		self.QLabel_file = QtGui.QLabel()
		self.QLabel_file.setStyleSheet("border: 1px solid black;")
		QLayout_fileType.addWidget(self.QLabel_file)
		#self.QListView_file.setMaximumHeight(20)

		#### versions		
		self.QCheckBox_version = QtGui.QCheckBox('Versions')
		QLayout.addWidget(self.QCheckBox_version)

		self.QListView_version = fileListView()
		QLayout.addWidget(self.QListView_version)

		#### comment
		self.QLabel_comment = QtGui.QLabel()
		self.QLabel_comment.setStyleSheet("border: 1px solid black;")
		self.QLabel_comment.setMinimumHeight(80)
		self.QLabel_comment.setScaledContents(True)
		QLayout.addWidget(self.QLabel_comment)

		#### button
		self.QPushButton_open = QtGui.QPushButton('Open File')
		QLayout.addWidget(self.QPushButton_open)





		


## BaseLayout
class assetsManagerBaseLayout():
	def __init__(self, QLayoutBase):
		self.QLayoutBase = QLayoutBase
		self.QLayout = QtGui.QVBoxLayout()
		self.QLayoutBase.addLayout(self.QLayout)
		self.sName = 'Projects'
		self.bFilter = True
		self.sPath = workspaces.sPathLocal
		self.sType = 'folder'
		self.bListItemRightClick = True
		self.oLayout = None
		self.bListItemClick = False

	def initUI(self):
		self.setBaseLayout()
		
		if self.bListItemRightClick:
			self.QListView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
			self.QListView.connect(self.QListView, QtCore.SIGNAL("customContextMenuRequested(QPoint)" ), self._listItemRightClicked)

		if self.bListItemClick and self.oLayout:
			QSelectionModel = self.oLayout.QListView.selectionModel()
			QSelectionModel.currentChanged.connect(self._listItemClick)

	def setBaseLayout(self):
		QLabel = QtGui.QLabel('%s:' %self.sName)
		self.QLayout.addWidget(QLabel)

		#### filter
		self.QFilterEdit = QtGui.QLineEdit()
		self.QLayout.addWidget(self.QFilterEdit)

		#### List
		self.QSourceModel = QtGui.QStandardItemModel()
		self.QProxyModel = QtGui.QSortFilterProxyModel()
		self.QProxyModel.setDynamicSortFilter(True)
		self.QProxyModel.setSourceModel(self.QSourceModel)

		#QListView = QtGui.QListView()
		self.QListView = fileListView()
		self.QListView.setModel(self.QProxyModel)
		self.QLayout.addWidget(self.QListView)

		self.QFilterEdit.textChanged.connect(self._filterRegExpChanged)

	def rebuildListModel(self):
		self.QSourceModel.clear()
		lFiles = files.getFilesFromPath(self.sPath, sType = self.sType)
		if len(lFiles) > 1: lFiles.sort()
		for sFile in lFiles:
			sFile_item = QtGui.QStandardItem(sFile)
			self.QSourceModel.appendRow(sFile_item)

	def _filterRegExpChanged(self):
		regExp = QtCore.QRegExp(self.QFilterEdit.text(), QtCore.Qt.CaseInsensitive)
		self.QProxyModel.setFilterRegExp(regExp)

	def _listItemRightClicked(self, QPos):
		QListMenu= QtGui.QMenu(self.QListView)
		QMenuItem_create = QListMenu.addAction("Create")
		QMenuItem_rename = QListMenu.addAction("Rename")
		QMenuItem_delete = QListMenu.addAction("Delete")
		#self.connect(menu_item_rename, QtCore.SIGNAL("triggered()"), self.renameItem) 
		#self.connect(menu_item_delete, QtCore.SIGNAL("triggered()"), self.menuItemClicked) 

		parentPosition = self.QListView.mapToGlobal(QtCore.QPoint(0, 0))        
		QListMenu.move(parentPosition + QPos)

		try:
			currentItem = self.QListView.currentIndex().data()
			if not currentItem:
				QMenuItem_rename.setEnabled(False)
				QMenuItem_delete.setEnabled(False)			
			QListMenu.show() 
		except:
			pass

	## controlled from other list's item click
	def _listItemClick(self):
		QListViewSource = self.oLayout.QListView
		sPathSource = self.oLayout.sPath
		currentItem = QListViewSource.currentIndex().data()
		if currentItem:
			sPath = os.path.join(sPathSource, str(currentItem))
			sPath = os.path.join(sPath, self.sName.lower())
			self.sPath = sPath
			if os.path.exists(sPath):
				self.rebuildListModel()
			else:
				self.QSourceModel.clear()
		else:
			self.QSourceModel.clear()

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