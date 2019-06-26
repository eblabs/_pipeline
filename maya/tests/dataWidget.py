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

role_defaultValue = Qt.UserRole + 1
role_attrType = Qt.UserRole + 2
role_min = Qt.UserRole + 3
role_max = Qt.UserRole + 4
role_enum = Qt.UserRole + 5
role_template = Qt.UserRole + 6

itemType = {'strAttr': {'value': '',
						'widget': QLineEdit},
			'floatAttr': {'value': 0.0,
						  'min': None,
						  'max': None,
						  'widget': QDoubleSpinBox},
			'intAttr': {'value': 0,
						'min': None,
						'max': None,
						'widget': QSpinBox},
			'enumAttr': {'value': None,
						 'enumName': [],
						 'widget': QComboBox},
			'boolAttr': {'value': True,
						 'widget': QComboBox},
			'listAttr': {'value': [],
						 'template': '',
						 'widget': QLineEdit},
			'dictAttr': {'value': {},
						 'template': [],
						 'widget': QLineEdit}}

class DataWdiget(QTreeView):
	"""docstring for DataWdiget"""

	def __init__(self):
		super(DataWdiget, self).__init__()

		self._data = [{'attr1': {'value': 'text1'}},
					  {'attr2': {'value': 3.0,
					  			 'min': 0.0,
					  			 'max': 10.0}},
					  {'attr3': {'value': 5,
					  			 'min': 1}},
					  {'attr4': {'value':False}},
					  {'attr5': {'value': ['path1', 'path2', 'path3'],
					  			 'template': 'strAttr'}},
					  {'attr6': {'value': {'key1': 'val1',
								 		   'key2':  2.0,
								 		   'key3': 3},
								 'template': {'key1': 'strAttr',
								 			  'key2': 'floatAttr',
								 			  'key3': 'intAttr'}}},
					  {'attr7': {'value': 'option2',
					  			 'type': 'enumAttr',
					  			 'enumName': ['option1',
					  			 			  'option2',
					  			 			  'option3',
					  			 			  'option4']}}]

		self.init_widget()
		self.assign_data()

	def init_widget(self):
		# QHeader = QTreeWidgetItem(['Attribute', 'Value'])
		# self.setHeaderItem(QHeader)
		# self.setRootIsDecorated(True)
		self.setAlternatingRowColors(True)
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
		size=QSize(20,20)
		for attrDict in self._data:
			key = attrDict.keys()[0]
			attrInfo = attrDict[key]

			column_attr = QStandardItem(key)
			column_attr.setEditable(False)
			column_attr.setData(size, role=Qt.SizeHintRole)

			column_val = AttrItem(**attrInfo)
			column_val.setData(size, role=Qt.SizeHintRole)

			self._model.appendRow([column_attr, column_val])

			if isinstance(attrInfo['value'], list) or isinstance(attrInfo['value'], dict):

				template_item = column_val.data(role=role_template)

				self._assign_data(column_attr, attrInfo['value'], template=template_item)

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

	def _assign_data(self, model, data, template=None):
		size=QSize(20,20)
		if isinstance(data, list):		
			for i, item in enumerate(data):
				# add each item
				column_attr = QStandardItem(str(i))
				column_attr.setEditable(False)
				column_attr.setData(size, role=Qt.SizeHintRole)

				column_val = AttrItem(str(item), type=template)
				column_val.setData(size, role=Qt.SizeHintRole)

				model.appendRow([column_attr, column_val])

				template_item = column_val.data(role=role_template)

				self._assign_data(column_attr, item, template=template_item)

		elif isinstance(data, dict):
			for key, item in data.iteritems():
				column_attr = QStandardItem(key)
				column_attr.setEditable(False)
				column_attr.setData(size, role=Qt.SizeHintRole)

				if template and key in template:
					attr_type = template[key]
				else:
					attr_type = None

				column_val = AttrItem(str(item), type=attr_type)
				column_val.setData(size, role=Qt.SizeHintRole)

				model.appendRow([column_attr, column_val])

				template_item = column_val.data(role=role_template)

				self._assign_data(column_attr, item, template=template_item)

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
		item = index.model().itemFromIndex(index)
		attrType = item.data(role=role_attrType)

		value = index.data()

		widget = itemType[attrType]['widget'](parent)

		# extra setting
		if isinstance(widget, QComboBox):
			enumName = item.data(role=role_enum)
			widget.addItems(enumName)
			enumIndex = widget.findText(value, Qt.MatchFixedString)
			widget.setCurrentIndex(enumIndex)
		elif isinstance(widget, QDoubleSpinBox) or isinstance(widget, QSpinBox):
			minVal = item.data(role=role_min)
			maxVal = item.data(role=role_max)
			if minVal:
				widget.setMinimum(minVal)
			if maxVal:
				widget.setMaximum(maxVal)
		elif isinstance(widget, QLineEdit):
			widget.setFrame(False)

		return widget

	def setEditorData(self, editor, index):
		super(AttrDelegate, self).setEditorData(editor, index)

	def setModelData(self, editor, model, index):
		super(AttrDelegate, self).setModelData(editor, model, index)
		item = model.itemFromIndex(index)
		self.QSignelCollectData.emit(model.itemFromIndex(index))
		self.QSignelRebuildData.emit(model.itemFromIndex(index))

	'''
	def paint(self, painter, option, index):
		super(AttrDelegate, self).paint(painter, option, index)
		painter.save()
		painter.setPen(Qt.black)
		painter.drawRect(option.rect)
		painter.restore()
	'''

