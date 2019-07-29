#=================#
# IMPORT PACKAGES #
#=================#

# import system packages
import sys
import os

# import copy_reg, types to fix one pickle problem
import copy_reg
import types

# import ast
import ast

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

## import utils
import utils.common.logUtils as logUtils
import utils.common.modules as modules
# import widget
import taskCreator
#=================#
#   GLOBAL VARS   #
#=================#
logger = logUtils.get_logger()

ROLE_TASK_NAME = Qt.UserRole + 1
ROLE_TASK_FUNC_NAME = Qt.UserRole + 2
ROLE_TASK_FUNC = Qt.UserRole + 3
ROLE_TASK_KWARGS = Qt.UserRole + 4
ROLE_TASK_KWARGS_KEY = Qt.UserRole + 5
ROLE_TASK_PRE = Qt.UserRole + 6
ROLE_TASK_RUN = Qt.UserRole + 7
ROLE_TASK_POST = Qt.UserRole + 8
ROLE_TASK_SECTION = Qt.UserRole + 9
ROLE_TASK_TYPE = Qt.UserRole + 10

ICONS_STATUS = [icons.grey, icons.green, icons.yellow, icons.red]
ICONS_TASK = {'task': icons.task,
			  'function': icons.function,
			  'method': icons.method}

SC_RELOAD = 'Ctrl+R'
SC_RUN_ALL = 'Ctrl+Shift+Space'
SC_RUN_PAUSE = 'Ctrl+Space'
SC_RELOAD_RUN = 'Ctrl+Shift+R'
SC_REMOVE = 'delete'
SC_DUPLICATE = 'Ctrl+D'
SC_EXPAND_COLLAPSE = 'CTRL+K'

