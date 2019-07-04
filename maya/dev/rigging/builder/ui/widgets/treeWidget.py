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

# import OrderedDict
from collections import OrderedDict 
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

SC_REFRESH = 'Ctrl+R'
SC_RUN_ALL = 'Ctrl+Shift+Space'
SC_RUN_PAUSE = 'Ctrl+Space'
SC_REFRESH_RUN = 'Ctrl+Shift+R'

#=================#
#      CLASS      #
#=================#
class TreeWidget(QTreeWidget):
	"""base class for TreeWidget"""
	QSignalProgressInit = Signal(int)
	QSignalDoubleClick = Signal()
	QSignalClear = Signal()
	def __init__(self, *args, **kwargs):
		super(TreeWidget, self).__init__()

		self._itemRunner = ItemRunner(self)
		self._stop = False
		self._pause = False
		
		# get kwargs
		self._header = kwargs.get('header', ['Task', 'Status'])
		self._Builder = kwargs.get('builder', None) # builder object

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

		self._root = self.invisibleRootItem()

		# right clicked menu
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.right_clicked_menu)
		
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
			QTreeWidgetItem_child.setData(0, ROLE_TASK_FUNC_NAME, dataInfo['taskName'])
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
		if event.key() == Qt.Key_Escape and event.modifiers() == Qt.NoModifier:
			self._clear_selection()
		else:
			QTreeWidget.keyPressEvent(self, event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self._clear_selection()
			
		super(TreeWidget, self).mousePressEvent(event)

	def mouseDoubleClickEvent(self, event):
		# double click to run the task
		if self.indexAt(event.pos()).isValid():
			self.QSignalDoubleClick.emit()

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

		# shoot signal to progress bar
		self.QSignalProgressInit.emit(len(items))

		# start run tasks
		self._itemRunner.start()

	def right_clicked_menu(self, QPos):
		menu= QMenu(self)
		self._action_execute = menu.addAction('Execute\t'+SC_RUN_PAUSE)
		self._action_execute_single = menu.addAction('Execute Single')
		self._action_execute_all = menu.addAction('Execute All\t'+SC_RUN_ALL)		
		self._action_refresh = menu.addAction('Reload\t'+SC_REFRESH)
		self._action_rebuild = menu.addAction('Rebuild\t'+SC_REFRESH_RUN)

		menu.addSeparator()

		self._action_create = menu.addAction('Create')
		self._action_create.setShortcut('Ctrl+n')
		self._action_duplicate = menu.addAction('Duplicate')
		self._action_duplicate.setShortcut('Ctrl+d')
		self._action_remove = menu.addAction('Remove')
		self._action_remove.setShortcut('delete')

		menu.addSeparator()

		self._action_display = menu.addAction('Display Name')
		self._action_color = menu.addAction('Color')
		self._action_color_text = menu.addAction('Text Color')
		self._action_color_reset = menu.addAction('Reset Color')

		# set enable/disable
		currentItem = self.currentIndex().data()
		actions = [self._action_execute,
				   self._action_execute_single,
				   self._action_execute_all,	
				   self._action_duplicate,
				   self._action_remove,
				   self._action_display,
				   self._action_color,
				   self._action_color_text,
				   self._action_color_reset]
		if not currentItem:
			for act in actions:
				act.setEnabled(False)
		else:
			for act in actions:
				act.setEnabled(True)

		# connect functions
		self._action_display.triggered.connect(self.set_display_name)
		self._action_color.triggered.connect(self.set_display_color)
		self._action_color_text.triggered.connect(self.set_text_color)
		self._action_color_reset.triggered.connect(self.reset_display_color)

		pos_parent = self.mapToGlobal(QPoint(0, 0))        
		menu.move(pos_parent + QPos)

		menu.show()

	def set_display_name(self):
		item = self.currentItem()
		current_name = item.text(0)
		text, ok = QInputDialog.getText(self, 'Display Name','Set Display Name', text=current_name)
		if text and ok:
			item.setText(0, text)

	def set_display_color(self):
		item = self.currentItem()
		background_col = item.background(0).color()
		col = QColorDialog.getColor(background_col, self, 'Display Color')
		if col.isValid():
			item.setBackground(0, col)

	def set_text_color(self):
		item = self.currentItem()
		foreground_col = item.foreground(0).color()
		col = QColorDialog.getColor(foreground_col, self, 'Text Color')
		if col.isValid():
			item.setForeground(0, col)

	def reset_display_color(self):
		item = self.currentItem()
		item.setData(0, Qt.BackgroundRole, None)
		item.setData(0, Qt.ForegroundRole, None)

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

	def _refresh_tasks(self):
		if self._Builder:
			self._remove_all_tasks()
			self.add_tree_items()
		# refresh progress bar, shoot signal
		# the range doesn't matter, will re-init when run the task
		self.QSignalProgressInit.emit(1)

	def _run_tasks(self):
		self.run_task(item=self.currentItem())

	def _pause_tasks(self):
		self._pause = not self._pause

	def _stop_tasks(self):
		self._stop = True

	def _run_all_tasks(self):
		self.run_task()

	def _remove_all_tasks(self):
		itemCount = self.topLevelItemCount()
		for i in range(itemCount):
			self.takeTopLevelItem(0)

	def _clear_selection(self):
		self.clearSelection()
		self.clearFocus()
		self.setCurrentIndex(QModelIndex())

		# shoot clear signal
		self.QSignalClear.emit()

		

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
	QSignalProgress = Signal(int) # emit signal to update progress bar
	QSignalError = Signal() # emit signal for error
	QSignalPause = Signal() # emiet signal to pause
	def __init__(self, parent, items=[], ignoreCheck=False):
		super(ItemRunner, self).__init__(parent)
		self._parent = parent
		self._items = items
		self._ignoreCheck = ignoreCheck

	def run(self):
		self.run_task()
		
	def run_task(self):
		# disable treeWidget when running
		self._parent.setEnabled(False)
		
		itemCount = float(len(self._items))
		for i, item in enumerate(self._items):
			if self._parent._pause:
				self.QSignalPause.emit()
			while self._parent._pause:
				# in case need to be stopped from pause
				if self._parent._stop: 
					self.QSignalError.emit()
					self._parent._pause = False				
				self.sleep(1) # pause the process

			# check if need to be stopped
			if self._parent._stop:
				self.QSignalError.emit()
				Logger.warn('Task process is stopped by the user')
				self._parent.setEnabled(True) # enable back widget if error
				break
			
			self._run_task_on_single_item(item, ignoreCheck=self._ignoreCheck)

			# emit signal
			self.QSignalProgress.emit(i+1)

		self._parent.setEnabled(True) # enable back widget when finished
				
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
					# emit error signal
					self.QSignalError.emit()
					self._parent.setEnabled(True) # enable back widget if error
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
				# emit error signal
				self.QSignalError.emit()
				self._parent.setEnabled(True) # enable back widget if error
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
					# emit error signal
					self.QSignalError.emit()
					self._parent.setEnabled(True) # enable back widget if error
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
				# emit error signal
				self.QSignalError.emit()
				self._parent.setEnabled(True) # enable back widget if error
				raise RuntimeError()
		