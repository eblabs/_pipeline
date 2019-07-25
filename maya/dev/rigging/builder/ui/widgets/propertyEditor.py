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

import dev.rigging.task
PROPERTY_ITEMS = dev.rigging.task.PROPERTY_ITEMS

ROLE_ITEM_KWARGS = Qt.UserRole + 1

ROLE_TASK_KWARGS = Qt.UserRole + 4

# =================#
#      CLASS       #
# =================#

class PropertyEditor(QTreeView):
	"""base class for PropertyEditor"""
	def __init__(self):
		super(PropertyEditor, self).__init__()
		self._property = []
		self._size = QSize(20,20)
		self._enable = True

		self.init_widget()

	def init_widget(self):
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
		delegate.QSignalUpdateParent.connect(self._update_parent)
		delegate.QSignalRebuildChild.connect(self._rebuild_child)

		self.setItemDelegate(delegate)

		self.right_click_menu()

		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self._show_menu)

	def init_property(self, item):
		'''
		initialize property
		'''
		self.refresh()

		data_property = item.data(0, ROLE_TASK_KWARGS)

		for key, data in data_property.iteritems():
			# add row item
			row, template_child = self._add_row_item(key, itemKwargs=data)

			# add row
			self._model.appendRow(row)

			# loop downstream
			self._add_child(row[0], data['value'], template=template_child)

	def refresh(self):
		self.setEnabled(True)
		self._model.clear()
		self._model = QStandardItemModel(0,2)
		self._model.setHeaderData(0, Qt.Horizontal, 'Properties')
		self._model.setHeaderData(1, Qt.Horizontal, '')
		self.setModel(self._model)
		
	def enable_widget(self):
		self._enable = not self._enable
		self.setEnabled(self._enable)

	def right_click_menu(self):
		self.menu = QMenu()
		self.action_edit = self.menu.addAction('Reset Value')
		self.menu.addSeparator()
		self.action_setSelect = self.menu.addAction('Set Selection')
		self.action_addSelect = self.menu.addAction('Add Selection')
		self.menu.addSeparator()
		self.action_addElement = self.menu.addAction('Add Element')
		self.action_delElement = self.menu.addAction('Remove Element')
		self.action_dupElement = self.menu.addAction('Duplicate Element')

		for action in [self.action_setSelect,
					   self.action_addSelect,
					   self.action_addElement,
					   self.action_delElement,
					   self.action_dupElement]:
			action.setEnabled(False)

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
				val = convert_data(self._model.data(index_val))
				if isinstance(value, list):
					value_collect.append(str(val))
				else:
					value_collect.update({attr: str(val)})
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
			itemKwargs = item_attr.data(role=ROLE_ITEM_KWARGS)
			if itemKwargs and 'template' in itemKwargs:
				template = itemKwargs['template']
			else:
				template = None
			# rebuild
			self._add_child(item_attr, value, template=template)

	def _add_row_item(self, key, val=None, itemKwargs={}):
		# column 1: property name
		column_property = QStandardItem(key)
		column_property.setEditable(False)
		column_property.setData(self._size, role=Qt.SizeHintRole)

		# update kwargs
		if 'type' in itemKwargs:
			kwargs_add = PROPERTY_ITEMS[itemKwargs['type']]
			kwargs_add.update(itemKwargs)
			itemKwargs = kwargs_add

		# column 2: value
		if val != None:
			itemKwargs.update({'value': val})

		column_val = PropertyItem(dataInfo=itemKwargs)

		if 'height' in itemKwargs:
			size = QSize(self._size.width(), itemKwargs['height'])
		
			column_property.setData(size, role=Qt.SizeHintRole)

		# get template
		if 'template' in itemKwargs:
			template = itemKwargs['template']
		else:
			template = None

		return [column_property, column_val], template

	def _show_menu(self, QPos):
		index = self.currentIndex()
		item = self._model.itemFromIndex(index)
		column = item.column()
		if column > 0:
			pos = self.viewport().mapToGlobal(QPos)        
			self.menu.move(pos)

			dataInfo = item.data(role=ROLE_ITEM_KWARGS)
			print dataInfo
			if 'select' in dataInfo and dataInfo['select']:
				self.action_setSelect.setEnabled(True)
				if 'template' in dataInfo and dataInfo['template'] != None:
					self.action_addSelect.setEnabled(True)
				else:
					self.action_addSelect.setEnabled(False)
			else:
				self.action_setSelect.setEnabled(False)
			
			if 'template' in dataInfo and dataInfo['template'] != None:
				self.action_addElement.setEnabled(True)
				self.action_delElement.setEnabled(True)
				self.action_dupElement.setEnabled(True)
			else:
				self.action_addElement.setEnabled(False)
				self.action_delElement.setEnabled(False)
				self.action_dupElement.setEnabled(False)

			self.menu.show()

