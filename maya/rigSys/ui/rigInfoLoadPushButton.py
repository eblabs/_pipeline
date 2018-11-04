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
import lib.common.uiUtils as uiUtils
import assets.lib.assets as assets
import assets.lib.rigs as rigs
# ---- import end ----

class RigInfoLoadPushButton(QtGui.QPushButton):
	"""docstring for RigInfoLoadPushButton"""
	def __init__(self, versionsList=[], *args, **kwargs):
		super(RigInfoLoadPushButton, self).__init__(*args, **kwargs)
		self.checked = 'publish'
		self.versionsList = versionsList
		self.initWidget()
		
	def initWidget(self):
		self.setText('Load')
		self.setMinimumHeight(40)
		self.setEnabled(False)

		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self._rightClickedMenu)

	def _rightClickedMenu(self, QPos):

		QMenu = QtGui.QMenu(self)
		# mode
		
		actionDict = {}

		QAction_publish = QtGui.QAction('publish', QMenu, checkable=True)
		QAction_wip = QtGui.QAction('wip', QMenu, checkable=True)

		self.QActionGroup = QtGui.QActionGroup(QMenu)

		for QAction in [QAction_publish, QAction_wip]:
			QMenu.addAction(QAction)
			self.QActionGroup.addAction(QAction)
			actionDict.update({QAction.text(): QAction})

		QMenu_version = QMenu.addMenu('version')

		for version in self.versionsList:
			QAction_version = QtGui.QAction(version, QMenu_version, checkable=True)
			QMenu_version.addAction(QAction_version)
			self.QActionGroup.addAction(QAction_version)
			actionDict.update({QAction_version.text(): QAction_version})

		if self.checked in actionDict:
			QAction_checked = actionDict[self.checked]
		else:
			QAction_checked = actionDict['publish']
		QAction_checked.setChecked(True)
		
		QMenu.addSeparator()
		QMenuItem_create = QMenu.addAction("Create")

		self.QActionGroup.triggered.connect(self._setMode)

		parentPosition = self.mapToGlobal(QtCore.QPoint(0, 0))        
		QMenu.move(parentPosition + QPos)

		QMenu.show()

	def _setMode(self):
		QAction_checked = self.QActionGroup.checkedAction()
		self.checked = QAction_checked.text()

		