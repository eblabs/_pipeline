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
import baseAttrWidget

# =================#
#   GLOBAL VARS   #
# =================#
from . import Logger

# =================#
#      CLASS      #
# =================#
class ListAttrWidget(baseAttrWidget.BaseAttrWidget):
	"""base class for ListAttrWidget"""
	def __init__(self, **kwargs):
		super(ListAttrWidget, self).__init__(**kwargs)

	def add_attr_widget(self):
		self._widget = QLineEdit(str(self._val))
		super(ListAttrWidget, self).add_attr_widget()

	def _build_right_click_menu(self):
		super(ListAttrWidget, self)._build_right_click_menu()
		action_items = self.right_menu.addAction('List Items')
		action_items.connect(action_items, SIGNAL("triggered()"), self.list_data_menu)
	
	def list_items_menu(self):
		pass