#=================#
#      CLASS      #
#=================#
class TreeWidget(QTreeWidget):
	"""base class for TreeWidget"""
	QSignalProgressInit = Signal(int)
	QSignalClear = Signal()
	QSignalExecute = Signal()
	QSignalAttrName = Signal(QTreeWidgetItem)
	def __init__(self, *args, **kwargs):
		super(TreeWidget, self).__init__()

		self.itemRunner = ItemRunner(self)
		self._stop = False
		self._pause = False
		self._expand = True
		self._displayItems = [] # list of item display name to make sure no same name
		self._attrItems = [] # list of item attr name to make sure no same name
		self._change = False # use to check if mouse is on checkbox or actual task
		# get kwargs
		self._header = kwargs.get('header', ['Task', 'Pre', 'Build', 'Post'])
		self.builder = kwargs.get('builder', None) # builder object

		# task folders
		self.taskFolders = ['dev.rigging.task.core',
							'dev.rigging.task.base',
							'dev.rigging.task.test']

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
		self.setColumnWidth(1,20)
		self.setColumnWidth(2,20)
		self.setColumnWidth(3,20)

		self.setSelectionMode(self.ExtendedSelection)
		self.setDragDropMode(self.InternalMove)
		self.setDragEnabled(True)
		self.setDropIndicatorShown(True)

		self._root = self.invisibleRootItem()

		# right clicked menu
		self.right_clicked_menu()
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.show_menu)

		# short cut
		QShortcut(QKeySequence(SC_DUPLICATE), self, self.duplicate_tasks) 
		QShortcut(QKeySequence(SC_REMOVE), self, self.remove_tasks)

		QShortcut(QKeySequence(SC_EXPAND_COLLAPSE), self, self.expand_collapse)  

		self.itemChanged.connect(self._item_data_changed)
		self.itemPressed.connect(self._item_data_changed_reset)

	def add_tree_items(self):
		self._add_child_item(self._root, 
							 self.builder.tree_hierarchy())

		self.expandAll()

	def _add_child_item(self, QItem, data):
		for d in data:
			name = d.keys()[0]
			dataInfo = d[name]
			dataInfo.update({'attrName': name})
			item = TaskItem(**dataInfo)

			display = item.text(0) # get display name
			attrName = item.data(0, ROLE_TASK_NAME) # get attr name

			self._displayItems.append(display) # add to list for later check
			self._attrItems.append(attrName) # add to list for later check

			QItem.addChild(item)

			if 'children' in dataInfo:
				self._add_child_item(item, dataInfo['children'])

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
			if not self._change:
				self.run_sel_tasks()

	def right_clicked_menu(self):
		'''
		right click menu for functions
		'''
		self.menu= QMenu(self)

		# execute
		self.menu_execute_sel = SubMenu('Execute Selection', 
										parent=self.menu, 
										shortcut=SC_RUN_PAUSE)

		self.menu_execute_all = SubMenu('Execute All', 
										parent=self.menu, 
										shortcut=SC_RUN_ALL)

		self.menu_rebuild = SubMenu('Rebuild', 
									parent=self.menu, 
									shortcut=SC_RELOAD_RUN)

		self.menu.addMenu(self.menu_execute_sel)
		self.menu.addMenu(self.menu_execute_all)
		self.menu.addMenu(self.menu_rebuild)

		self.action_reload = self.menu.addAction('Reload')
		self.action_reload.setShortcut(SC_RELOAD)

		self.menu.addSeparator()

		self.action_create = self.menu.addAction('Create')
		self.action_create.setShortcut('Ctrl+n')
		self.action_duplicate = self.menu.addAction('Duplicate')
		self.action_duplicate.setShortcut(SC_DUPLICATE)
		self.action_remove = self.menu.addAction('Remove')
		self.action_remove.setShortcut(SC_REMOVE)

		self.menu.addSeparator()

		self.action_display = self.menu.addAction('Display Name')
		self.action_color = self.menu.addAction('Display Color')
		self.action_color_text = self.menu.addAction('Text Color')
		self.action_color_reset = self.menu.addAction('Reset Color')

		self.menu.addSeparator()

		self.action_expand = self.menu.addAction('Expand/Collapse')
		self.action_expand.setShortcut(SC_EXPAND_COLLAPSE)

		# set enable/disable
		self._menu_widgets = [self.menu_execute_sel,
							  self.menu_execute_all,
							  self.action_duplicate,
							  self.action_remove,
							  self.action_display,
							  self.action_color,
							  self.action_color_text,
							  self.action_color_reset]

		for widget in self._menu_widgets:
			widget.setEnabled(False)

		# connect functions
		self.action_reload.triggered.connect(self.reload_tasks)
		self.menu_execute_sel.QSignalSection.connect(self.run_sel_tasks)
		self.menu_execute_all.QSignalSection.connect(self.run_all_tasks)
		self.menu_rebuild.QSignalSection.connect(self.rebuild_tasks)

		self.action_duplicate.triggered.connect(self.duplicate_tasks)
		self.action_remove.triggered.connect(self.remove_tasks)

		self.action_display.triggered.connect(self.set_display_name)
		self.action_color.triggered.connect(self.set_display_color)
		self.action_color_text.triggered.connect(self.set_text_color)
		self.action_color_reset.triggered.connect(self.reset_display_color)		

		self.action_expand.triggered.connect(self.expand_collapse)

		# task creation window
		self.task_create_window = TaskCreate()
		self.action_create.triggered.connect(self._task_create_window_open)
		self.task_create_window.QSignalTaskCreation.connect(self._create_task)

	def show_menu(self, QPos):
		currentItem = self.currentIndex().data()
		if not currentItem:
			for widget in self._menu_widgets:
				widget.setEnabled(False)
		else:
			for widget in self._menu_widgets:
				widget.setEnabled(True)
			# disable duplicate and remove for in class method
			taskType = self.currentItem().data(0, ROLE_TASK_TYPE)
			if taskType == 'method':
				self.action_duplicate.setEnabled(False)
				self.action_remove.setEnabled(False)

		pos_parent = self.mapToGlobal(QPoint(0, 0))        
		self.menu.move(pos_parent + QPos)

		self.menu.show()

	# task functions to connect with button and menu
	def run_sel_tasks(self, section=['pre_build', 'build', 'post_build']):
		items = self.selectedItems()
		self._run_task(items=items, section=section)
		self.QSignalExecute.emit()

	def run_all_tasks(self, section=['pre_build', 'build', 'post_build']):
		self._run_task(section=section)
		self.QSignalExecute.emit()

	def rebuild_tasks(self, section=['pre_build', 'build', 'post_build']):
		self.reload_tasks()
		self._run_task(section=section)
		self.QSignalExecute.emit()

	def reload_tasks(self):
		self._displayItems = []
		self._attrItems = []

		self._expand = True

		if self.builder:
			self._remove_all_tasks()
			self.add_tree_items()
		# refresh progress bar, shoot signal
		# the range doesn't matter, will re-init when run the task
		self.QSignalProgressInit.emit(1)

	def pause_resume_tasks(self):
		self._pause = not self._pause

	def stop_tasks(self):
		self._stop = True

	def set_display_name(self):
		item = self.currentItem()
		current_name = item.text(0)
		text, ok = QInputDialog.getText(self, 'Display Name','Set Display Name', text=current_name)
		if text and ok and text != current_name:
			update_name = self._get_unique_name(current_name, text, self._displayItems)
			item.setText(0, update_name)

	def set_display_color(self):
		items = self.selectedItems()
		background_col = items[-1].background(0).color()
		col = QColorDialog.getColor(background_col, self, 'Display Color')
		if col.isValid():
			for item in items:
				items_collect = self._collect_items(item)
				for item_setCol in items_collect:
					item_setCol.setBackground(0, col)

	def set_text_color(self):
		items = self.selectedItems()
		foreground_col = items[-1].foreground(0).color()
		col = QColorDialog.getColor(foreground_col, self, 'Text Color')
		if col.isValid():
			for item in items:
				items_collect = self._collect_items(item)
				for item_setCol in items_collect:
					item_setCol.setForeground(0, col)

	def set_attr_name(self, name):
		title = "Change task's attribute name in the builder"
		# check if name already exists
		if name in self._attrItems:
			text = 'attribute name already exists'
			QMessageBox.warning(self, title, text)
			return
		else:
			# check if the string starts with letter
			check = False
			try:
				ast.literal_eval(name[0]) # not letter
				check = False
			except ValueError:
				check = True # letter
			except:
				check = False # unknow type
			if not check:
				# raise warning box
				text = 'attribute name is illegal, must start with letter'
				QMessageBox.warning(self, title, text)
				return
			else:
				# set attr name
				item = self.currentItem()
				current_name = item.data(0, ROLE_TASK_NAME)
				item.setData(0, ROLE_TASK_NAME, name)
				# remove previous name, add new name
				self._attrItems.remove(current_name)
				self._attrItems.append(name)
				# shoot signal to reset task info 
				self.QSignalAttrName.emit(item)

	def reset_display_color(self):
		items = self.selectedItems()
		for item in items:
			items_collect = self._collect_items(item)
			for item_setCol in items_collect:
				item_setCol.setData(0, Qt.BackgroundRole, None)
				item_setCol.setData(0, Qt.ForegroundRole, None)

	def duplicate_tasks(self):
		items = self.selectedItems()
		for item in items:
			# get item data
			display = item.text(0)
			attrName = item.data(0, ROLE_TASK_NAME)
			taskName = item.data(0, ROLE_TASK_FUNC_NAME)
			task = item.data(0, ROLE_TASK_FUNC)
			taskKwargs = item.data(0, ROLE_TASK_KWARGS)
			check = item.checkState(0)
			section = item.data(0, ROLE_TASK_SECTION)
			taskType = item.data(0, ROLE_TASK_TYPE)

			if taskType != 'method':

				display = self._get_unique_name('', display, self._displayItems)
				attrName = self._get_unique_name('', attrName, self._attrItems)

				kwargs = {'display': display,
						  'attrName': attrName,
						  'taskName': taskName,
						  'task': task,
						  'taskKwargs': taskKwargs,
						  'check': check,
						  'section': section,
						  'taskType': taskType}

				self._create_item(**kwargs)

	def remove_tasks(self):
		for item in self.selectedItems():
			# check type, can't delete in class method
			taskType = item.data(0, ROLE_TASK_TYPE)
			if taskType != 'method':				
				# reparent child if any is method, and get remove list
				remove_items = self._reparent_childs(item=item)
				for itm in remove_items:
					display = itm.text(0)
					attrName = itm.data(0, ROLE_TASK_NAME)
					# remove names from list
					if display in self._displayItems:
						self._displayItems.remove(display)
					if attrName in self._attrItems:
						self._attrItems.remove(attrName)
					
					index = self.indexFromItem(itm)
					if index.row() >= 0:
						# index >= 0 means still in ui, remove it
						parent = itm.parent()
						if not parent:
							parent = self._root
						parent.removeChild(itm) 

	def _reparent_childs(self, item):
		'''
		re parent childs if upper parent got removed
		'''
		item_childs = self._collect_items(item=item)
		item_hold = []
		item_remove = [item]
		for itm in item_childs[1:]:
			taskType = itm.data(0, ROLE_TASK_TYPE)
			if taskType == 'method':
				item_hold.append(itm)
			else:
				item_remove.append(itm)

		# check if item_hold parent need to be removed or not
		for itm in item_hold:
			print 'hold'
			print itm.text(0)
			itm_search = itm
			i=0
			while i<10:
				parent = itm_search.parent()
				if not parent:
					# reach top level
					index = self.indexFromItem(itm_search)
					
					# to add the item to upper level, we need take it out first
					indexOrig = self.indexFromItem(itm)
					itm.parent().takeChild(indexOrig.row())

					# add to upper level
					self.insertTopLevelItem(index.row(), itm)
					break
				elif parent not in set(item_remove):
					# either under method or other task
					index = self.indexFromItem(itm_search)

					# to add the item to upper level, we need take it out first
					indexOrig = self.indexFromItem(itm)
					itm.parent().takeChild(indexOrig.row())

					# add to upper level
					parent.insertChild(index.row(), itm)
					break
				else:
					itm_search = parent

					i+=1

		return item_remove
					


	def expand_collapse(self):
		self._expand = not self._expand
		if not self._expand:
			self.collapseAll()
		else:
			self.expandAll()

	def _run_task(self, items=None, collect=True, 
				 section=['pre_build', 'build', 'post_build']):
		'''
		run task

		item(QItem): None will be the root
		collect(bool)[True]: loop downstream tasks
		section(list): run for spcific section
					   ['pre_build', 'build', 'post_build']

		'''
		# reset value
		self._stop = False
		self._pause = False

		itemsRun = []
		ignoreCheck = False

		# collect items
		if isinstance(items, list):
			itemsRun = []
			for item in items:
				if collect and item not in set(itemsRun):
					itemsRun += self._collect_items(item)
					ignoreCheck = False
				else:
					itemsRun = items
					ignoreCheck = True
		else:
			if collect:
				itemsRun = self._collect_items(item=items)
				ignoreCheck = False
			else:
				itemsRun = [items]
				ignoreCheck = True

		# register in itemRunner
		self.itemRunner._items = itemsRun
		self.itemRunner._ignoreCheck = ignoreCheck
		self.itemRunner._section = section

		# shoot signal to progress bar
		self.QSignalProgressInit.emit(len(itemsRun)*len(section))

		# start run tasks
		self.itemRunner.start()

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

	def _create_item(self, item=None, **kwargs):
		'''
		create QTreeWidgetItem
		'''
		if not item:
			item = self._root

		item_create = TaskItem(**kwargs)

		item.addChild(item_create)

	def _create_task(self, taskInfo):
		attrName = taskInfo[0]
		display = taskInfo[1] 
		taskName = taskInfo[2]
		# imported task, get task object
		taskImport, taskFunc = modules.import_module(taskName)
		task = getattr(taskImport, taskFunc)
		if inspect.isfunction(task):
			# function, normally is callback
			taskKwargs = taskImport._kwargs_ui
			taskType = 'function'
		else:
			# task class
			taskObj = task()
			taskKwargs = taskObj._kwargs_ui
			taskType = taskObj.taskType

		attrName = self._get_unique_name('', attrName, self._attrItems)
		self._attrItems.append(attrName)

		if not display:
			display = attrName
		display = self._get_unique_name('', display, self._displayItems)
		self._displayItems.append(display)
			
		kwargs = {'display': display,
				  'attrName': attrName,
				  'taskName': taskName,
				  'task': task,
				  'taskKwargs': taskKwargs,
				  'check': Qt.Checked,
				  'taskType': taskType}

		item = self.selectedItems()
		if item:
			item = item[0]

		self._create_item(item=item, **kwargs)

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

	def _get_unique_name(self, nameOrig, nameNew, nameList):
		i = 1
		nameNew_add = nameNew
		while nameNew_add in nameList:
			nameNew_add = nameNew+str(i)
			i+=1
		nameList.append(nameNew_add)
		if nameOrig:
			nameList.remove(nameOrig)
		return nameNew_add

	def _item_data_changed(self, item):
		self._change = True

	def _item_data_changed_reset(self, item):
		self._change = False

	def _task_create_window_open(self):
		try:
			self.task_create_window.close()
		except:
			pass
		self.task_create_window.refresh_widgets()
		self.task_create_window.widget_taskCreation.rebuild_list_model(self.taskFolders)
		self.task_create_window.show()

