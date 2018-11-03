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

class AssetManager(uiUtils.BaseWindow):
	"""docstring for AssetManager"""
	def __init__(self, parent=None, title='Asset Manager', geometry=[100,100,100,100]):
		super(AssetManager, self).__init__(parent=parent, title=title, geometry=geometry)
	
	def initUI(self):
		super(AssetManager, self).initUI()

		# base layout - horizontal
		QLayoutBase = QtGui.QHBoxLayout(self)
		self.setLayout(QLayoutBase)

		# project

		# asset

		# set

		# file

		
