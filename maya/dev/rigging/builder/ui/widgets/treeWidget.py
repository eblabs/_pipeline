#=================#
# IMPORT PACKAGES #
#=================#

# import system packages
import sys
import os

# import inspect
import inspect

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

# import icon
import icons

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

ROLE_TASK_NAME = Qt.UserRole + 1
ROLE_TASK_FUNC_NAME = Qt.UserRole + 2
ROLE_TASK_FUNC = Qt.UserRole + 3
ROLE_TASK_KWARGS = Qt.UserRole + 4
ROLE_TASK_RETURN = Qt.UserRole + 5

ICONS_STATUS = [icons.grey, icons.green, icons.yellow, icons.red]

#=================#
#      CLASS      #
#=================#
class TreeWidget(QTreeWidget):
	"""base class for TreeWidget"""
	def __init__(self, *args, **kwargs):
		super(TreeWidget, self).__init__()

		self._itemRunner = ItemRunner(self)
		self._stop = False
		self._pause = False
		
		# get kwargs
		self._header = kwargs.get('header', ['Task', 'Status'])
		self._Builder = kwargs.get('builder', None) # builder object

		self.init_widget()
		self.add_tree_items()

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

		self._root = self.invisibleRootItem()
		
	def add_tree_items(self):
		self._add_child_item(self._root, 
							 self._Builder.tree_hierarchy())

		self.expandAll()

	def _add_child_item(self, QItem, data):
		for d in data:
			name = d.keys()[0]
			dataInfo = d[name]

			#QTreeWidgetItem_child = QTreeWidgetItem()
			QTreeWidgetItem_child = TaskItem()
			QTreeWidgetItem_child.setText(0, dataInfo['display'])
			QTreeWidgetItem_child.setData(0, ROLE_TASK_NAME, name)
			QTreeWidgetItem_child.setData(0, ROLE_TASK_FUNC, dataInfo['taskName'])
			QTreeWidgetItem_child.setData(0, ROLE_TASK_FUNC, dataInfo['Task'])
			QTreeWidgetItem_child.setData(0, ROLE_TASK_KWARGS, dataInfo['kwargs'])
			QTreeWidgetItem_child.setData(0, ROLE_TASK_RETURN, 0)
			QTreeWidgetItem_child.setFlags(QTreeWidgetItem_child.flags()|Qt.ItemIsTristate|Qt.ItemIsUserCheckable)
			QTreeWidgetItem_child.setCheckState(0, Qt.Checked)
			#QTreeWidgetItem_child.setIcon(1, QIcon(icons.grey))

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
		if event.key() == Qt.Key_Escape:
			self._stop = True # stop task run

			if event.modifiers() == Qt.NoModifier:
				self.clearSelection()
				self.clearFocus()
				self.setCurrentIndex(QModelIndex())

		elif event.key() == Qt.Key_Space:
			# pause and resume task run
			self._pause = not self._pause
		else:
			QTreeWidget.keyPressEvent(self, event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QModelIndex())
		super(TreeWidget, self).mousePressEvent(event)

	def mouseDoubleClickEvent(self, event):
		# double click to run the task
		if self.indexAt(event.pos()).isValid():
			self.run_task(item=self.currentItem())

	def run_task(self, item=None, collect=True):
		'''
		run task

		item(QItem): None will be the root
		collect(bool)[True]: loop downstream tasks
		'''
		# reset value
		self._stop = False
		self._pause = False
		# collect items
		if collect:
			items = self._collect_items(item=item)
			ignoreCheck = False
		else:
			items = [item]
			ignoreCheck = True
		# register in itemRunner
		self._itemRunner._items = items
		self._itemRunner._ignoreCheck = ignoreCheck
		# start run tasks
		self._itemRunner.start()
	
	def _collect_items(self, item=None):
		'''
		collect items parented to the item in order [item included]

		collect items from root if item is None
		'''

		if item:
			items = [item]
		else:
			items = []
			item = self._root
		# get child count
		childCount = item.childCount()
		# loop downstream
		for i in range(childCount):
			items += self._collect_items(item=item.child(i))

		return items

