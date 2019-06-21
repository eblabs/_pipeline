# =================#
# IMPORT PACKAGES  #
# =================#

# import ast
import ast

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
class DictAttrWidget(baseAttrWidget.BaseAttrWidget):
	"""base class for DictAttrWidget"""
	def __init__(self, **kwargs):
		super(DictAttrWidget, self).__init__(**kwargs)

	def add_attr_widget(self):
		self._widget = QLineEdit(str(self._val))
		super(DictAttrWidget, self).add_attr_widget()

	def _build_right_click_menu(self):
		super(DictAttrWidget, self)._build_right_click_menu()
		action_data = self.right_menu.addAction('List Data')
		action_data.connect(action_data, SIGNAL("triggered()"), self.list_data_menu)
	
	def list_data_menu(self):
		val = self._widget.text()
		self._attrValue = ast.literal_eval(val)
		try:
			self.data_menu.close()
		except:
			pass
		import attrWidget
		self.data_menu = attrWidget.AttrWidget(self._attrValue)
		self.data_menu.show()