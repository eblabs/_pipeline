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

# get maya main window
def getMayaWindow():
	ptr = OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(ptr), QtGui.QMainWindow)

# base ui
class BaseWindow(QtGui.QWidget):
	"""docstring for baseWindow"""
	def __init__(self, parent=None, title='Window', geometry=[100,100,100,100]):
		super(BaseWindow, self).__init__()
		
		# Parent widget       
		self.setParent(parent)       
		self.setWindowFlags(QtCore.Qt.Window)

		# Set the object name
		self.setObjectName(title.replace(' ', '') + '_uniqueId')        
		self.setWindowTitle(title)        
		self.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3]) 
		
		# initialize Ui
		self.initUI()

	def initUI(self):
		pass
		
