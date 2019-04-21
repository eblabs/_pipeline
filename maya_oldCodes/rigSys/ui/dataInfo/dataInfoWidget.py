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

# -- import rigSys widget
import dataInfoTreeWidget
reload(dataInfoTreeWidget)

class DataInfoWidget(QtGui.QGroupBox):
	"""docstring for DataInfoWidget"""
	def __init__(self, *args, **kwargs):
		super(DataInfoWidget, self).__init__(*args, **kwargs)
		self.setTitle('Data Info')
		self.setFixedWidth(340)

		self.initWidget()

	def initWidget(self):
		# base layout
		QVBoxLayout = QtGui.QVBoxLayout(self)

		# tree widget
		self.QTreeView = dataInfoTreeWidget.DataInfoTreeWidget()
		QVBoxLayout.addWidget(self.QTreeView)
		