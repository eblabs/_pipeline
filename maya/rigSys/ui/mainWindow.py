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

# -- import maya lib
import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI

# -- import lib
import lib.common.uiUtils as uiUtils
reload(uiUtils)
# ---- import end ----

class MainWindow(uiUtils.BaseWindow):
	"""docstring for MainWindow"""
	def __init__(self, parent=None, title='Window', geometry=[100,100,100,100]):
		super(MainWindow, self).__init__(parent=parent, title=title, geometry=geometry)
		
	def initUI(self):
		super(MainWindow, self).initUI()

		# base layout - vertical
		QLayoutBase = QtGui.QHBoxLayout(self)
		self.setLayout(QLayoutBase)

		# left layout - horizontal
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
		self._publishUI(QLayoutLeft)

		# builder ui (right side)
		self._builderUI(QLayoutRight)

	def _rigInfoUI(self, QLayout):
		QGroupBox = self._addGroupBox(QLayout, 'Rig Info')
		QGroupBox.setFixedHeight(160)
		# rig info labels
		QVBoxLayout = QtGui.QVBoxLayout(QGroupBox)

		for name in ['Project', 'Asset', 'Rig']:
			QHBoxLayout = QtGui.QHBoxLayout()
			QVBoxLayout.addLayout(QHBoxLayout)

			QLabelName = QtGui.QLabel(name + ':')
			QLineEditInfo = QtGui.QLineEdit()
			QHBoxLayout.addWidget(QLabelName)
			QHBoxLayout.addWidget(QLineEditInfo)

		QPushButton = QtGui.QPushButton('Load')
		QPushButton.setMinimumHeight(40)
		#QPushButton.setFixedWidth()
		#QPushButton.setEnabled(False)
		#QPushButton.setStyleSheet('background-color:rgb(255,100,100)')
		QVBoxLayout.addWidget(QPushButton)

	def _dataUI(self, QLayout):
		QGroupBox = self._addGroupBox(QLayout, 'Rig Data')
		QGroupBox.setMinimumHeight(260)

		# tab widget
		QGridLayout = QtGui.QGridLayout(QGroupBox)

		QTabWidget = QtGui.QTabWidget()
		QGridLayout.addWidget(QTabWidget)

		# data info
		QWidgetInfo = QtGui.QWidget()
		QTabWidget.addTab(QWidgetInfo, 'Info')

		# data edit
		QWidgetEdit = QtGui.QWidget()
		QTabWidget.addTab(QWidgetEdit, 'Edit')

	def _publishUI(self, QLayout):
		QGroupBox = self._addGroupBox(QLayout, 'Publish')

		QVBoxLayout = QtGui.QVBoxLayout(QGroupBox)

		# tag
		QHBoxLayoutTag = QtGui.QHBoxLayout()
		QVBoxLayout.addLayout(QHBoxLayoutTag)
		QLabelTag = QtGui.QLabel('Tag:')
		QLineEditTag = QtGui.QLineEdit()
		QHBoxLayoutTag.addWidget(QLabelTag)
		QHBoxLayoutTag.addWidget(QLineEditTag)

		# comment
		QVBoxLayoutComment = QtGui.QVBoxLayout()
		QVBoxLayout.addLayout(QVBoxLayoutComment)

		QLabelComment = QtGui.QLabel('Comment:')
		QLabelComment.setMaximumHeight(20)
		QVBoxLayoutComment.addWidget(QLabelComment)

		QLineEditComment = QtGui.QLineEdit()
		QLineEditComment.setMinimumHeight(100)
		QLineEditComment.setAlignment(QtCore.Qt.AlignTop)
		QVBoxLayoutComment.addWidget(QLineEditComment)

		# button
		QPushButton = QtGui.QPushButton('Publish')
		QPushButton.setMinimumHeight(40)
		#QPushButton.setStyleSheet('background-color:rgb(255,100,100)')
		QVBoxLayout.addWidget(QPushButton)

	def _builderUI(self, QLayout):
		QGroupBox = self._addGroupBox(QLayout, 'Builder')

	def _addGroupBox(self, QLayout, title):
		QGroupBox = QtGui.QGroupBox()
		QGroupBox.setTitle(title)
		QLayout.addWidget(QGroupBox)
		return QGroupBox
		
