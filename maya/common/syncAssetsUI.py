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
		self.QPushButtonRefresh = QtGui.QPushButton('Force to refresh')
		self.QPushButtonRefresh.setMaximumWidth(150)
		QLayoutButton.addWidget(self.QPushButtonRefresh)
		self.QPushButtonRefresh.clicked.connect(self._refreshCmd)

		QLabel = QtGui.QLabel()
		QLayoutButton.addWidget(QLabel)
		
		self.QPushButtonPush = QtGui.QPushButton('Push to Server')
		self.QPushButtonPush.setMaximumWidth(150)
		QLayoutButton.addWidget(self.QPushButtonPush)
		self.QPushButtonPush.clicked.connect(self._publishCmd)

		self.QPushButtonPull = QtGui.QPushButton('Pull to Local')
		self.QPushButtonPull.setMaximumWidth(150)
		QLayoutButton.addWidget(self.QPushButtonPull)
		self.QPushButtonPull.clicked.connect(self._checkoutCmd)

	def setProjectList(self):
		lProjects = self.dAssetData.keys()
		lStatus = []
		lProjects.sort()
		for sProject in lProjects:
			lStatus.append(self.dAssetData[sProject]['status'])
		self.oLayout_project._setList(lProjects, lStatus)

	def setAssetList(self):
		self.oLayout_asset._refreshFileList()
		self.sProject, sStatus = self._getSelectItem(self.oLayout_project)

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
		self.sAsset, sStatus = self._getSelectItem(self.oLayout_asset)

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
			sStatus = oLayout.QSourceModel.item(iIndexSource.row(), column = syncAssetLayout.STATUS).text()
		else:
			sSelect = None
			sStatus = None
		return sSelect, sStatus

	def _publishCmd(self):
		bCheck = QtGui.QMessageBox.question(self, 'Push To Server', 'Are you sure you want to push to server?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
		if bCheck == QtGui.QMessageBox.Yes:
			self._syncCmd('server')

	def _checkoutCmd(self):
		bCheck = QtGui.QMessageBox.question(self, 'Pull To Local', 'Are you sure you want to pull to local?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
		if bCheck == QtGui.QMessageBox.Yes:
			self._syncCmd('local')

	def _refreshCmd(self):
		self.oLayout_project._refreshFileList()
		self.getFileInfoFromLocalAndServer()
		self.setProjectList()
			
	def _syncCmd(self, sMode):
		sTypeSel, sStatusTypeSel = self._getSelectItem(self.oLayout_type)
		sAssetSel, sStatusAssetSel = self._getSelectItem(self.oLayout_asset)
		sProjectSel, sStatusProjectSel = self._getSelectItem(self.oLayout_project)
		if sTypeSel:
			workspaces.syncAsset(sProjectSel, sAssetSel, sTypeSel, sMode = sMode)
		elif sAssetSel:
			lTypes = self.dAssetData[sProjectSel]['folders'][sAssetSel]['folders'].keys()
			if lTypes:
				for sType in lTypes:
					workspaces.syncAsset(sProjectSel, sAssetSel, sType, sMode = sMode)
			else:
				workspaces.syncAsset(sProjectSel, sAssetSel, None, sMode = sMode)
		elif sProjectSel:
			lAssets = self.dAssetData[sProjectSel]['folders'].keys()
			if lAssets:
				for sAsset in lAssets:
					lTypes = self.dAssetData[sProjectSel]['folders'][sAsset]['folders'].keys()
					if lTypes:
						for sType in lTypes:
							workspaces.syncAsset(sProjectSel, sAsset, sType, sMode = sMode)
					else:
						workspaces.syncAsset(sProjectSel, sAsset, None, sMode = sMode)
			else:
				workspaces.syncAsset(sProjectSel, None, None, sMode = sMode)
		else:
			lProjects = self.dAssetData.keys()
			if lProjects:
				for sProject in lProjects:
					lAssets = self.dAssetData[sProject]['folders'].keys()
					if lAssets:
						for sAsset in lAssets:
							lTypes = self.dAssetData[sProject]['folders'][sAsset]['folders'].keys()
							if lTypes:
								for sType in lTypes:
									workspaces.syncAsset(sProject, sAsset, sType, sMode = sMode)
							else:
								workspaces.syncAsset(sProject, sAsset, None, sMode = sMode)
					else:
						workspaces.syncAsset(sProject, None, None, sMode = sMode)

		self._refreshCmd()


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
		sStatus_project = dAssetData[sProject]['status']

		sPathLocal_asset = os.path.join(files.sPathLocal, sProject)
		sPathLocal_asset = os.path.join(sPathLocal_asset, 'assets')
		sPathServer_asset = os.path.join(files.sPathServer, sProject)
		sPathServer_asset = os.path.join(sPathServer_asset, 'assets')

		lAssetsData, lAssets = compareFilesLocalServer(sPathLocal_asset, sPathServer_asset)
		for iAsset, sAsset in enumerate(lAssets):
			dAssetData[sProject]['folders'].update(lAssetsData[iAsset])
			sStatus_asset = dAssetData[sProject]['folders'][sAsset]['status']

			sPathLocal_type = os.path.join(sPathLocal_asset, sAsset)
			sPathServer_type = os.path.join(sPathServer_asset, sAsset)

			lTypesData, lTypes = compareFilesLocalServer(sPathLocal_type, sPathServer_type)

			for iType, sType in enumerate(lTypes):
				dAssetData[sProject]['folders'][sAsset]['folders'].update(lTypesData[iType])
				sPathLocal_file = os.path.join(sPathLocal_type, sType)
				sPathServer_file = os.path.join(sPathServer_type, sType)
				sStatus = compareFileVersion(sPathLocal_file, sPathServer_file)
				dAssetData[sProject]['folders'][sAsset]['folders'][sType]['status'] = sStatus

				if sStatus_asset == 'Out of date' or sStatus == 'Out of date':
					sStatus_asset = 'Out of date'
				elif sStatus_asset == 'Not on local' or sStatus == 'Not on local':
					sStatus_asset = 'Not on local'
				else:
					sStatus_asset = 'Up to date'

			dAssetData[sProject]['folders'][sAsset]['status'] = sStatus_asset

			if sStatus_project == 'Out of date' or sStatus_asset == 'Out of date':
				sStatus_project = 'Out of date'
			elif sStatus_project == 'Not on local' or sStatus_asset == 'Not on local':
				sStatus_project = 'Not on local'
			else:
				sStatus_project = 'Up to date'

		dAssetData[sProject]['status'] = sStatus_project

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

def compareFileVersion(sPathLocal, sPathServer):
	sVersionLocal = os.path.join(sPathLocal, 'assetInfo.version')
	sVersionServer = os.path.join(sPathServer, 'assetInfo.version')

	if os.path.exists(sVersionLocal) and os.path.exists(sVersionServer):
		dAssetDataLocal = files.readJsonFile(sPathLocal)
		dAssetDataServer = files.readJsonFile(sPathServer)

		if dAssetDataLocal['versionInfo']:
			lVersionsLocal = dAssetDataLocal['versionInfo'].keys()
			iVersionLocal = int(max(lVersionsLocal))
		else:
			iVersionLocal = -1

		if dAssetDataServer['versionInfo']:
			lVersionsServer = dAssetDataServer['versionInfo'].keys()
			iVersionServer = int(max(lVersionsServer))
		else:
			iVersionServer = -1

		if iVersionLocal == iVersionServer:
			sStatus = 'Up to date'
		elif iVersionLocal > iVersionServer:
			sStatus = 'Out of date'
		else:
			sStatus = 'Not on local'

	elif os.path.exists(sVersionLocal):
		sStatus = 'Out of date'
	elif os.path.exists(sVersionServer):
		sStatus = 'Not on local'
	else:
		sStatus = 'Up to date'

	return sStatus