class TaskItem(QTreeWidgetItem):
	def __init__(self, **kwargs):
		super(TaskItem, self).__init__()

		display = kwargs.get('display', 'task1')
		attrName = kwargs.get('attrName', 'task1')
		taskName = kwargs.get('taskName', '')
		task = kwargs.get('task', None)
		taskKwargs = kwargs.get('taskKwargs', {})
		check = kwargs.get('check', Qt.Checked)
		section = kwargs.get('section', '')
		taskType = kwargs.get('taskType', 'task')

		self.setText(0, display)
		self.setData(0, ROLE_TASK_NAME, attrName)
		self.setData(0, ROLE_TASK_FUNC_NAME, taskName)
		self.setData(0, ROLE_TASK_FUNC, task)
		self.setData(0, ROLE_TASK_KWARGS, taskKwargs)
		self.setData(0, ROLE_TASK_KWARGS_KEY, taskKwargs.keys())
		self.setData(0, ROLE_TASK_TYPE, taskType)
		self.setData(0, ROLE_TASK_PRE, 0)
		self.setData(0, ROLE_TASK_RUN, 0)
		self.setData(0, ROLE_TASK_POST, 0)
		self.setData(0, ROLE_TASK_SECTION, section)

		self.setFlags(self.flags()|Qt.ItemIsTristate|Qt.ItemIsUserCheckable)
		self.setCheckState(0, check)

		font = QFont()
		font.setPointSize(10)
		self.setFont(0, font)

		self.setIcon(0, QIcon(ICONS_TASK[taskType]))

	def setData(self, column, role, value):
		super(TaskItem, self).setData(column, role, value)
		# change icons if item is checked/unchecked
		if role == Qt.CheckStateRole:
			state = self.checkState(column)
			if state == Qt.Checked:
				# checked, go back to the icons previous
				taskReturn_pre = self.data(0, ROLE_TASK_PRE)
				taskReturn_run = self.data(0, ROLE_TASK_RUN)
				taskReturn_post = self.data(0, ROLE_TASK_POST)
				self.setIcon(1, QIcon(ICONS_STATUS[taskReturn_pre]))
				self.setIcon(2, QIcon(ICONS_STATUS[taskReturn_run]))
				self.setIcon(3, QIcon(ICONS_STATUS[taskReturn_post]))
			else:
				# unchecked, set icon to uncheck
				self.setIcon(1, QIcon(icons.unCheck))
				self.setIcon(2, QIcon(icons.unCheck))
				self.setIcon(3, QIcon(icons.unCheck))
		elif role == ROLE_TASK_PRE:
			# set icon for the pre build
			self.setIcon(1, QIcon(ICONS_STATUS[value]))
		elif role == ROLE_TASK_RUN:
			# set icon for the build
			self.setIcon(2, QIcon(ICONS_STATUS[value]))
		elif role == ROLE_TASK_POST:
			# set icon for the post build
			self.setIcon(3, QIcon(ICONS_STATUS[value]))

