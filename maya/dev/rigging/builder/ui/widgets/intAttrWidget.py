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
class IntAttrWidget(baseAttrWidget.BaseAttrWidget):
	"""base class for IntAttrWidget"""
	def __init__(self, **kwargs):
		super(IntAttrWidget, self).__init__(**kwargs)

	def add_attr_widget(self):
		self._widget = QSpinBox()
		self._widget.setValue(self._val)
		super(IntAttrWidget, self).add_attr_widget()

