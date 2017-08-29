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
		self.oLayout_file = assetsManagerBaseLayout(QLayoutBase)
		self.oLayout_file.sName = 'File'
		self.oLayout_file.bFilter = False
		self.oLayout_file.bListItemRightClick = False
		self.oLayout_file.sLayoutStyle = 'QHBoxLayout'

		#### type enum
		self.QLayout_fileType = QtGui.QHBoxLayout()
		self.oLayout_file.QLayout.addLayout(self.QLayout_fileType)
		QLabel = QtGui.QLabel('Asset Type:')
		self.QLayout_fileType.addWidget(QLabel)
		
		self.QComboBox_file = QtGui.QComboBox()
		### add asset type
		for sType in files.lAssetTypes:
			self.QComboBox_file.addItem(sType.title())
		self.QLayout_fileType.addWidget(self.QComboBox_file)
		
		#### file
		self.oLayout_file.initUI()
		self.oLayout_file.QListView.setMaximumHeight(20)
		#### versions		
		self.QCheckBox_version = QtGui.QCheckBox('Versions')
		self.oLayout_file.QLayout.addWidget(self.QCheckBox_version)

		self.QListView_version = fileListView()
		self.oLayout_file.QLayout.addWidget(self.QListView_version)

		#### comment
		self.QLabel_comment = QtGui.QLabel()
		self.QLabel_comment.setStyleSheet("border: 1px solid black;")
		self.QLabel_comment.setMinimumHeight(80)
		self.QLabel_comment.setScaledContents(True)
		self.oLayout_file.QLayout.addWidget(self.QLabel_comment)

		#### button
		self.QLayout_open = QtGui.QHBoxLayout()
		self.oLayout_file.QLayout.addLayout(self.QLayout_open)
		self.QLayout_open.setDirection(QtGui.QBoxLayout.RightToLeft)
		self.QPushButton_open = QtGui.QPushButton('Open File')
		self.QLayout_open.addWidget(self.QPushButton_open)

		


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
		self.sLayoutStyle = None

	def initUI(self):
		self.setBaseLayout()
		if self.bFilter:
			self.QFilterEdit.textChanged.connect(self._filterRegExpChanged)
		if self.bListItemRightClick:
			self.QListView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
			self.QListView.connect(self.QListView, QtCore.SIGNAL("customContextMenuRequested(QPoint)" ), self._listItemRightClicked)

		if self.bListItemClick and self.oLayout:
			QSelectionModel = self.oLayout.QListView.selectionModel()
			QSelectionModel.currentChanged.connect(self._listItemClick)

	def setBaseLayout(self):
		if self.sLayoutStyle:
			if self.sLayoutStyle == 'QHBoxLayout':
				QLayoutList = QtGui.QHBoxLayout()
			elif self.sLayoutStyle == 'QVBoxLayout':
				QLayoutList = QtGui.QVBoxLayout()
			self.QLayout.addLayout(QLayoutList)
		else:
			QLayoutList = self.QLayout
		QLabel = QtGui.QLabel('%s:' %self.sName)
		QLayoutList.addWidget(QLabel)

		#### filter
		if self.bFilter:
			self.QFilterEdit = QtGui.QLineEdit()
			QLayoutList.addWidget(self.QFilterEdit)
		else:
			self.QFilterEdit = None

		#### List
		self.QSourceModel = QtGui.QStandardItemModel()
		if self.bFilter:
			self.QProxyModel = QtGui.QSortFilterProxyModel()
			self.QProxyModel.setDynamicSortFilter(True)
			self.QProxyModel.setSourceModel(self.QSourceModel)
		else:
			self.QProxyModel = None

		#QListView = QtGui.QListView()
		self.QListView = fileListView()
		if self.bFilter:
			self.QListView.setModel(self.QProxyModel)
		else:
			self.QListView.setModel(self.QSourceModel)
		QLayoutList.addWidget(self.QListView)

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