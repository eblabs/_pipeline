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

# import lib
import lib.common.packages as packages

class RigBuildInfoTreeWidget(QtGui.QTreeWidget):
	"""docstring for RigBuilderTreeWidget"""
	def __init__(self, *args, **kwargs):
		super(RigBuildInfoTreeWidget, self).__init__(*args, **kwargs)
		self.initWidget()

		# rig info
		self.project = None
		self.asset = None
		self.rig = None
		self.mode = 'publish'

	def initWidget(self):
		QHeader = QtGui.QTreeWidgetItem(['Function', 'Status'])
		self.setHeaderItem(QHeader)
		self.setRootIsDecorated(False)
		self.setAlternatingRowColors(True)
		self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.setHeaderHidden(True)
		self.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
		self.header().setStretchLastSection(False)
		self.setColumnWidth(1,40)

		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self._rightClickedMenu)

	def _rightClickedMenu(self, QPos):
		QMenu= QtGui.QMenu(self)
		QAction_execute = QMenu.addAction('Execute')
		QAction_refresh = QMenu.addAction('Refresh')
		QAction_rebuild = QMenu.addAction('Rebuild')

		parentPosition = self.mapToGlobal(QtCore.QPoint(0, 0))        
		QMenu.move(parentPosition + QPos)

		QMenu.show()
		
	def keyPressEvent(self, event):
		if (event.key() == QtCore.Qt.Key_Escape and
			event.modifiers() == QtCore.Qt.NoModifier):
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		else:
			QtGui.QTreeWidget.keyPressEvent(self, event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		super(RigBuildInfoTreeWidget, self).mousePressEvent(event)

	def mouseDoubleClickEvent(self, event):
		pass
		