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

ROLE_TASK_NAME = Qt.UserRole + 1
ROLE_TASK_FUNC = Qt.UserRole + 2
ROLE_TASK_KWARGS = Qt.UserRole + 3

#=================#
#      CLASS      #
#=================#
class TreeWidget(QTreeWidget):
	"""base class for TreeWidget"""
	def __init__(self, *args, **kwargs):
		super(TreeWidget, self).__init__(*args, **kwargs)
		
		# get kwargs
		self._header = kwargs.get('header', ['Task', 'Status'])

		self.init_widget()

	def init_widget(self):
		QHeader = QTreeWidgetItem(self._header)
		self.setHeaderItem(QHeader)
		self.setRootIsDecorated(True)
		self.setAlternatingRowColors(True)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setHeaderHidden(True)
		self.header().setSectionResizeMode(0, QHeaderView.Stretch)
		self.header().setStretchLastSection(False)
		self.setColumnWidth(1,40)

		self.setSelectionMode(self.ExtendedSelection)
		self.setDragDropMode(self.InternalMove)
		self.setDragEnabled(True)
		self.setDropIndicatorShown(True)
		
	def add_tree_items(self, data):
		self._add_child_item(self.invisibleRootItem(), data)

		self.expandAll()

	def _add_child_item(self, QItem, data):
		for d in data:
			name = d.keys()[0]
			dataInfo = d[name]
			print name
			print dataInfo

			QTreeWidgetItem_child = QTreeWidgetItem()
			QTreeWidgetItem_child.setText(0, dataInfo['display'])
			QTreeWidgetItem_child.setData(0, ROLE_TASK_NAME, name)
			QTreeWidgetItem_child.setData(0, ROLE_TASK_FUNC, dataInfo['Task'])
			QTreeWidgetItem_child.setData(0, ROLE_TASK_KWARGS, dataInfo['kwargs'])
			QTreeWidgetItem_child.setFlags(QTreeWidgetItem_child.flags()|Qt.ItemIsTristate|Qt.ItemIsUserCheckable)
			QTreeWidgetItem_child.setCheckState(0, Qt.Checked)

			QItem.addChild(QTreeWidgetItem_child)

			if 'children' in dataInfo:
				self._add_child_item(QTreeWidgetItem_child, dataInfo['children'])

	def dropEvent(self, event):
		if event.source() == self:
			QAbstractItemView.dropEvent(self, event)

	def dropMimeData(self, parent, row, data, action):
		if action == Qt.MoveAction:
			return self.moveSelection(parent, row)
		return False

	def moveSelection(self, parent, position):
		selection = [QPersistentModelIndex(i)
					 for i in self.selectedIndexes()]
		parent_index = self.indexFromItem(parent)
		if parent_index in selection:
			return False
		# save the drop location in case it gets moved
		target = self.model().index(position, 0, parent_index).row()
		if target < 0:
			target = position
		# remove the selected items
		taken = []
		for index in reversed(selection):
			item = self.itemFromIndex(QModelIndex(index))
			if item is None or item.parent() is None:
				taken.append(self.takeTopLevelItem(index.row()))
			else:
				taken.append(item.parent().takeChild(index.row()))
		# insert the selected items at their new positions
		while taken:
			if position == -1:
				# append the items if position not specified
				if parent_index.isValid():
					parent.insertChild(
						parent.childCount(), taken.pop(0))
				else:
					self.insertTopLevelItem(
						self.topLevelItemCount(), taken.pop(0))
			else:
				# insert the items at the specified position
				if parent_index.isValid():
					parent.insertChild(min(target,
						parent.childCount()), taken.pop(0))
				else:
					self.insertTopLevelItem(min(target,
						self.topLevelItemCount()), taken.pop(0))
		return True

	def keyPressEvent(self, event):
		if (event.key() == Qt.Key_Escape and
			event.modifiers() == Qt.NoModifier):
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QModelIndex())
		else:
			QTreeWidget.keyPressEvent(self, event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QModelIndex())
		super(TreeWidget, self).mousePressEvent(event)

	def mouseDoubleClickEvent(self, event):
		if self.indexAt(event.pos()).isValid():
			TaskItem = self.currentItem()
			display = TaskItem.text(0)
			name = TaskItem.data(0, ROLE_TASK_NAME)
			Task = TaskItem.data(0, ROLE_TASK_FUNC)
			kwargs = TaskItem.data(0, ROLE_TASK_KWARGS)
			print 'display: ' + display
			print 'name: ' + name
			print 'kwargs:'
			print kwargs
			Task()