class AttrItem(QStandardItem):
	"""docstring for AttrItem"""
	def __init__(self, *args, **kwargs):
		super(AttrItem, self).__init__()

		self._attrVal = kwargs.get('value', None)
		self._attrType = kwargs.get('type', None)
		self._enumName = kwargs.get('enumName', [])
		self._min = kwargs.get('min', None)
		self._max = kwargs.get('max', None)
		self._template = kwargs.get('template', None)
		self._hint = kwargs.get('hint', '')

		if args:
			self._attrVal = args[0]
		
		self._set_data()

		self.setEditable(True)

	def _set_data(self):
		data_info = {'value': None,
					 'min': None,
					 'max': None,
					 'enumName': None,
					 'template': None,
					 'type': None,
					 'hint': ''}
		
		if not self._attrType:
			if self._attrVal in [True, False]:
				self._attrType = 'boolAttr'
				self._enumName = ['True', 'False']
			elif isinstance(self._attrVal, float):
				self._attrType = 'floatAttr'
			elif isinstance(self._attrVal, int):
				self._attrType = 'intAttr'
			elif isinstance(self._attrVal, list):
				self._attrType = 'listAttr'
			elif isinstance(self._attrVal, dict):
				self._attrType = 'dictAttr'
			elif isinstance(self._attrVal, basestring):
				self._attrType = 'strAttr'
			else:
				return

		for key, item in itemType[self._attrType].iteritems():
			data_info.update({key: item})

		data_info['type'] = self._attrType

		if self._attrVal:
			data_info['value'] = self._attrVal
		if self._min:
			data_info['min'] = self._min
		if self._max:
			data_info['max'] = self._max
		if self._enumName:
			data_info['enumName'] = self._enumName
		if self._template:
			data_info['template'] = self._template
		if self._hint:
			data_info['hint'] = self._hint

		self.setText(str(data_info['value']))

		self.setData(str(data_info['value']), role=role_defaultValue)
		self.setData(data_info['type'], role_attrType)
		self.setData(data_info['min'], role_min)
		self.setData(data_info['max'], role_max)
		self.setData(data_info['enumName'], role_enum)
		self.setData(data_info['template'], role_template)
		if data_info['hint']:
			self.setData(data_info['hint'], Qt.ToolTipRole)



		


		




		
	
win = DataWdiget()
win.show()