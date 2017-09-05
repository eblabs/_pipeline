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

		self.oLayout_type = syncAssetLayout(QLayoutBase)
		self.oLayout_type.sName = 'Types'
		self.oLayout_type.initUI()

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
		for sProject in lProjects:
			lStatus.append(self.dAssetData[sProject]['status'])
		self.oLayout_project._setList(lProjects, lStatus)	


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

		#self.QFilterEdit.textChanged.connect(self._filterRegExpChanged)

	def _setList(self, lFiles, lStatus):
		for i, sFile in enumerate(lFiles):
			self._addVersion(sFile, lStatus[i])


	def _addVersion(self, sName, sStatus):
		self.QSourceModel.insertRow(0)
		self.QSourceModel.setData(self.QSourceModel.index(0, syncAssetLayout.NAME), sName)
		self.QSourceModel.setData(self.QSourceModel.index(0, syncAssetLayout.STATUS), sStatus)
		if sStatus == 'Out of date':
			self.QSourceModel.item(0, column = syncAssetLayout.STATUS).setForeground(QtGui.QBrush(QtGui.QColor('red')))
		elif sStatus == 'Up to date':
			self.QSourceModel.item(0, column = syncAssetLayout.STATUS).setForeground(QtGui.QBrush(QtGui.QColor('green')))
		else:
			self.QSourceModel.item(0, column = syncAssetLayout.STATUS).setForeground(QtGui.QBrush(QtGui.QColor('yellow')))



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