class PropertyDelegate(QItemDelegate):
	"""
	base class for PropertyDelegate
	PropertyDelegate will create the correct widget base on property type
	"""
	QSignalUpdateParent = Signal(QStandardItem)
	QSignalRebuildChild = Signal(QStandardItem)

	def __init__(self, parent=None):
		super(PropertyDelegate, self).__init__(parent)
		
	def createEditor(self, parent, option, index):
		item = index.model().itemFromIndex(index)

		dataInfo = item.data(role=ROLE_ITEM_KWARGS)

		value = index.data()

		widget = dataInfo['widget'](parent)

		# extra setting
		if isinstance(widget, QComboBox):
			# set enum
			widget.addItems(dataInfo['enum'])
			enumIndex = widget.findText(value, Qt.MatchFixedString)
			widget.setCurrentIndex(enumIndex)

		elif isinstance(widget, QDoubleSpinBox) or isinstance(widget, QSpinBox):
			# set range
			if 'min' in dataInfo and dataInfo['min'] != None:
				widget.setMinimum(dataInfo['min'])
			if 'max' in dataInfo and dataInfo['max'] != None:
				widget.setMaximum(dataInfo['max'])

		elif isinstance(widget, QLineEdit):
			widget.setFrame(False)

		return widget

	def setEditorData(self, editor, index):
		super(PropertyDelegate, self).setEditorData(editor, index)

	def setModelData(self, editor, model, index):
		item = index.model().itemFromIndex(index)
		# get previous value
		value = item.text()

		# get data info
		dataInfo = item.data(role=ROLE_ITEM_KWARGS)	

		# set data
		super(PropertyDelegate, self).setModelData(editor, model, index)
		
		# if it's string/list/dict
		if isinstance(editor, QLineEdit):
			# get default value
			value_default = dataInfo['value']
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
					self.QSignalRebuildChild.emit(item)

				else:
					# change back to previous
					item.setText(value)

			# if dict
			elif isinstance(value_default, dict):
				if isinstance(value_change, dict):
					# shoot signal
					self.QSignalRebuildChild.emit(item)
				else:
					# change back to previous
					item.setText(value)

		# shoot rebuild signal
		self.QSignalUpdateParent.emit(item)


class PropertyItem(QStandardItem):
	"""
	base class for PropertyItem
	PropertyItem register all the data info into QStandardItem
	so it can be query or recreate later
	espically for list and dictionary, 
	it hold the template to add items 
	"""
	def __init__(self, dataInfo={}):
		super(PropertyItem, self).__init__()

		self._data_info = dataInfo

		self._set_data()

	def _set_data(self):
		self.setText(str(self._data_info['value']))

		self.setData(self._data_info, role=ROLE_ITEM_KWARGS)

		if 'hint' in self._data_info and self._data_info['hint']:
			self.setData(self._data_info['hint'], Qt.ToolTipRole)

# =================#
#      FUNCTION    #
# =================#
def convert_data(value):
	try:
		value = ast.literal_eval(value)
	except:
		pass
	return value