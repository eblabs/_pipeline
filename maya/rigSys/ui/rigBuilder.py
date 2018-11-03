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

# -- import types
import types

# -- import maya lib
import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI

# -- import lib
import lib.common.uiUtils as uiUtils
import assets.lib.assets as assets
# ---- import end ----

# -- import rigSys widget
import rigInfoLineEdit

class RigBuilder(uiUtils.BaseWindow):
	"""docstring for RigBuilder"""
	def __init__(self, parent=None, title='Rig Builder', geometry=[100,100,100,100]):
		super(RigBuilder, self).__init__(parent=parent, title=title, geometry=geometry)
		
	def initUI(self):
		super(RigBuilder, self).initUI()

		# base layout - horizontal
		QLayoutBase = QtGui.QHBoxLayout(self)
		self.setLayout(QLayoutBase)

		# left layout - vertical
		QFrameLeft = QtGui.QFrame()
		QFrameLeft.setFixedWidth(340)
		QLayoutBase.addWidget(QFrameLeft)
		QLayoutLeft = QtGui.QVBoxLayout(QFrameLeft)

		# right layout
		QFrameRight = QtGui.QFrame()
		QFrameRight.setMinimumWidth(340)
		QLayoutBase.addWidget(QFrameRight)
		QLayoutRight = QtGui.QGridLayout(QFrameRight)

		# rig info ui
		self._rigInfoUI(QLayoutLeft)

		# data ui
		self._dataUI(QLayoutLeft)

		# publish ui
		#self._publishUI(QLayoutLeft)

		# builder ui (right side)
		self._builderUI(QLayoutRight)

	def _rigInfoUI(self, QLayout):
		QGroupBox = self._addGroupBox(QLayout, 'Rig Info')
		QGroupBox.setFixedHeight(160)
		# rig info labels
		QVBoxLayout = QtGui.QVBoxLayout(QGroupBox)

		attrDict = {}

		for name in ['Project', 'Asset', 'Rig']:
			QHBoxLayout = QtGui.QHBoxLayout()
			QVBoxLayout.addLayout(QHBoxLayout)
			QLabelName = QtGui.QLabel(name + ':')
			if name != 'Rig':
				if name == 'Project':
					fileMethod = self._getProjects
				elif name == 'Asset':
					fileMethod = self._getAssets
				QWidget = rigInfoLineEdit.RigInfoLineEdit(name = name, fileMethod = fileMethod)
				attrDict.update({'QLineEdit' + name: QWidget})
			else:
				QWidget = QtGui.QComboBox()
				attrDict.update({'QComboBox' + name: QWidget})

			QHBoxLayout.addWidget(QLabelName)
			QHBoxLayout.addWidget(QWidget, 1)

		self._addAttributeFromDict(attrDict)
		
		QPushButton = QtGui.QPushButton('Load')
		QPushButton.setMinimumHeight(40)
		#QPushButton.setFixedWidth()
		#QPushButton.setEnabled(False)
		#QPushButton.setStyleSheet('background-color:rgb(255,100,100)')
		QVBoxLayout.addWidget(QPushButton)

	def _dataUI(self, QLayout):
		QGroupBox = self._addGroupBox(QLayout, 'Data')
		QGroupBox.setMinimumHeight(260)

		# tab widget
		QGridLayout = QtGui.QGridLayout(QGroupBox)

		QTabWidget = QtGui.QTabWidget()
		QGridLayout.addWidget(QTabWidget)

		# data info
		QWidgetInfo = QtGui.QWidget()
		self._dataInfoWidget(QWidgetInfo)
		QTabWidget.addTab(QWidgetInfo, 'Data Info')
		
		# data edit
		QWidgetEdit = QtGui.QWidget()
		QTabWidget.addTab(QWidgetEdit, 'Data Edit')

		# publish
		QWidgetPublish = QtGui.QWidget()
		self._publishUI(QWidgetPublish)
		QTabWidget.addTab(QWidgetPublish, 'Rig Publish')

	def _dataInfoWidget(self, QWidget):
		QGridLayout = QtGui.QGridLayout(QWidget)

		NAME, INFO = range(2)

		QTreeView = QtGui.QTreeView()
		QSourceModel = QtGui.QStandardItemModel(0,2)
		QSourceModel.setHeaderData(NAME, QtCore.Qt.Horizontal, "Name")
		QSourceModel.setHeaderData(INFO, QtCore.Qt.Horizontal, "Data Info")
		QTreeView.setRootIsDecorated(False)
		QTreeView.setAlternatingRowColors(True)
		QTreeView.setModel(QSourceModel)

		QGridLayout.addWidget(QTreeView)
		
	def _publishUI(self, QWidget):
		# base layout
		QVBoxLayout = QtGui.QVBoxLayout(QWidget)

		# tag layout
		QHBoxLayout = QtGui.QHBoxLayout()
		QVBoxLayout.addLayout(QHBoxLayout)
		QLabel = QtGui.QLabel('Tag:')
		QLineEditTag = QtGui.QLineEdit()
		QHBoxLayout.addWidget(QLabel)
		QHBoxLayout.addWidget(QLineEditTag)

		# comment
		QLabel = QtGui.QLabel('Comment:')
		QTextEdit = QtGui.QTextEdit()
		QVBoxLayout.addWidget(QLabel)
		QVBoxLayout.addWidget(QTextEdit)

		# publish button
		QPushButton = QtGui.QPushButton('Publish')
		QVBoxLayout.addWidget(QPushButton)

	def _builderUI(self, QLayout):
		QGroupBox = self._addGroupBox(QLayout, 'Builder')

	def _addGroupBox(self, QLayout, title):
		QGroupBox = QtGui.QGroupBox()
		QGroupBox.setTitle(title)
		QLayout.addWidget(QGroupBox)
		return QGroupBox

	def _getProjects(self):
		fileList = assets.listAllProject()
		return fileList

	def _getAssets(self):
		project = self.QLineEditProject.text()
		if project:
			fileList = assets.listAllAsset(project)
		else:
			fileList = []
		return fileList

	def _addAttributeFromDict(self, attrDict):
		for key, value in attrDict.items():
			setattr(self, key, value)
