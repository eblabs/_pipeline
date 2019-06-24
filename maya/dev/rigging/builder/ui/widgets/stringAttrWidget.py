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
class StringAttrWidget(baseAttrWidget.BaseAttrWidget):
	"""base class for StringAttrWidget"""
	def __init__(self, **kwargs):
		super(StringAttrWidget, self).__init__(**kwargs)

	def add_attr_widget(self):
		self._widget = QLineEdit(str(self._val))
		self._widget.setFrame(False)
		super(StringAttrWidget, self).add_attr_widget()

	def _get_input_value(self):
		val = self._widget.text()
		self._val = ast.literal_eval(val)


		
