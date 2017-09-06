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
reload(workspaces)
reload(files)


## sync assets UI
class syncAssetsUI(QtGui.QWidget):
	"""docstring for ClassName"""
	def __init__(self, sParent = None):
		super(syncAssetsUI, self).__init__()

		self.dAssetData = getFileInfoFromLocalAndServer()
		print self.dAssetData
		
		#Parent widget under Maya main window        
		self.setParent(sParent)       
		self.setWindowFlags(QtCore.Qt.Window)

		#Set the object name     
		self.setObjectName('syncAssets_uniqueId')        
		self.setWindowTitle('Sync Assets')        
		self.setGeometry(100, 100, 1000, 500) 
		self.initUI()

	def initUI(self):
		QLayoutBase = QtGui.QHBoxLayout(self)
		self.setLayout(QLayoutBase)

		self.oLayout_project = syncAssetLayout(QLayoutBase)
		self.oLayout_project.initUI()

		self.setProjectList()

		self.oLayout_asset = syncAssetLayout(QLayoutBase)
		self.oLayout_asset.sName = 'Assets'
		self.oLayout_asset.initUI()

		QSelectionModel = self.oLayout_project.QTreeView.selectionModel()
		QSelectionModel.currentChanged.connect(self.setAssetList)

		self.oLayout_type = syncAssetLayout(QLayoutBase)
		self.oLayout_type.sName = 'Types'
		self.oLayout_type.initUI()

		QSelectionModel = self.oLayout_asset.QTreeView.selectionModel()
		QSelectionModel.currentChanged.connect(self.setTypeList)

		QLayoutButton = QtGui.QVBoxLayout(self)
		QLayoutButton.setAlignment(QtCore.Qt.AlignBottom)
		QLayoutBase.addLayout(QLayoutButton)
		self.QPushButtonPush = QtGui.QPushButton('Push to Server')
		self.QPushButtonPush.setMaximumWidth(150)
		QLayoutButton.addWidget(self.QPushButtonPush)

		self.QPushButtonPull = QtGui.QPushButton('Pull to Local')
		self.QPushButtonPull.setMaximumWidth(150)
		QLayoutButton.addWidget(self.QPushButtonPull)

	def setProjectList(self):
		lProjects = self.dAssetData.keys()
		lStatus = []
		lProjects.sort()
		for sProject in lProjects:
			lStatus.append(self.dAssetData[sProject]['status'])
		self.oLayout_project._setList(lProjects, lStatus)

	def setAssetList(self):
		self.oLayout_asset._refreshFileList()
		self.sProject = self._getSelectItem(self.oLayout_project)

		if self.sProject:
			if self.dAssetData[self.sProject]['folders']:
				lAssets = self.dAssetData[self.sProject]['folders'].keys()
				lStatus = []
				lAssets.sort()
				for sAsset in lAssets:
					lStatus.append(self.dAssetData[self.sProject]['folders'][sAsset]['status'])
				self.oLayout_asset._setList(lAssets, lStatus)
			else:
				self.oLayout_asset._refreshFileList()
		else:
			self.oLayout_asset._refreshFileList()

	def setTypeList(self):
		self.oLayout_type._refreshFileList()
		self.sAsset = self._getSelectItem(self.oLayout_asset)

		if self.sAsset:
			if self.dAssetData[self.sProject]['folders'][self.sAsset]['folders']:
				lTypes = self.dAssetData[self.sProject]['folders'][self.sAsset]['folders'].keys()
				lStatus = []
				lTypes.sort()
				for sType in lTypes:
					lStatus.append(self.dAssetData[self.sProject]['folders'][self.sAsset]['folders'][sType]['status'])
				self.oLayout_type._setList(lTypes, lStatus)
			else:
				self.oLayout_type._refreshFileList()
		else:
			self.oLayout_type._refreshFileList()

	def _getSelectItem(self, oLayout):
		iIndexProxy = oLayout.QTreeView.currentIndex()
		if iIndexProxy.row() >= 0:
			iIndexSource = oLayout.QProxyModel.mapToSource(iIndexProxy)
		else:
			iIndexSource = None

		if iIndexSource:
			sSelect = oLayout.QSourceModel.item(iIndexSource.row(), column = syncAssetLayout.NAME).text()
		else:
			sSelect = None
		return sSelect



