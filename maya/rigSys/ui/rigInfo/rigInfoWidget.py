# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# import PySide
try:
	from PySide2 import QtCore, QtGui
	from shiboken2 import wrapInstance 
except ImportError:
	from PySide import QtCore, QtGui
	from shiboken import wrapInstance

# -- import lib
import assets.lib.assets as assets
import assets.lib.rigs as rigs

# -- import rigSys widget
import rigInfoLineEdit
import rigInfoLoadPushButton
import createRigDialog

class RigInfoWidget(QtGui.QGroupBox):
	"""docstring for RigInfoWidget"""
	def __init__(self, *args, **kwargs):
		super(RigInfoWidget, self).__init__(*args, **kwargs)
		self.setTitle('Rig Info')
		self.setFixedHeight(160)

		self.initWidget()
		self.connectSignal()

	def initWidget(self):
		# add layout
		QVBoxLayout = QtGui.QVBoxLayout(self)

		# project
		QHBoxLayout = QtGui.QHBoxLayout()
		QVBoxLayout.addLayout(QHBoxLayout)
		QLabelName = QtGui.QLabel('Project:')
		self.QLineEdit_project = rigInfoLineEdit.RigInfoLineEdit(name = 'Project', 
													fileMethod = self._getProjects)
		QHBoxLayout.addWidget(QLabelName)
		QHBoxLayout.addWidget(self.QLineEdit_project, 1)

		# asset
		QHBoxLayout = QtGui.QHBoxLayout()
		QVBoxLayout.addLayout(QHBoxLayout)
		QLabelName = QtGui.QLabel('Asset:')
		self.QLineEdit_asset = rigInfoLineEdit.RigInfoLineEdit(name = 'Asset', 
													fileMethod = self._getAssets)
		QHBoxLayout.addWidget(QLabelName)
		QHBoxLayout.addWidget(self.QLineEdit_asset, 1)

		# rig
		QHBoxLayout = QtGui.QHBoxLayout()
		QVBoxLayout.addLayout(QHBoxLayout)
		QLabelName = QtGui.QLabel('Rig:')
		self.QComboBox_rig = QtGui.QComboBox()
		QHBoxLayout.addWidget(QLabelName)
		QHBoxLayout.addWidget(self.QComboBox_rig, 1)

		# load button
		self.QPushButton_load = rigInfoLoadPushButton.RigInfoLoadPushButton()
		QVBoxLayout.addWidget(self.QPushButton_load)

	def connectSignal(self):
		self.QLineEdit_project.textChanged.connect(self.QLineEdit_asset.clear)
		self.QLineEdit_asset.textChanged.connect(self._getRigs)
		self.QComboBox_rig.currentIndexChanged.connect(self._getRigInfo)

	def _getProjects(self):
		fileList = assets.listAllProject()
		return fileList

	def _getAssets(self):
		project = self.QLineEdit_project.text()
		if project:
			fileList = assets.listAllAsset(project)
		else:
			fileList = []
		return fileList

	def _getRigs(self):
		self.QComboBox_rig.clear()
		project = self.QLineEdit_project.text()
		asset = self.QLineEdit_asset.text()
		if project and asset:
			rigList = rigs.getRigs(asset, project)
			if rigList:
				for r in rigList:
					self.QComboBox_rig.addItem(r)
			self.QComboBox_rig.addItem('Create')

	def _createRigDialogPop(self):
		self.QDialog_create = createRigDialog.CreateRigDialog(self.QComboBox_rig)
		self.QDialog_create.show()

		# connect signal
		self.QDialog_create.QSignalClose.connect(self._closeCreateRigDialog)
		self.QDialog_create.QSignalCreate.connect(self._createRig)

	def _closeCreateRigDialog(self):
		currentItem = self.QDialog_create.rigName
		if not currentItem:
			currentItem = 'animationRig'
		self._getRigs()
		currentIndex = self.QComboBox_rig.findText(currentItem)
		self.QComboBox_rig.setCurrentIndex(currentIndex)

	def _createRig(self):
		project = self.QLineEdit_project.text()
		asset = self.QLineEdit_asset.text()
		rigs.createRig(project, asset, self.QDialog_create.rigName, 
		 			   rigType = self.QDialog_create.rigType)
		self.QDialog_create.hide()

	def _getRigInfo(self):
		currentText = self.QComboBox_rig.currentText()
		if currentText == 'Create':
			self._createRigDialogPop()
		else:
			self._setRigInfo()

	def _setRigInfo(self):
		self.QPushButton_load.setEnabled(False)
		self.QPushButton_load.versionsList = []
		self.QPushButton_load.checked = 'publish'
		self.project = None
		self.asset = None
		self.rig = None

		project = self.QLineEdit_project.text()
		asset = self.QLineEdit_asset.text()
		rig = self.QComboBox_rig.currentText()

		if project and asset and rig:
			pathRig = rigs.checkRigGroupExist(project, asset, rig = rig)
			if pathRig:
				self.project = project
				self.asset = asset
				self.rig = rig

				self.QPushButton_load.setEnabled(True)

				# get versions
				pathVersionFolder = rigs.getDataFolderPath(project, asset, rig, 'buildScript', 
											mode = 'version', version = None)
				versionsList = assets.getVersions(pathVersionFolder)
				self.QPushButton_load.versionsList = versionsList
				

				
		
		