## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI
import os
import functools
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
	VERSION, FILENAME = range(2)
	"""docstring for assetsManagerUI"""
	def __init__(self, sParent = None):
		super(assetsManagerUI, self).__init__()

		self.dAssetData = None

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
		self.oLayout_asset.sPathListItem = 'assets'
		self.oLayout_asset.initUI()

		## Type Layout
		self.oLayout_type = assetsManagerBaseLayout(QLayoutBase)
		self.oLayout_type.sName = 'Types'
		self.oLayout_type.oLayout = self.oLayout_asset
		self.oLayout_type.bListItemClick = True
		self.oLayout_type.initUI()

		## File Layout
		self._fileLayout(QLayoutBase)
		
	def _fileLayout(self, QLayoutBase):
		QLayout = QtGui.QVBoxLayout()
		QLayoutBase.addLayout(QLayout)

		QLabel = QtGui.QLabel('File:')
		QLayout.addWidget(QLabel)

		#### file
		self.QLabel_file = QtGui.QLabel()
		self.QLabel_file.setStyleSheet("border: 1px solid black;")
		QLayout.addWidget(self.QLabel_file)
		#self.QComboBox_file.currentIndexChanged.connect(self._getVersionInfo)

		#### versions		
		self.QCheckBox_version = QtGui.QCheckBox('Versions')
		QLayout.addWidget(self.QCheckBox_version)

		self.QSourceModel_version = QtGui.QStandardItemModel(0,2)
		self.QSourceModel_version.setHeaderData(assetsManagerUI.VERSION, QtCore.Qt.Horizontal, "Version")
		self.QSourceModel_version.setHeaderData(assetsManagerUI.FILENAME, QtCore.Qt.Horizontal, "File Name")
		self.QTreeView_version = fileTreeView()
		self.QTreeView_version.setRootIsDecorated(False)
		self.QTreeView_version.setAlternatingRowColors(True)
		self.QTreeView_version.setModel(self.QSourceModel_version)
		QLayout.addWidget(self.QTreeView_version)

		#### connect version with QTreeView
		self.QTreeView_version.setEnabled(False)
		#self.QCheckBox_version.stateChanged.connect(self._setVersionEnabled)

		#### comment
		self.QLabel_comment = QtGui.QLabel()
		self.QLabel_comment.setStyleSheet("border: 1px solid black;")
		self.QLabel_comment.setMinimumHeight(80)
		self.QLabel_comment.setScaledContents(True)
		QLayout.addWidget(self.QLabel_comment)

		self.QLabel_comment.setAlignment(QtCore.Qt.AlignTop)

		#QSelectionModel = self.QTreeView_version.selectionModel()
		#QSelectionModel.currentChanged.connect(self._setVersionComment)

		#### button
		self.QPushButton_open = QtGui.QPushButton('Open File')
		QLayout.addWidget(self.QPushButton_open)

	def _addItem_QComboBox_file(self):
		currentItem = self.oLayout_asset.QListView.currentIndex().data()
		if currentItem:
			self.sPathAsset = os.path.join(self.oLayout_asset.sPath, currentItem)
			if os.path.exists(self.sPathAsset):
				lFolders = files.getFilesFromPath(self.sPathAsset, sType = 'folder')
				if lFolders:
					for sFolder in lFolders:
						self.QComboBox_file.addItem(sFolder.title())
				else:
					self.QComboBox_file.clear()
			else:
				self.QComboBox_file.clear()
		else:
			self.QComboBox_file.clear()

	def _getVersionInfo(self):
		currentItem = self.QComboBox_file.currentText()
		if currentItem:
			sPathSource = os.path.join(self.sPathAsset, currentItem.lower())
			if os.path.exists(sPathSource):
				## get version file
				sVersionFile = files.getFileFromPath(sPathSource, 'assetInfo', sType = '.version')
				if sVersionFile:
					self.dAssetData = files.readJsonFile(os.path.join(sPathSource, sVersionFile))

					sFileLatest = self.dAssetData['assetInfo']['sCurrentVersionName']
					sFileTypeLatest = self.dAssetData['assetInfo']['sFileType']
					sPathFile = os.path.join(sPathSource, '%s%s' %(sFileLatest, sFileTypeLatest))
					if sFileLatest and os.path.exists(sPathFile):
						self.QLabel_file.setText(sFileLatest)

						dVersions = self.dAssetData['versionInfo']
						lVersions = dVersions.keys()
						lVersions.sort(reverse = True)

						self._refreshVersion()
						for iVersion in lVersions:
							sFileVersion = dVersions[iVersion]['sVersionName']
							sFileTypeVersion = dVersions[iVersion]['sFileType']
							sPathFile = os.path.join(sPathSource, 'wipFiles')
							sPathFile = os.path.join(sPathFile, '%s%s' %(sFileVersion, sFileTypeVersion))
							if sFileVersion and os.path.exists(sPathFile):
								self._addVersion(iVersion, sFileVersion)
					else:
						self.QLabel_file.clear()
						self._refreshVersion()
				else:
					self.QLabel_file.clear()
					self._refreshVersion()
			else:
				self.QLabel_file.clear()
				self._refreshVersion()
		else:
			self.QLabel_file.clear()
			self._refreshVersion()

	def _addVersion(self, iVersion, sFileName):
		self.QSourceModel_version.insertRow(0)
		self.QSourceModel_version.setData(self.QSourceModel_version.index(0, assetsManagerUI.VERSION), iVersion)
		self.QSourceModel_version.setData(self.QSourceModel_version.index(0, assetsManagerUI.FILENAME), sFileName)

	def _refreshVersion(self):
		iRowCount = self.QSourceModel_version.rowCount()
		for i in range(0, iRowCount + 1):
			self.QSourceModel_version.removeRow(i)
	
	def _setVersionEnabled(self):
		bVersion = self.QCheckBox_version.isChecked()
		self.QTreeView_version.setEnabled(bVersion)
		if not bVersion:
			self.QTreeView_version.clearSelection()
			self.QTreeView_version.clearFocus()
			self.QTreeView_version.setCurrentIndex(QtCore.QModelIndex())

	def _setVersionComment(self):
		iVersion = self.QTreeView_version.currentIndex().data()
		if iVersion and self.dAssetData:
			sComment = self.dAssetData['versionInfo'][str(iVersion)]['sComment']
			self.QLabel_comment.setText(sComment)
		else:
			self.QLabel_comment.clear()

		

					







		


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
		self.sPathListItem = None

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
		QInput_create = functools.partial(self.popWinRightClick, sWinType = 'create')
		QInput_rename = functools.partial(self.popWinRightClick, sWinType = 'rename')
		QInput_delete = functools.partial(self.popWinRightClick, sWinType = 'delete')
		QMenuItem_create.connect(QMenuItem_create, QtCore.SIGNAL("triggered()"), QInput_create)
		QMenuItem_rename.connect(QMenuItem_rename, QtCore.SIGNAL("triggered()"), QInput_rename)
		QMenuItem_delete.connect(QMenuItem_delete, QtCore.SIGNAL("triggered()"), QInput_delete)
		
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
			if self.sPathListItem:
				sPath = os.path.join(sPath, self.sPathListItem)
			self.sPath = sPath
			if os.path.exists(sPath):
				self.rebuildListModel()
			else:
				self.QSourceModel.clear()
		else:
			self.QSourceModel.clear()

	def popWinRightClick(self, sWinType = 'create'):
		if 'project' in self.sName.lower():
			sCreateType = 'project'
		elif 'asset' in self.sName.lower():
			sCreateType = 'asset'
		elif 'type' in self.sName.lower():
			sCreateType = 'type'
		else:
			sCreateType = ''
		sText = '%s %s:' %(sWinType.title(), sCreateType)
		if sWinType != 'delete':
			sInput, bInput = QtGui.QInputDialog.getText(self.QListView, sWinType.title(), sText)
		else:
			sInput = True
			bInput = True
		if bInput:
			bCheck = QtGui.QMessageBox.question(self.QListView, sWinType.title(), 'Are you sure to %s this %s?' %(sWinType, sCreateType), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
		else:
			bCheck = False
		if bCheck != QtGui.QMessageBox.Yes:
			sInput = None

		return sInput

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

	def mouseDoubleClickEvent(self, event):
		pass

class fileTreeView(QtGui.QTreeView):
	def __init__(self, parent=None):
		super(fileTreeView, self).__init__(parent)

	def keyPressEvent(self, event):
		if (event.key() == QtCore.Qt.Key_Escape and
			event.modifiers() == QtCore.Qt.NoModifier):
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		else:
			QtGui.QTreeView.keyPressEvent(self, event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		QtGui.QTreeView.mousePressEvent(self, event)

	def mouseDoubleClickEvent(self, event):
		pass

## Functions
def getMayaWindow():
	ptr = OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(ptr), QtGui.QMainWindow)