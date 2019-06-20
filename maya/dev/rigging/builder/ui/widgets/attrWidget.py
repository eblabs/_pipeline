#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

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

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#
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
		QLayoutBase = QVBoxLayout(self)
		self.setLayout(QLayoutBase)

		# attributes layout
		QGroupBoxAttr = QGroupBox()
		QGroupBoxAttr.setTitle('Attributes')
		QLayoutBase.addWidget(QGroupBoxAttr)

		## form layout
		self._QFormLayoutAttr = QFormLayout(QGroupBoxAttr)

	def _add_attrs(self):
		for key, item in self._kwargs.iteritems():
			if isinstance(item, float):
				self._add_float_attr(key, item)
			elif isinstance(item, basestring):
				self._add_string_attr(key, item)
			elif item in [True, False]:
				self._add_bool_attr(key, item)
			elif isinstance(item, int):
				self._add_int_attr(key, item)
				

	def _add_float_attr(self, attr, value):
		QFloatAttr = QDoubleSpinBox()
		QFloatAttr.setDecimals(3)
		QFloatAttr.setValue(value)
		self._QFormLayoutAttr.addRow(attr, QFloatAttr)

	def _add_string_attr(self, attr, value):
		QStringAttr = QLineEdit(value)
		self._QFormLayoutAttr.addRow(attr, QStringAttr)

	def _add_int_attr(self, attr, value):
		QIntAttr = QSpinBox()
		QIntAttr.setValue(value)
		self._QFormLayoutAttr.addRow(attr, QIntAttr)

	def _add_bool_attr(self, attr, value):
		QCheckBoxAttr = QCheckBox()
		QCheckBoxAttr.setEnabled(value)
		if value:
			QCheckBoxAttr.setCheckState(Qt.Checked)
		else:
			QCheckBoxAttr.setCheckState(Qt.Unchecked)
		self._QFormLayoutAttr.addRow(attr, QCheckBoxAttr)


