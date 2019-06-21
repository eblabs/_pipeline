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
class FloatAttrWidget(baseAttrWidget.BaseAttrWidget):
	"""base class for FloatAttrWidget"""
	def __init__(self, **kwargs):
		super(FloatAttrWidget, self).__init__(**kwargs)

	def add_attr_widget(self):
		self._widget = QDoubleSpinBox()
		self._widget.setDecimals(3)
		self._widget.setValue(self._val)
		super(FloatAttrWidget, self).add_attr_widget()

