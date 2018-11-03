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

# listViewSearch widget for rig info
class ListViewRigInfo(QtGui.QListView):
	"""docstring for ListViewSearchRigInfo"""
	QSignalClose = QtCore.Signal()
	QSignalSelect = QtCore.Signal(str)
	def __init__(self, *arg, **kwargs):
		super(ListViewRigInfo, self).__init__(*arg, **kwargs)

	def keyPressEvent(self, event):
		if (event.key() == QtCore.Qt.Key_Escape and
			event.modifiers() == QtCore.Qt.NoModifier):
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		else:
			QtGui.QListView.keyPressEvent(self, event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		QtGui.QListView.mousePressEvent(self, event)
		name = self.currentIndex().data()
		self.QSignalSelect.emit(name)

	def mouseDoubleClickEvent(self, event):
		self.QSignalClose.emit()