class TaskItem(QTreeWidgetItem):
	def setData(self, column, role, value):
		super(TaskItem, self).setData(column, role, value)
		if role == Qt.CheckStateRole:
			state = self.checkState(column)
			if state == Qt.Checked:
				taskReturn = self.data(0, ROLE_TASK_RETURN)
				self.setIcon(1, QIcon(ICONS_STATUS[taskReturn]))
			else:
				self.setIcon(1, QIcon(icons.unCheck))
		elif role == ROLE_TASK_RETURN:
			self.setIcon(1, QIcon(ICONS_STATUS[value]))



class ItemRunner(QThread):
	"""
	QThread to run items one by one
	
	use multi-threading so the ui won't be frozen,
	and can be stopped anytime
	"""
	QSignelProgress = Signal(float) # emit signal to update progress bar

	def __init__(self, parent, items=[], ignoreCheck=False):
		super(ItemRunner, self).__init__(parent)
		self._parent = parent
		self._items = items
		self._ignoreCheck = ignoreCheck

	def run(self):
		self.run_task()
		
	def run_task(self):
		itemCount = float(len(self._items))
		for i, item in enumerate(self._items):
			while self._parent._pause:
				# in case need to be stopped from pause
				if self._parent._stop: 
					break
				self.sleep(1) # pause the process

			# check if need to be stopped
			if self._parent._stop:
				Logger.warn('Task process is stopped by the user')
				break
			
			self._run_task_on_single_item(item, ignoreCheck=self._ignoreCheck)

			# get progress percentage
			progress = (i+1)/itemCount
			# emit signal
			self.QSignelProgress.emit(progress)

	def _run_task_on_single_item(self, item, ignoreCheck=False):
		# get attributes from item
		display = item.text(0)
		name = item.data(0, ROLE_TASK_NAME)
		Task = item.data(0, ROLE_TASK_FUNC)
		kwargs = item.data(0, ROLE_TASK_KWARGS)
		taskReturn = item.data(0, ROLE_TASK_RETURN) # skip if already run
		checkState = item.checkState(0)

		if not ignoreCheck and checkState != Qt.Checked:
			# skip unchecked task
			return 

		if taskReturn > 0:
			# skip task already runned
			return

		# check if registered function is a method
		if inspect.ismethod(Task):
			# try to run function 
			try:
				taskReturn = Task(**kwargs)
				if taskReturn == 3:
					# error raises
					item.setData(0, ROLE_TASK_RETURN, 3)
					raise RuntimeError()
				elif taskReturn == 2:
					# warning raises
					item.setData(0, ROLE_TASK_RETURN, 2)
				else:
					# run succesfully
					item.setData(0, ROLE_TASK_RETURN, 1)

				# log
				Logger.info('Run method "{}" succesfully'.format(display))
			
			except:
				# error raises
				item.setData(0, ROLE_TASK_RETURN, 3)
				raise RuntimeError()

		else:
			# Task is an imported task
			# try to run task
			try:
				# get obj
				TaskObj = Task(**kwargs)
				# run task
				taskReturn = TaskObj.run()

				if taskReturn == 3:
					# error raises
					item.setData(0, ROLE_TASK_RETURN, 3)
					raise RuntimeError()
				elif taskReturn == 2:
					# warning raises
					item.setData(0, ROLE_TASK_RETURN, 2)
				else:
					# run succesfully
					item.setData(0, ROLE_TASK_RETURN, 1)

				# attach to builder
				setattr(self._parent._Builder, name, TaskObj)
				
				# log
				Logger.info('Run task "{}" succesfully'.format(display))
			
			except:
				# error raises
				item.setData(0, ROLE_TASK_RETURN, 3)
				raise RuntimeError()
		