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

# import ast
import ast

# =================#
#   GLOBAL VARS   #
# =================#
from . import Logger

from config.PROPERTY_ITEMS import PROPERTY_ITEMS 

ROLE_VALUE = Qt.UserRole + 1
ROLE_TYPE = Qt.UserRole + 2
ROLE_MIN = Qt.UserRole + 3
ROLE_MAX = Qt.UserRole + 4
ROLE_ENUM = Qt.UserRole + 5
ROLE_TEMPLATE = Qt.UserRole + 6

# =================#
#      CLASS       #
# =================#

class PropertyEditor(QTreeView):
	"""base class for PropertyEditor"""
	def __init__(self, data):
		super(PropertyEditor, self).__init__()
		self._property = data
		self._size = QSize(20,20)

		self._init_widget()
		self._set_data()

	def _init_widget(self):
		# different color each row
		self.setAlternatingRowColors(True) 
		# show header so user can adjust the first column width
		self.setHeaderHidden(False)
		# last section stretch
		self.header().setStretchLastSection(True)

		# QStandardItemModel
		self._model = QStandardItemModel(0,2)
		self._model.setHeaderData(0, Qt.Horizontal, 'Properties')
		self._model.setHeaderData(1, Qt.Horizontal, '')
		self.setModel(self._model)

		# delegate
		delegate = PropertyDelegate(self)
		delegate.QSignelUpdateParent.connect(self._update_parent)
		delegate.QSignelRebuildChild.connect(self._rebuild_child)

		self.setItemDelegate(delegate)

	def _init_property(self):
		'''
		initialize property
		'''
		for propertyInfo in self._property:
			key = propertyInfo.keys()[0]
			data = propertyInfo[key]

			# add row item
			row, template_child = self._add_row_item(key, itemKwargs=data)

			# add row
			self._model.appendRow(row)

			# loop downstream
			self._add_child(row[0], data['value'], template=template_child)

	def _add_child(self, item, data, template=None):
		if isinstance(data, list):
			# loop in each item in list	
			for i, val in enumerate(data):
				row, template_child = self._add_row_item(str(i), val=val, 
														 itemKwargs={'type':template})

				# add row
				item.appendRow(row)

				# loop downstream
				self._add_child(row[0], val, template=template_child)

		elif isinstance(data, dict):
			for key, val in data.iteritems():

				if template and key in template:
					attrType = template[key]
				else:
					attrType = None

				row, template_child = self._add_row_item(key, val=val, 
														 itemKwargs={'type':attrType})

				# add row
				item.appendRow(row)

				# loop downstream
				self._add_child(row[0], val, template=template_child)

	def _update_parent(self, item):
		# get item parent
		parent = item.parent()
		if parent:
			# get index
			index_parent = parent.index()
			# get value index
			index_value = self._model.index(parent.row(), 1, parent=index_parent.parent())
			# get value
			value = convert_data(self._model.data(index_value))
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
			self._update_parent(self._model.itemFromIndex(index_parent))

	def _rebuild_child(self, item):
		index_value = item.index()
		index_attr = self._model.index(item.row(), 0, parent=index_value.parent())
		# get value
		value = convert_data(self._model.data(index_value))
		
		if isinstance(value, list) or isinstance(value, dict):
			item_attr = self._model.itemFromIndex(index_attr)
			# clear out the childs
			rows = item_attr.rowCount()
			item_attr.removeRows(0, rows)
			# get template
			template = item_attr.data(role=ROLE_TEMPLATE)
			# rebuild
			self._add_child(item_attr, value, template=template)

	def _add_row_item(self, key, val=None, itemKwargs={}):
		# column 1: property name
		column_property = QStandardItem(key)
		column_property.setEditable(False)
		column_property.setData(self._size, role=Qt.SizeHintRole)

		# column 2: value
		column_val = PropertyItem(*val, **itemKwargs)
		column_val.setData(self._size, role=Qt.SizeHintRole)

		# get template
		template = column_val.data(role=ROLE_TEMPLATE)

		return [column_property, column_val], template