class syncAssetLayout():
	NAME, STATUS = range(2)
	def __init__(self, QLayoutBase):
		self.QLayoutBase = QLayoutBase
		self.QLayout = QtGui.QVBoxLayout()
		self.QLayoutBase.addLayout(self.QLayout)
		self.sName = 'Projects'
		self.oLayout = None
		self.bListItemClick = False
		
	def initUI(self):
		self.setBaseLayout()

	def setBaseLayout(self):
		QLabel = QtGui.QLabel('%s:' %self.sName)
		self.QLayout.addWidget(QLabel)

		#### filter
		self.QFilterEdit = QtGui.QLineEdit()
		self.QFilterEdit.setPlaceholderText('Filter...')
		self.QLayout.addWidget(self.QFilterEdit)

		self.QSourceModel = QtGui.QStandardItemModel(0,2)
		self.QSourceModel.setHeaderData(syncAssetLayout.NAME, QtCore.Qt.Horizontal, "Name")
		self.QSourceModel.setHeaderData(syncAssetLayout.STATUS, QtCore.Qt.Horizontal, "Status")
		self.QProxyModel = QtGui.QSortFilterProxyModel()
		self.QProxyModel.setDynamicSortFilter(True)
		self.QProxyModel.setSourceModel(self.QSourceModel)
		self.QTreeView = fileTreeView()
		self.QTreeView.setRootIsDecorated(False)
		self.QTreeView.setAlternatingRowColors(True)
		self.QTreeView.setModel(self.QProxyModel)
		self.QTreeView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.QTreeView.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
		self.QTreeView.header().setStretchLastSection(False)
		self.QLayout.addWidget(self.QTreeView)

		self.QFilterEdit.textChanged.connect(self._filterRegExpChanged)

	def _setList(self, lFiles, lStatus):
		for i, sFile in enumerate(lFiles):
			self._addFile(sFile, lStatus[i])

	def _refreshFileList(self):
		iRowCount = self.QSourceModel.rowCount()
		for i in range(0, iRowCount + 1):
			self.QSourceModel.removeRow(0)
	
	def _addFile(self, sName, sStatus):
		iRowCount = self.QSourceModel.rowCount()
		self.QSourceModel.insertRow(iRowCount)
		self.QSourceModel.setData(self.QSourceModel.index(iRowCount, syncAssetLayout.NAME), sName)
		self.QSourceModel.setData(self.QSourceModel.index(iRowCount, syncAssetLayout.STATUS), sStatus)
		if sStatus == 'Out of date':
			self.QSourceModel.item(iRowCount, column = syncAssetLayout.STATUS).setForeground(QtGui.QBrush(QtGui.QColor('red')))
		elif sStatus == 'Up to date':
			self.QSourceModel.item(iRowCount, column = syncAssetLayout.STATUS).setForeground(QtGui.QBrush(QtGui.QColor('green')))
		else:
			self.QSourceModel.item(iRowCount, column = syncAssetLayout.STATUS).setForeground(QtGui.QBrush(QtGui.QColor('yellow')))

	def _filterRegExpChanged(self):
		regExp = QtCore.QRegExp(self.QFilterEdit.text(), QtCore.Qt.CaseInsensitive)
		self.QProxyModel.setFilterRegExp(regExp)
	


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

def getMayaWindow():
	ptr = OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(ptr), QtGui.QMainWindow)

def getFileInfoFromLocalAndServer():
	dAssetData = {}
	## get projects
	lProjectsData, lProjects = compareFilesLocalServer(files.sPathLocal, files.sPathServer)
	for iProject, sProject in enumerate(lProjects):
		dAssetData.update(lProjectsData[iProject])

		sPathLocal_asset = os.path.join(files.sPathLocal, sProject)
		sPathLocal_asset = os.path.join(sPathLocal_asset, 'assets')
		sPathServer_asset = os.path.join(files.sPathServer, sProject)
		sPathServer_asset = os.path.join(sPathServer_asset, 'assets')

		lAssetsData, lAssets = compareFilesLocalServer(sPathLocal_asset, sPathServer_asset)
		for iAsset, sAsset in enumerate(lAssets):
			dAssetData[sProject]['folders'].update(lAssetsData[iAsset])

			sPathLocal_type = os.path.join(sPathLocal_asset, sAsset)
			sPathServer_type = os.path.join(sPathServer_asset, sAsset)

			lTypesData, lTypes = compareFilesLocalServer(sPathLocal_type, sPathServer_type)
			for iType, sType in enumerate(lTypes):
				dAssetData[sProject]['folders'][sAsset]['folders'].update(lTypesData[iType])

	return dAssetData

def compareFilesLocalServer(sPathLocal, sPathServer):
	lReturn = []

	if os.path.exists(sPathLocal):
		lFiles_local = workspaces._getFoldersFromFolderList(sPathLocal)
	else:
		lFiles_local = []
	if os.path.exists(sPathServer):
		lFiles_server = workspaces._getFoldersFromFolderList(sPathServer)
	else:
		lFiles_server = []

	lFiles = list(set(lFiles_local + lFiles_server))
	for sFile in lFiles:
		if sFile in lFiles_local and sFile in lFiles_server:
			sStatus = 'Up to date'
		elif sFile in lFiles_local:
			sStatus = 'Out of date'
		else:
			sStatus = 'Not on local'
		dFiles = {sFile: {'status': sStatus, 'folders': {}}}
		lReturn.append(dFiles)

	return lReturn, lFiles