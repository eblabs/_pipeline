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

# -- import rigSys widget
import rigInfoListView

# rig info menu
# right clicked on rig info line edit
# rig info menu will pop out
# with a filter and list view to set rig info

class RigInfoMenu(QtGui.QMenu):
	"""docstring for RigInfoMenu"""
	def __init__(self, size=[200,300], filterName='Project', fileList=[], QPos=None, QWidget=None):
		super(RigInfoMenu, self).__init__(QWidget)
		self.size = size
		self.filterName = filterName
		self.fileList = fileList
		self.QPos = QPos
		self.QWidget = QWidget
		self.initWidget()

	def initWidget(self):
		self.setMinimumSize(self.size[0], self.size[1])
		QGridLayout = QtGui.QGridLayout(self)
		self.FileView = uiUtils.ListViewSearch(filterName = self.filterName, ListViewWidget = rigInfoListView.ListViewRigInfo)
		self._rebuildListModel()
		QGridLayout.addWidget(self.FileView)
		parentPosition = self.QWidget.mapToGlobal(QtCore.QPoint(0, 0))        
		self.move(parentPosition + self.QPos)

	def _rebuildListModel(self):
		self.FileView.QSourceModel.clear()
		for f in self.fileList:
			QItem = QtGui.QStandardItem(f)
			self.FileView.QSourceModel.appendRow(QItem)
		