class PropertyDelegate(QItemDelegate):
	"""
	base class for PropertyDelegate
	PropertyDelegate will create the correct widget base on property type
	"""
	QSignelUpdateParent = Signal(QStandardItem)
	QSignelRebuildChild = Signal(QStandardItem)

	def __init__(self, parent=None):
		super(PropertyDelegate, self).__init__(parent)
		
	def createEditor(self, parent, option, index):
		item = index.model().itemFromIndex(index)
		attrType = item.data(role=ROLE_TEMPLATE)

		value = index.data()

		widget = PROPERTY_ITEMS[attrType]['widget'](parent)

		# extra setting
		if isinstance(widget, QComboBox):
			# set enum
			enum = item.data(role=ROLE_ENUM)
			widget.addItems(enum)
			enumIndex = widget.findText(value, Qt.MatchFixedString)
			widget.setCurrentIndex(enumIndex)

		elif isinstance(widget, QDoubleSpinBox) or isinstance(widget, QSpinBox):
			# set range
			minVal = item.data(role=ROLE_MIN)
			maxVal = item.data(role=ROLE_MAX)
			if minVal:
				widget.setMinimum(minVal)
			if maxVal:
				widget.setMaximum(maxVal)

		elif isinstance(widget, QLineEdit):
			widget.setFrame(False)

		return widget

	def setEditorData(self, editor, index):
		super(PropertyDelegate, self).setEditorData(editor, index)

	def setModelData(self, editor, model, index):
		item = model().itemFromIndex(index)
		# get previous value
		value = item.text()		

		# set data
		super(PropertyDelegate, self).setModelData(editor, model, index)
		
		# if it's string/list/dict
		if isinstance(editor, QLineEdit):
			# get default value
			value_default = item.data(role=ROLE_VALUE)
			# get changed value
			value_change = item.text()
			# convert value
			value_change = convert_data(value_change)

			# if string and changed value is not 
			if isinstance(value_default, basestring) and not isinstance(value_change, basestring):
				# change back to previous
				item.setText(value)
			# if list
			elif isinstance(value_default, list):
				if isinstance(value_change, list):
					# shoot signal
					self.QSignelRebuildChild.emit(item)
					
				else:
					# change back to previous
					item.setText(value)
			# if dict
			elif isinstance(value_default, dict):
				if isinstance(value_change, dict):
					# shoot signal
					self.QSignelRebuildChild.emit(item)
				else:
					# change back to previous
					item.setText(value)

		# shoot rebuild signal
		self.QSignelUpdateParent.emit(item)


class PropertyItem(QStandardItem):
	"""
	base class for PropertyItem
	PropertyItem register all the data info into QStandardItem
	so it can be query or recreate later
	espically for list and dictionary, 
	it hold the template to add items 
	"""
	def __init__(self, *args, **kwargs):
		super(PropertyItem, self).__init__()

		self._value = kwargs.get('value', None)
		self._type = kwargs.get('type', None)
		self._enum = kwargs.get('enum', [])
		self._min = kwargs.get('min', None)
		self._max = kwargs.get('max', None)
		self._template = kwargs.get('template', None)
		self._hint = kwargs.get('hint', '')

		if args:
			self._value = args[0]
		
		self._set_data()

	def _set_data(self):
		data_info = {'value': None,
					 'min': None,
					 'max': None,
					 'enum': None,
					 'template': None,
					 'type': None,
					 'hint': ''}
		
		if not self._type:
			if self._value in [True, False]:
				self._type = 'bool'
				self._enum = ['True', 'False']
			elif isinstance(self._value, float):
				self._type = 'float'
			elif isinstance(self._value, int):
				self._type = 'int'
			elif isinstance(self._value, list):
				self._type = 'list'
			elif isinstance(self._value, dict):
				self._type = 'dict'
			elif isinstance(self._value, basestring):
				self._type = 'str'
			else:
				return

		data_info.update(PROPERTY_ITEMS[self._type])

		data_info['type'] = self._type

		self._value = str(self._value)

		for attr in ['value', 'min', 'max', 'enum', 'template', 'hint']:
			if hasattr(self, '_'+attr):
				data_info[attr] = getattr(self, '_'+attr)

		self.setText(str(data_info['value']))

		self.setData(data_info['value'], role=ROLE_VALUE)
		self.setData(data_info['type'], ROLE_TYPE)
		self.setData(data_info['min'], ROLE_MIN)
		self.setData(data_info['max'], ROLE_MAX)
		self.setData(data_info['enumName'], ROLE_ENUM)
		self.setData(data_info['template'], ROLE_TEMPLATE)
		if data_info['hint']:
			self.setData(data_info['hint'], Qt.ToolTipRole)

# =================#
#      FUNCTION    #
# =================#
def convert_data(value):
	try:
		value = ast.literal_eval(value)
	except:
		pass
	return value