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

# =================#
#   GLOBAL VARS   #
# =================#
from . import Logger


# =================#
#      CLASS      #
# =================#
class BaseAttrWidget(QWidget):
	"""
	base class for BaseAttrWidget
	all the attr widgets should be
	inheritaned from this class
	"""
	def __init__(self, **kwargs):
		super(BaseAttrWidget, self).__init__()
		self._widget = QWidget()
		self._attr = kwargs.get('attr', 'attr')
		self._val = kwargs.get('value', '')
		self.init_widget()
		self.add_attr_widget()
		self.connect_right_click_menu()

	def init_widget(self):
		self._form_layout = QFormLayout(self)
		self.setLayout(self._form_layout)

		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.right_click_menu)

	def add_attr_widget(self):
		self._form_layout.addRow(self._attr+':', self._widget)

	def right_click_menu(self, QPos):
		self._build_right_click_menu()
		pos = self.mapToGlobal(QPoint(0, 0))        
		self.right_menu.move(pos + QPos)
		self.right_menu.show()
		
	def _build_right_click_menu(self):
		self.right_menu= QMenu(self)
		action_reset = self.right_menu.addAction('Reset')

	def connect_right_click_menu(self):
		self._widget.setContextMenuPolicy(Qt.CustomContextMenu)
		self._widget.customContextMenuRequested.connect(self.right_click_menu)


