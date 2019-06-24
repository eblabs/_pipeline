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

import ast

valueRole = Qt.UserRole + 1
defaultRole = valueRole +1

class DataWdiget(QTreeView):
	"""docstring for DataWdiget"""

	def __init__(self):
		super(DataWdiget, self).__init__()

		self._data = [{'attr1': 'text1'},
					  {'attr2': 3.0},
					  {'attr3': 5},
					  {'attr4': False},
					  {'attr5': ['path1', 'path2', 'path3']},
					  {'attr6': {'key1': 'val1',
								 'key2': 'val2',
								 'key3': 'val3'}},
					  {'attr7': [{'dict1': {'key1': 'attr1', 'key2': 'attr2'}},
								 {'dict2': {'key1': 'attr1',
										   'key2': 'attr2'}}]},
					  {'attr8': {'key1': ['path1', 'path2'],
								 'key2': {'key1': 'val1',
										  'key2': 'val2'}}}]

		self.init_widget()
		self.assign_data()

	def init_widget(self):
		# QHeader = QTreeWidgetItem(['Attribute', 'Value'])
		# self.setHeaderItem(QHeader)
		# self.setRootIsDecorated(True)
		# self.setAlternatingRowColors(True)
		self.setHeaderHidden(False)
		#self.setUniformRowHeights(True)
		delegate = AttrDelegate(self)
		delegate.QSignelCollectData.connect(self._collect_data)
		delegate.QSignelRebuildData.connect(self._rebuild_data)
		
		
		#self.header().setSectionResizeMode(0, QHeaderView.Stretch)
		self.header().setStretchLastSection(True)

		self._model = QStandardItemModel(0,2)
		self._model.setHeaderData(0, Qt.Horizontal, 'Attribute')
		self._model.setHeaderData(1, Qt.Horizontal, 'Value')
		# size
		# size = QSize(20,500)
		# index = self._model.index(0,0)
		# self._model.setData(index, size, Qt.SizeHintRole)
		self.setModel(self._model)

		self.setItemDelegate(delegate)

		
		
	def assign_data(self):
		for attrDict in self._data:
			self._assign_data(self._model, attrDict)
			'''
			key = attrDict.keys()[0]
			val = attrDict[key]
			column_attr = QStandardItem(key)
			column_attr.setEditable(False)
			column_val = QStandardItem(str(val))

			self._model.appendRow([column_attr, column_val])

			if isinstance(val, dict):
				for key, val in val.iteritems():
					attr = QStandardItem(key)
					attr.setEditable(False)
					val = QStandardItem(str(val))
					column_attr.appendRow([attr, val])
			'''

	def _assign_data(self, model, data):
		size=QSize(20,20)
		if isinstance(data, list):
			for i, item in enumerate(data):
				# add each item
				column_attr = QStandardItem(str(i+1))
				column_attr.setEditable(False)
				column_attr.setData(size, role=Qt.SizeHintRole)

				column_val = QStandardItem(str(item))
				column_val.setData('value', role=valueRole)
				column_val.setData(str(item), role=defaultRole)
				column_val.setData(size, role=Qt.SizeHintRole)

				model.appendRow([column_attr, column_val])

				self._assign_data(column_attr, item)

		elif isinstance(data, dict):
			for key, item in data.iteritems():
				column_attr = QStandardItem(key)
				column_attr.setEditable(False)
				column_attr.setData(size, role=Qt.SizeHintRole)
				column_val = QStandardItem(str(item))
				column_val.setData('value', role=valueRole)
				column_val.setData(str(item), role=defaultRole)
				column_val.setData(size, role=Qt.SizeHintRole)

				model.appendRow([column_attr, column_val])

				self._assign_data(column_attr, item)

	def _collect_data(self, item):
		# get item parent
		parent = item.parent()
		if parent:
			# get index
			index_parent = parent.index()
			# get value index
			index_value = self._model.index(parent.row(), 1, parent=index_parent.parent())
			# get value
			value = self._convert_data(self._model.data(index_value))
			# get childs row count
			row_childs = parent.rowCount()
			# create empty container for update val
			if isinstance(value, list):
				value_collect = []
			else:
				value_collect = {}
			# loop in each row
			for i in range(row_childs):
				index_attr = self._model.index(i, 0, parent=index_parent)
				index_val = self._model.index(i, 1, parent=index_parent)
				attr = str(self._model.data(index_attr))
				val = self._convert_data(self._model.data(index_val))
				if isinstance(value, list):
					value_collect.append(val)
				else:
					value_collect.update({attr: val})
			# assign data
			if value != value_collect:
				self._model.setData(index_value, str(value_collect))

			# loop to upper level
			self._collect_data(self._model.itemFromIndex(index_parent))

	def _rebuild_data(self, item):
		index_value = item.index()
		index_attr = self._model.index(item.row(), 0, parent=index_value.parent())
		# get value
		value = self._convert_data(self._model.data(index_value))
		
		if isinstance(value, list) or isinstance(value, dict):
			item_attr = self._model.itemFromIndex(index_attr)
			# clear out the childs
			rows = item_attr.rowCount()
			item_attr.removeRows(0, rows)
			# rebuild
			self._assign_data(item_attr, value)

	def _convert_data(self, data):
		try:
			data = ast.literal_eval(str(data))
		except:
			data = str(data)
		return data
	'''
	def drawRow(self, painter, option, index):
		super(DataWdiget, self).drawRow(painter, option, index)
		painter.setPen(Qt.lightGray)
		y = option.rect.y()
		#saving is mandatory to keep alignment through out the row painting
		painter.save()
		painter.translate(self.visualRect(self.model().index(0, 0)).x() - self.indentation() - .5, -.5)
		for sectionId in range(self.header().count() - 1):
			painter.translate(self.header().sectionSize(sectionId), 0)
			painter.drawLine(0, y, 0, y + option.rect.height())
		painter.restore()
		#don't draw the line before the root index
		if index == self.model().index(0, 0):
			return
		painter.drawLine(0, y, option.rect.width(), y)
	'''





class AttrDelegate(QItemDelegate):
	"""docstring for AttrDelegate"""
	QSignelCollectData = Signal(QStandardItem)
	QSignelRebuildData = Signal(QStandardItem)

	def __init__(self, parent=None):
		super(AttrDelegate, self).__init__(parent)
		
	def createEditor(self, parent, option, index):
		value = index.model().data(index)
		try:
			value = ast.literal_eval(str(value))
		except:
			pass

		if isinstance(value, basestring):
			line_edit = QLineEdit(parent)
			return line_edit
		elif isinstance(value, float):
			spin_double_box = QDoubleSpinBox(parent)
			return spin_double_box		
		elif value in [True, False]:
			check_box = QCheckBox(parent)
			return check_box
		elif isinstance(value, int):
			spin_box = QSpinBox(parent)
			return spin_box
		elif isinstance(value, list):
			line_edit = QLineEdit(parent)
			return line_edit
		elif isinstance(value, dict):
			line_edit = QLineEdit(parent)
			return line_edit

	def setEditorData(self, editor, index):
		super(AttrDelegate, self).setEditorData(editor, index)

	def setModelData(self, editor, model, index):
		super(AttrDelegate, self).setModelData(editor, model, index)
		item = model.itemFromIndex(index)
		print 'setModelData'
		print item.data(role=valueRole)
		print item.data(role=defaultRole)
		self.QSignelCollectData.emit(model.itemFromIndex(index))
		self.QSignelRebuildData.emit(model.itemFromIndex(index))
	




		
	
win = DataWdiget()
win.show()