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

class saveAssetUI(QtGui.QWidget):
	"""docstring for saceAssetUI"""
	def __init__(self, sParent = None):
		super(saveAssetUI, self).__init__()

		self.setPathWin = None

		#Parent widget under Maya main window        
		self.setParent(sParent)       
		self.setWindowFlags(QtCore.Qt.Window)

		#Set the object name     
		self.setObjectName('saveAsset_uniqueId')        
		self.setWindowTitle('Save Asset')        
		self.setFixedSize(400, 240)
		self.initUI()

	def initUI(self):
		QLayoutBase = QtGui.QVBoxLayout(self)
		self.setLayout(QLayoutBase)

		QLayoutPath = QtGui.QHBoxLayout(self)
		QLayoutBase.addLayout(QLayoutPath)

		self.QLabelProject = QtGui.QLabel()
		self.QLabelAsset = QtGui.QLabel()
		self.QLabelType = QtGui.QLabel()

		lLabels = ['Project:', 'Asset:', 'Type:']
		for i, QLabel in enumerate([self.QLabelProject, self.QLabelAsset, self.QLabelType]):
			QLayoutLabel = QtGui.QVBoxLayout(self)
			QLabelTitle = QtGui.QLabel(lLabels[i])
			QLabelTitle.setMaximumHeight(20)
			QLabel.setStyleSheet("border: 1px solid black;")
			QLabel.setMaximumHeight(20)
			QLayoutLabel.addWidget(QLabelTitle)
			QLayoutLabel.addWidget(QLabel)
			QLayoutPath.addLayout(QLayoutLabel)

		QPushButtonPath = QtGui.QPushButton('Change Path')
		QLayoutBase.addWidget(QPushButtonPath)
		QPushButtonPath.pressed.connect(self._setPathWinPop)

		## tag
		QLayoutTag = QtGui.QHBoxLayout(self)
		QLayoutBase.addLayout(QLayoutTag)

		QLabelTag = QtGui.QLabel('Tag:')
		QLabelTag.setMaximumHeight(20)
		QLayoutTag.addWidget(QLabelTag)

		self.QLineEditTag = QtGui.QLineEdit()
		QLayoutTag.addWidget(self.QLineEditTag)

		## comment
		QLayoutComment = QtGui.QVBoxLayout(self)
		QLayoutBase.addLayout(QLayoutComment)

		QLabelComment = QtGui.QLabel('Comment:')
		QLabelComment.setMaximumHeight(20)
		QLayoutComment.addWidget(QLabelComment)

		self.QLineEditComment = QtGui.QLineEdit()
		self.QLineEditComment.setMinimumHeight(100)
		self.QLineEditComment.setAlignment(QtCore.Qt.AlignTop)
		QLayoutComment.addWidget(self.QLineEditComment)

		## Save button
		self.QPushButtonSave = QtGui.QPushButton('Save Asset')
		QLayoutBase.addWidget(self.QPushButtonSave)
		self.QPushButtonSave.setEnabled(False)
		self._getAssetFolders()
		self.QPushButtonSave.clicked.connect(self._saveAsset)

	def _getAssetFolders(self):
		sPath = workspaces._getProject(rootDirectory = False)
		if os.path.isfile(sPath):
			sPath = os.path.dirname(sPath)
		sPath = os.path.abspath(sPath)
		if files.sPathLocal in sPath:
			sPath = sPath.replace('%s\\' %files.sPathLocal, '')
			sFolders = sPath.split('\\')
			if len(sFolders) == 4:
				self.QLabelProject.setText(sFolders[0])
				self.QLabelAsset.setText(sFolders[2])
				self.QLabelType.setText(sFolders[3])
				self.QPushButtonSave.setEnabled(True)


	def _setPathWinPop(self):
		try:
			self.setPathWin.close()
		except:
			pass
		self.setPathWin = setPathWin()
		self.setPathWin.show()
		self.setPathWin.QPushButtonPath.clicked.connect(self._resetPath)

	def _resetPath(self):
		if self.setPathWin.sProject and self.setPathWin.sAsset and self.setPathWin.sType:
			self.QLabelProject.setText(self.setPathWin.sProject)
			self.QLabelAsset.setText(self.setPathWin.sAsset)
			self.QLabelType.setText(self.setPathWin.sType)
			self.QPushButtonSave.setEnabled(True)

	def _saveAsset(self):
		sProject = self.QLabelProject.text()
		sAsset = self.QLabelAsset.text()
		sType = self.QLabelType.text()

		sTag = self.QLineEditTag.text()
		sComment = self.QLineEditComment.text()

		bCheck = QtGui.QMessageBox.question(self, 'Save Asset', 'Project: %s\n\nAsset: %s\n\nType: %s\n\nTag: %s\n\nComment: %s' %(sProject, sAsset, sType, sTag, sComment), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

		if bCheck == QtGui.QMessageBox.Yes:
			workspaces.saveAsset(sAsset, sType, sProject, sTag = sTag, sComment = sComment)
			self.close()

	def closeEvent(self, event):
		try:
			self.setPathWin.close()
		except:
			pass
		event.accept()

class setPathWin(QtGui.QDialog):
	def __init__(self, sParent=None):
		super(setPathWin, self).__init__()

		self.sProject = None
		self.sAsset = None
		self.sType = None

		self.setWindowTitle('Set save path')
		self.setGeometry(100, 100, 350, 100)
		self.setFixedHeight(100)

		self.initUI()

	def initUI(self):
		QLayoutBase = QtGui.QVBoxLayout(self)
		self.setLayout(QLayoutBase)

		QLayoutPath = QtGui.QHBoxLayout(self)
		QLayoutBase.addLayout(QLayoutPath)

		self.QComboBoxProject = QtGui.QComboBox()
		self.QComboBoxAsset = QtGui.QComboBox()
		self.QComboBoxType = QtGui.QComboBox()

		lLabels = ['Project:', 'Asset:', 'Type:']
		for i, QComboBox in enumerate([self.QComboBoxProject, self.QComboBoxAsset, self.QComboBoxType]):
			QLayoutLabel = QtGui.QVBoxLayout(self)
			QLabel = QtGui.QLabel(lLabels[i])
			QLabel.setMaximumHeight(20)
			QLayoutLabel.addWidget(QLabel)
			QLayoutLabel.addWidget(QComboBox)
			QLayoutPath.addLayout(QLayoutLabel)

		self._listProjects()
		self._listAssets()
		self._listTypes()
		self.QComboBoxProject.currentIndexChanged.connect(self._listAssets)
		self.QComboBoxAsset.currentIndexChanged.connect(self._listTypes)

		self.QPushButtonPath = QtGui.QPushButton('Set Path')
		QLayoutBase.addWidget(self.QPushButtonPath)
		self._setPushButtonEnabled()
		self.QComboBoxType.currentIndexChanged.connect(self._setPushButtonEnabled)
		self.QPushButtonPath.pressed.connect(self._setPath)

	def _listProjects(self):
		lFolders = workspaces._getFoldersFromFolderList(files.sPathLocal)
		for sFolder in lFolders:
			self.QComboBoxProject.addItem(sFolder)

	def _listAssets(self):
		sProject = self.QComboBoxProject.currentText()
		if sProject:
			self.QComboBoxAsset.clear()
			sDir, sWipDir = workspaces._getAssetDirectory(sProject = sProject)
			lFolders = workspaces._getFoldersFromFolderList(sDir)
			for sFolder in lFolders:
				self.QComboBoxAsset.addItem(sFolder)
		else:
			self.QComboBoxAsset.clear()

	def _listTypes(self):
		sProject = self.QComboBoxProject.currentText()
		sAsset = self.QComboBoxAsset.currentText()
		if sAsset:
			self.QComboBoxType.clear()
			sDir, sWipDir = workspaces._getAssetDirectory(sProject = sProject, sAsset = sAsset)
			lFolders = workspaces._getFoldersFromFolderList(sDir)
			for sFolder in lFolders:
				self.QComboBoxType.addItem(sFolder)
		else:
			self.QComboBoxType.clear()

	def _setPushButtonEnabled(self):
		sType = self.QComboBoxType.currentText()
		if sType:
			self.QPushButtonPath.setEnabled(True)
		else:
			self.QPushButtonPath.setEnabled(False)

	def _setPath(self):
		self.sProject = self.QComboBoxProject.currentText()
		self.sAsset = self.QComboBoxAsset.currentText()
		self.sType = self.QComboBoxType.currentText()
		self.close()
