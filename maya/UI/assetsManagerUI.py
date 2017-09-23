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
import common.workspaces as workspaces
import common.files as files
reload(workspaces)
reload(files)

## Assets Manager UI
class assetsManagerUI(QtGui.QWidget):
	VERSION, FILENAME = range(2)
	"""docstring for assetsManagerUI"""
	def __init__(self, sParent = None):
		super(assetsManagerUI, self).__init__()

		self.dAssetData = None
		self.sPath = None

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
		QSelectionModel = self.oLayout_type.QListView.selectionModel()
		QSelectionModel.currentChanged.connect(self._getVersionInfo)
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
		self.QTreeView_version.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		QLayout.addWidget(self.QTreeView_version)

		#### connect version with QTreeView
		self.QTreeView_version.setEnabled(False)
		self.QCheckBox_version.stateChanged.connect(self._setVersionEnabled)

		#### comment
		self.QLabel_comment = QtGui.QLabel()
		self.QLabel_comment.setStyleSheet("border: 1px solid black;")
		self.QLabel_comment.setMinimumHeight(80)
		self.QLabel_comment.setScaledContents(False)
		self.QLabel_comment.setWordWrap(True)
		QLayout.addWidget(self.QLabel_comment)

		self.QLabel_comment.setAlignment(QtCore.Qt.AlignTop)

		QSelectionModel = self.QTreeView_version.selectionModel()
		QSelectionModel.currentChanged.connect(self._setVersionComment)

		#### button
		QLayoutButton = QtGui.QHBoxLayout(self)
		QLayout.addLayout(QLayoutButton)
		self.QPushButton_setProject = self._addQPushButton(QLayoutButton, sName = 'Set Project')
		self.QPushButton_open = self._addQPushButton(QLayoutButton, sName = 'Open File')
		self.QPushButton_import = self._addQPushButton(QLayoutButton, sName = 'Import File')
		QSelectionModel = self.oLayout_type.QListView.selectionModel()
		QSelectionModel.currentChanged.connect(self._setPushButtonEnabled)
		self.QPushButton_setProject.clicked.connect(self._setProject)
		self.QPushButton_open.clicked.connect(self._openAsset)
		self.QPushButton_import.clicked.connect(self._importAsset)


	
	def _getVersionInfo(self):
		currentItem = self.oLayout_type.QListView.currentIndex().data()
		
		if currentItem:
			self.sPath = os.path.join(os.path.join(self.oLayout_type.sPath, currentItem))

			## get version file
			sVersionFile = os.path.join(self.sPath, 'assetInfo.version')
			
			self.dAssetData = files.readJsonFile(os.path.join(self.sPath, sVersionFile))

			sFileLatest = self.dAssetData['assetInfo']['sCurrentVersionName']
			sFileTypeLatest = self.dAssetData['assetInfo']['sFileType']
			sPathFile = os.path.join(self.sPath, '%s%s' %(sFileLatest, sFileTypeLatest))
			if sFileLatest:
				self.QLabel_file.setText(sFileLatest)

				dVersions = self.dAssetData['versionInfo']
				lVersions = []
				for sKey in dVersions.keys():
					lVersions.append(int(sKey))
				lVersions.sort()

				self._refreshVersion()
				for iVersion in lVersions:
					sFileVersion = dVersions[str(iVersion)]['sVersionName']
					sFileTypeVersion = dVersions[str(iVersion)]['sFileType']
					sPathFile = os.path.join(self.sPath, 'wipFiles')
					sPathFile = os.path.join(sPathFile, '%s%s' %(sFileVersion, sFileTypeVersion))
					if sFileVersion and os.path.exists(sPathFile):
						self._addVersion(iVersion, sFileVersion)
			else:
				self.QLabel_file.clear()
				self._refreshVersion()
				self.QCheckBox_version.setChecked(False)
				
		else:
			self.QLabel_file.clear()
			self._refreshVersion()
			self.QCheckBox_version.setChecked(False)
			self.sPath = None


	def _addVersion(self, iVersion, sFileName):
		self.QSourceModel_version.insertRow(0)
		self.QSourceModel_version.setData(self.QSourceModel_version.index(0, assetsManagerUI.VERSION), iVersion)
		self.QSourceModel_version.setData(self.QSourceModel_version.index(0, assetsManagerUI.FILENAME), sFileName)

	def _refreshVersion(self):
		iRowCount = self.QSourceModel_version.rowCount()
		for i in range(0, iRowCount + 1):
			self.QSourceModel_version.removeRow(0)

	def _setVersionEnabled(self):
		bVersion = self.QCheckBox_version.isChecked()
		self.QTreeView_version.setEnabled(bVersion)
		if not bVersion:
			self.QTreeView_version.clearSelection()
			self.QTreeView_version.clearFocus()
			self.QTreeView_version.setCurrentIndex(QtCore.QModelIndex())

	def _getCurrentVersion(self):
		iIndex = self.QTreeView_version.currentIndex().row()
		if iIndex >= 0:
			iVersion = self.QSourceModel_version.item(iIndex, column = assetsManagerUI.VERSION).text()
		else:
			iVersion = None
		return iVersion

	def _setVersionComment(self):
		iVersion = self._getCurrentVersion()
		if iVersion and self.dAssetData:
			sComment = self.dAssetData['versionInfo'][str(iVersion)]['sComment']
			self.QLabel_comment.setText(sComment)
		else:
			self.QLabel_comment.clear()

	def _addQPushButton(self, QLayout, sName = 'Set Project'):
		QPushButton = QtGui.QPushButton(sName)
		QLayout.addWidget(QPushButton)
		QPushButton.setEnabled(False)
		return QPushButton

	def _setPushButtonEnabled(self):
		currentIndex = self.oLayout_type.QListView.currentIndex()
		if currentIndex.isValid():
			self.QPushButton_setProject.setEnabled(True)
			sFile = self.QLabel_file.text()
			if not sFile:				
				self.QPushButton_open.setEnabled(False)
				self.QPushButton_import.setEnabled(False)
			else:
				self.QPushButton_open.setEnabled(True)
				self.QPushButton_import.setEnabled(True)
		else:
			self.QPushButton_setProject.setEnabled(False)
			self.QPushButton_open.setEnabled(False)
			self.QPushButton_import.setEnabled(False)

	def _setProject(self):
		workspaces.setProject(self.sPath)
		self.close()

	def _getCurrentAsset(self):
		sFolders = files._getFoldersThroughPath(self.sPath)
		sType = sFolders[-1]
		sAsset = sFolders[-2]
		sProject = sFolders[-4]
		bVersion = self.QCheckBox_version.isChecked()
		if not bVersion:
			iVersion = 0
		else:
			iVersion = self._getCurrentVersion()
			if not iVersion:
				iVersion = 0
		return sProject, sAsset, sType, iVersion

	def _openAsset(self):
		bModified = workspaces.checkCurrentSceneModified()
		if bModified:
			bCheck = QtGui.QMessageBox.question(self, 'Open Asset', 'Current Scene is not saved, are you sure to open the asset?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
			if bCheck == QtGui.QMessageBox.Yes:
				bModified = False
		if not bModified:
			sProject, sAsset, sType, iVersion = self._getCurrentAsset()
			workspaces.loadAsset(sProject, sAsset, sType, iVersion = iVersion)
			self.close()

	def _importAsset(self):
		sProject, sAsset, sType, iVersion = self._getCurrentAsset()
		workspaces.loadAsset(sProject, sAsset, sType, iVersion = iVersion, sLoadType = 'import')
		self.close()

## BaseLayout
class assetsManagerBaseLayout():
	def __init__(self, QLayoutBase):
		self.QLayoutBase = QLayoutBase
		self.QLayout = QtGui.QVBoxLayout()
		self.QLayoutBase.addLayout(self.QLayout)
		self.sName = 'Projects'
		self.bFilter = True
		self.sPath = files.sPathLocal
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
		self.QFilterEdit.setPlaceholderText('Filter...')
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
		lFolders = workspaces._getFoldersFromFolderList(self.sPath)
		for sFolder in lFolders:
			sFolder_item = QtGui.QStandardItem(sFolder)
			self.QSourceModel.appendRow(sFolder_item)

	def _filterRegExpChanged(self):
		regExp = QtCore.QRegExp(self.QFilterEdit.text(), QtCore.Qt.CaseInsensitive)
		self.QProxyModel.setFilterRegExp(regExp)

	def _listItemRightClicked(self, QPos):
		QListMenu= QtGui.QMenu(self.QListView)
		QMenuItem_create = QListMenu.addAction("Create")
		QMenuItem_rename = QListMenu.addAction("Rename")
		QMenuItem_delete = QListMenu.addAction("Delete")
		QMenuItem_folder = QListMenu.addAction("Contain Folder")
		#self.connect(menu_item_rename, QtCore.SIGNAL("triggered()"), self.renameItem) 
		#self.connect(menu_item_delete, QtCore.SIGNAL("triggered()"), self.menuItemClicked) 
		QMenuItem_create.connect(QMenuItem_create, QtCore.SIGNAL("triggered()"), self._QMenuItemCreate)
		QMenuItem_rename.connect(QMenuItem_rename, QtCore.SIGNAL("triggered()"), self._QMenuItemRename)
		QMenuItem_delete.connect(QMenuItem_delete, QtCore.SIGNAL("triggered()"), self._QMenuItemDelete)
		QMenuItem_delete.connect(QMenuItem_folder, QtCore.SIGNAL("triggered()"), self._openContainFolder)
		
		parentPosition = self.QListView.mapToGlobal(QtCore.QPoint(0, 0))        
		QListMenu.move(parentPosition + QPos)

		currentItem = self.QListView.currentIndex().data()
		if not currentItem:
			QMenuItem_rename.setEnabled(False)
			QMenuItem_delete.setEnabled(False)
			QMenuItem_folder.setEnabled(False)
		if self.sName.lower() == 'types':
			QMenuItem_rename.setEnabled(False)
		if self.bListItemClick and self.oLayout:
			if self.oLayout.QListView.currentIndex().data():
				QMenuItem_create.setEnabled(True)
			else:
				QMenuItem_create.setEnabled(False)

		QListMenu.show() 


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

	def _QMenuItemCreate(self):
		currentItem = self.QListView.currentIndex().data()
		if self.sName != 'Types':
			sInput, bInput = QtGui.QInputDialog.getText(self.QListView, 'Create',  'Create %s:' %self.sName[:-1])
		else:
			sInput, bInput = QtGui.QInputDialog.getItem(self.QListView, 'Create', 'Create %s:' %self.sName[:-1], files.lAssetTypes, 0, False)
		if bInput and sInput:
			bCheck = QtGui.QMessageBox.question(self.QListView, 'Create', 'Are you sure to create this %s as %s?' %(self.sName[:-1], sInput), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
			if bCheck == QtGui.QMessageBox.Yes:
				if self.sName == 'Projects':
					workspaces.createProject(sInput)
				elif self.sName == 'Assets':
					QListViewSource = self.oLayout.QListView
					sProject = QListViewSource.currentIndex().data()
					workspaces.createAsset(sInput, sProject = sProject)
				else:
					QListViewSource = self.oLayout.QListView
					sAsset = QListViewSource.currentIndex().data()
					sFolders = files._getFoldersThroughPath(self.sPath)
					sProject = sFolders[-3]
					workspaces.createAssetType(sAsset, sProject = sProject, sType = sInput)

				self.rebuildListModel()


	def _QMenuItemRename(self):
		currentItem = self.QListView.currentIndex().data()
		sInput, bInput = QtGui.QInputDialog.getText(self.QListView, 'Rename',  'Rename %s:' %self.sName[:-1])
		if bInput and sInput:
			bCheck = QtGui.QMessageBox.question(self.QListView, 'Rename', 'Are you sure to rename %s?' %currentItem, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
			if bCheck == QtGui.QMessageBox.Yes:
				if self.sName == 'Projects':
					workspaces.renameProject(currentItem, sInput)
				else:
					sProject = files._getFoldersThroughPath(self.sPath)[-2]
					workspaces.renameAsset(sProject, currentItem, sInput)
				self.rebuildListModel()


	def _QMenuItemDelete(self):
		currentItem = self.QListView.currentIndex().data()
		bCheck = QtGui.QMessageBox.question(self.QListView, 'Delete', 'Are you sure to delete %s?' %currentItem, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
		if bCheck == QtGui.QMessageBox.Yes:
			self.QSourceModel.clear()
			workspaces._deleteWorkspaceFolderFromPath(self.sPath, currentItem)
			self.rebuildListModel()

	def _openContainFolder(self):
		currentItem = self.QListView.currentIndex().data()
		files.openFolderFromPath(os.path.join(self.sPath, currentItem))

	def _setQMenuItemCreateEnabled(self):
		currentItem = self.oLayout.QListView.currentIndex().data()
		if not currentItem:
			self.QMenuItem_create.setEnabled(False)
		else:
			self.QMenuItem_create.setEnabled(True)


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