class ItemRunner(QThread):
	"""
	QThread to run items one by one
	
	use multi-threading so the ui won't be frozen,
	and can be stopped anytime
	"""
	QSignalProgress = Signal(int) # emit signal to update progress bar
	QSignalError = Signal() # emit signal for error
	QSignalPause = Signal() # emiet signal to pause
	def __init__(self, parent):
		super(ItemRunner, self).__init__(parent)
		self._parent = parent
		self._items = []
		self._ignoreCheck = False
		self._section = ['pre_build', 'build', 'post_build']
		self._roles = {'pre_build': ROLE_TASK_PRE,
					   'build': ROLE_TASK_RUN,
					   'post_build': ROLE_TASK_POST}

	def run(self):
		self.run_task()
		
	def run_task(self):
		# disable treeWidget when running
		self._parent.setEnabled(False)
		
		itemCount = float(len(self._items))
		for i, section in enumerate(self._section):
			role = self._roles[section]
			for j, item in enumerate(self._items):
				if self._parent._pause:
					self.QSignalPause.emit()
				while self._parent._pause:
					# in case need to be stopped from pause
					if self._parent._stop: 
						#self.QSignalError.emit()
						self._parent._pause = False				
					self.sleep(1) # pause the process

				# check if need to be stopped
				if self._parent._stop:
					break
			
				self._run_task_on_single_item(item, 
											  ignoreCheck=self._ignoreCheck,
											  section=section,
											  role=role)

				# emit signal
				self.QSignalProgress.emit(itemCount*i + j + 1)

			if self._parent._stop:
				# emit signal if need stop
				self.QSignalError.emit()
				logger.warn('Task process is stopped by the user')
				self._parent.setEnabled(True)# enable back widget if error
				break

		self._parent.setEnabled(True) # enable back widget when finished
				
	def _run_task_on_single_item(self, item, ignoreCheck=False, section='pre_build', 
								 role=ROLE_TASK_PRE):
		# get attributes from item
		display = item.text(0)
		name = item.data(0, ROLE_TASK_NAME)
		Task = item.data(0, ROLE_TASK_FUNC)
		kwargs = item.data(0, ROLE_TASK_KWARGS)
		checkState = item.checkState(0)	

		kwargs_run = {}
		for key, data in kwargs.iteritems():
			if 'value' in data and data['value'] != None:
				val = data['value']
			else:
				val = data['default']
			kwargs_run.update({key: val})

		if not ignoreCheck and checkState != Qt.Checked:
			# skip unchecked task
			return 
		
		# get section status, if already run, skipped
		taskReturn = item.data(0, role)
		if taskReturn > 0:
			# skip, task already runned
			return

		# check if registered function is a method
		if inspect.ismethod(Task):
			# get section registered
			section_init = item.data(0, ROLE_TASK_SECTION)
			if section != section_init:
				# skip
				item.setData(0, role, 1)
			else:
				# try to run function 
				try:
					taskReturn = Task(**kwargs_run)

					self._execute_setting(item, taskReturn, 'method', display, role)

				except Exception as e:
					self._error_setting(item, e, role)

		# check if registered function is a function (mainly for callback)
		elif inspect.isfunction(Task):
			# try to run function 
			try:
				if kwargs_run[section]:
					taskReturn = Task(kwargs_run[section])
				else:
					taskReturn = 1

				self._execute_setting(item, taskReturn, 'function', display, role)

			except Exception as e:
				self._error_setting(item, e, role)

		else:
			# Task is an imported task
			# try to run task
			try:
				# check if builder has obj or not
				if not hasattr(self._parent.builder, name):
					# either is pre-build, or skipped the pre-build
					# get obj
					TaskObj = Task(**kwargs_run)
					# attach obj to builder
					setattr(self._parent.builder, name, TaskObj)

				# run task
				TaskObj = getattr(self._parent.builder, name)
				taskReturn = getattr(TaskObj, section)()

				self._execute_setting(item, taskReturn, 'task', display, role)

			except Exception as e:
				self._error_setting(item, e, role)

	def _execute_setting(self, item, taskReturn, func, display, role):
		if taskReturn == 2:
			# warning raises
			item.setData(0, role, 2)
		else:
			# run succesfully
			item.setData(0, role, 1)
		
		# log
		logger.info('Run {} "{}" succesfully'.format(func, display))
	
	def _error_setting(self, item, e, role):
		# error raises
		item.setData(0, role, 3)
		# emit error signal
		self.QSignalError.emit()
		self._parent.setEnabled(True) # enable back widget if error
		logger.error(e)
		raise RuntimeError()
		
