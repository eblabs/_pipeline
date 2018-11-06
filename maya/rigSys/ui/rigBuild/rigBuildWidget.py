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
import rigBuildInfoTreeWidget
reload(rigBuildInfoTreeWidget)

class RigBuildWidget(QtGui.QGroupBox):
	"""docstring for RigBuilderWidget"""
	def __init__(self, *args, **kwargs):
		super(RigBuildWidget, self).__init__(*args, **kwargs)
		self.setTitle('Rig Builder')

		self.initWidget()

	def initWidget(self):
		# base layout
		QVBoxLayout = QtGui.QVBoxLayout(self)

		# tree widget
		self.QTreeWidget = rigBuildInfoTreeWidget.RigBuildInfoTreeWidget()
		QVBoxLayout.addWidget(self.QTreeWidget)
		
		