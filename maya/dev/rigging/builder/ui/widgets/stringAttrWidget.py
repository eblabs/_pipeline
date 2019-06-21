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
class StringAttrWidget(baseAttrWidget.BaseAttrWidget):
	"""base class for StringAttrWidget"""
	def __init__(self, **kwargs):
		super(StringAttrWidget, self).__init__(**kwargs)

	def add_attr_widget(self):
		self._widget = QLineEdit(self._val)
		super(StringAttrWidget, self).add_attr_widget()


		
