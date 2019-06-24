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

class ListViewAttr(QTreeView):
	"""docstring for ListViewAttr"""
	def __init__(self):
		super(ListViewAttr, self).__init__()
		self.init_widget()
		
	def init_widget(self):
		self._model = QStandardItemModel(0,2)
		self.setModel(self._model)
		self._model.setHeaderData(0, Qt.Horizontal, 'Attribute')
		self._model.setHeaderData(1, Qt.Horizontal, 'Value')

		attrInfo = [['attr1', 'val1'],
					['attr2', 'val2'],
					['attr3', 'val3']]

		for key, val in attrInfo:
			column_attr = QStandardItem(key)
			column_attr.setEditable(False)
			column_val = QStandardItem(str(val))

			self._model.appendRow([column_attr, column_val])