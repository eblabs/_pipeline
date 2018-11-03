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
import rigInfoMenu
reload(rigInfoMenu)

# rig info line eidt widget
# have QMenu contain a filter and list view widget
class RigInfoLineEdit(QtGui.QLineEdit):
	"""docstring for RigInfoLineEdit"""
	def __init__(self, name='Project', fileMethod=None, menuSize=[200,300], *arg, **kwargs):
		super(RigInfoLineEdit, self).__init__(*arg, **kwargs)
		self.name = name
		self.menuSize = menuSize
		self.fileMethod = fileMethod

		self.initWidget()
	
	def initWidget(self):
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self._rightClickedMenu)

	def _rightClickedMenu(self, QPos):
		self.fileList = self.fileMethod()

		RigInfoMenu = rigInfoMenu.RigInfoMenu(size=self.menuSize, 
											  filterName=self.name, 
											  fileList=self.fileList,
											  QPos = QPos,
											  QWidget = self)
		# set filter text to QLineEdit text automatically
		text = self.text()
		RigInfoMenu.FileView.QLineEditFilter.setText(text)

		# connect double click to close menu
		# connect single click to set name
		RigInfoMenu.FileView.QListView.QSignalClose.connect(RigInfoMenu.close)
		RigInfoMenu.FileView.QListView.QSignalSelect.connect(self._setRigInfoText)

		# show menu
		RigInfoMenu.show()

	def _setRigInfoText(self, rigInfo):
		if rigInfo:
			self.setText(rigInfo)


		