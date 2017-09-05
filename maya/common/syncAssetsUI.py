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
	lProjects_local = workspaces._getFoldersFromFolderList(files.sPathLocal)
	lProjects_server = workspaces._getFoldersFromFolderList(files.sPathServer)
	lProjects = list(set(lProjects_local + lProjects_server))

	for sProject in lProjects:
		if sProject in lProjects_local and sProject in lProjects_server:
			sStatus = 'Up to date'
		elif sProject in lProjects_local:
			sStatus = 'Out of date'
		else:
			sStatus = 'Not on local'
		dProject = {sProject:{'status': sStatus}}
		dAssetData.update(dProject)
	return dAssetData