class SubMenu(QMenu):
	"""
	subMenu for right click menu
	include All, Pre-Build, Build, Post-Build
	and emit custom signal for furthur use
	"""
	QSignalSection = Signal(list)
	def __init__(self, title, parent=None, shortcut=''):
		super(SubMenu, self).__init__(title, parent)
		self.all = self.addAction('All')
		if shortcut:
			self.all.setShortcut(shortcut)
		self.pre = self.addAction('Pre-Build')
		self.build = self.addAction('Build')
		self.post = self.addAction('Post-Build')

		self.all.triggered.connect(self._all_triggered)
		self.pre.triggered.connect(self._pre_triggered)
		self.build.triggered.connect(self._build_triggered)
		self.post.triggered.connect(self._post_triggered)

	def _all_triggered(self):
		self.QSignalSection.emit(['pre_build', 'build', 'post_build'])

	def _pre_triggered(self):
		self.QSignalSection.emit(['pre_build'])

	def _build_triggered(self):
		self.QSignalSection.emit(['build'])

	def _post_triggered(self):
		self.QSignalSection.emit(['post_build'])

class TaskCreate(QDialog):
		"""widget to create task"""
		QSignalTaskCreation = Signal(list)
		def __init__(self, parent=None):
			super(TaskCreate, self).__init__(parent)

			self.setWindowTitle('Create Task')
			self.setGeometry(100, 100, 250, 300)

			self.init_widget()

		def init_widget(self):
			layout_base = QVBoxLayout()

			self.setLayout(layout_base)
		
			# task name
			self.task_name = QLineEdit()
			self.task_name.setPlaceholderText('Task Name...')
		
			layout_base.addWidget(self.task_name)

			# task display name
			self.task_display = QLineEdit()
			self.task_display.setPlaceholderText('Display Name (Optional)...')
		
			layout_base.addWidget(self.task_display)

			# get task creator widget
			self.widget_taskCreation = taskCreator.TaskCreator()
			layout_base.addWidget(self.widget_taskCreation)

			# create button
			self.button_create = QPushButton('Create')
			self.button_create.setFixedWidth(80)
			layout_base.addWidget(self.button_create)

			layout_base.setAlignment(self.button_create, Qt.AlignRight)

			self.button_create.clicked.connect(self._get_select_task)

		def refresh_widgets(self):
			self.task_name.setText('')
			self.task_display.setText('')
			self.widget_taskCreation.filter.setText('')
			self.setFocus()

		def _get_select_task(self):
			name = self.task_name.text()
			display = self.task_display.text()
			task = self.widget_taskCreation.listView.currentIndex().data()

			if name and task:
				self.QSignalTaskCreation.emit([name, display, task])

			self.close()

#=================#
#       Fix       #
#=================#
'''
For some reason, when I middle mouse drag the tasks, it freezed the ui,
and gave me an error when I try to use QWidget.close()

Base on what stack overflow said
	The problem is that multiprocessing must pickle things to sling them among processes, 
	and bound methods are not picklable. 
	The workaround (whether you consider it "easy" or not)
	is to add the infrastructure to your program to allow such methods to be pickled, 
	registering it with the copy_reg standard library method

Don't really know what this is, but it seems work well
'''
def _pickle_method(method):
	func_name = method.im_func.__name__
	obj = method.im_self
	cls = method.im_class
	return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
	for cls in cls.mro():
		try:
			func = cls.__dict__[func_name]
		except KeyError:
			pass
		else:
			break
	return func.__get__(obj, cls)

copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)