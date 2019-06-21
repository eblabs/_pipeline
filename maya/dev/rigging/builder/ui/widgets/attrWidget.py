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

# import attr widgets
import boolAttrWidget
import dictAttrWidget
import floatAttrWidget
import intAttrWidget
import listAttrWidget
import stringAttrWidget

# =================#
#   GLOBAL VARS   #
# =================#
from . import Logger


# =================#
#      CLASS      #
# =================#
class AttrWidget(QWidget):
	"""
	base class for AttrWidget
	use this class to add attrs dynamically
	"""

	def __init__(self, kwargs):
		super(AttrWidget, self).__init__()
		self._kwargs = kwargs

		self._init_widget()
		self._add_attrs()

	def _init_widget(self):
		# base layout -vertical
		self._layout_base = QVBoxLayout(self)
		self.setLayout(self._layout_base)

	def _add_attrs(self):
		for key, item in self._kwargs.iteritems():
			kwargs = {'attr': key,
					  'value': item}
			if isinstance(item, basestring) or item==None:
				self._add_string_attr(**kwargs)
			elif isinstance(item, float):
				self._add_float_attr(**kwargs)			
			elif item in [True, False]:
				self._add_bool_attr(**kwargs)
			elif isinstance(item, int):
				self._add_int_attr(**kwargs)
			elif isinstance(item, list):
				self._add_list_attr(**kwargs)
			elif isinstance(item, dict):
				self._add_dict_attr(**kwargs)

	def _add_float_attr(self, **kwargs):
		float_widget = floatAttrWidget.FloatAttrWidget(**kwargs)
		self._layout_base.addWidget(float_widget)

	def _add_string_attr(self, **kwargs):
		string_widget = stringAttrWidget.StringAttrWidget(**kwargs)
		self._layout_base.addWidget(string_widget)

	def _add_int_attr(self, **kwargs):
		int_widget = intAttrWidget.IntAttrWidget(**kwargs)
		self._layout_base.addWidget(int_widget)

	def _add_bool_attr(self, **kwargs):
		bool_widget = boolAttrWidget.BoolAttrWidget(**kwargs)
		self._layout_base.addWidget(bool_widget)

	def _add_list_attr(self, **kwargs):
		list_widget = listAttrWidget.ListAttrWidget(**kwargs)
		self._layout_base.addWidget(list_widget)

	def _add_dict_attr(self, **kwargs):
		dict_widget = dictAttrWidget.DictAttrWidget(**kwargs)
		self._layout_base.addWidget(dict_widget)
