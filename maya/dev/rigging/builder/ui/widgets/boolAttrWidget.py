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
class BoolAttrWidget(baseAttrWidget.BaseAttrWidget):
	"""base class for BoolAttrWidget"""
	def __init__(self, **kwargs):
		super(BoolAttrWidget, self).__init__(**kwargs)

	def add_attr_widget(self):
		self._widget = QCheckBox()
		#self._widget.setEnabled(self._val)
		if self._val:
			self._widget.setCheckState(Qt.Checked)
		else:
			self._widget.setCheckState(Qt.Unchecked)
		super(BoolAttrWidget, self).add_attr_widget()

