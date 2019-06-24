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

# import baseAttrWidget
import stringAttrWidget

# =================#
#   GLOBAL VARS   #
# =================#
from . import Logger

# =================#
#      CLASS      #
# =================#
class ListAttrWidget(stringAttrWidget.StringAttrWidget):
	"""base class for ListAttrWidget"""
	def __init__(self, **kwargs):
		super(ListAttrWidget, self).__init__(**kwargs)

	def _build_right_click_menu(self):
		super(ListAttrWidget, self)._build_right_click_menu()
		action_data = self.right_menu.addAction('Edit Data')
		action_data.connect(action_data, SIGNAL("triggered()"), self.list_data_menu)
	
	def list_data_menu(self):
		pass