# =================#
# IMPORT PACKAGES  #
# =================#

# import PySide
try:
	from PySide2.QtCore import *
	from PySide2.QtGui import *
	from PySide2.QtWidgets import *
	from PySide2 import __version__
	from shiboken2 import wrapInstance
except ImportError:
	from PySide.QtCore import *
	from PySide.QtGui import *
	from PySide import __version__
	from shiboken import wrapInstance

# =================#
#   GLOBAL VARS   #
# =================#
from . import Logger

# =================#
#      CLASS      #
# =================#
class ListItemsWidget(QListView):
	"""docstring for ListAttrWidget"""
	def __init__(self, kwargs):
		super(ListItemsWidget, self).__init__()

		
