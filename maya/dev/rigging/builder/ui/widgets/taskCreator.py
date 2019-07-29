#=================#
# IMPORT PACKAGES #
#=================#

# import system packages
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

## import utils
import utils.common.logUtils as logUtils
import utils.common.files as files
import utils.common.modules as modules
#=================#
#   GLOBAL VARS   #
#=================#
logger = logUtils.get_logger()

#=================#
#      CLASS      #
#=================#
class TaskCreator(QWidget):
	"""widget to create task"""
	def __init__(self):
		super(TaskCreator, self).__init__()
		
		self.init_widget()

	def init_widget(self):
		layout_base = QVBoxLayout()
		layout_base.setContentsMargins(0,0,0,0)
		self.setLayout(layout_base)

		# filter
		self.filter = QLineEdit()
		self.filter.setPlaceholderText('Task Type Filter...')
		
		layout_base.addWidget(self.filter)

		# task list
		self.sourceModel = QStandardItemModel()
		self.proxyModel = QSortFilterProxyModel()
		self.proxyModel.setDynamicSortFilter(True)
		self.proxyModel.setSourceModel(self.sourceModel)

		self.listView = TaskListView()
		self.listView.setModel(self.proxyModel)

		layout_base.addWidget(self.listView)

		self.filter.textChanged.connect(self.filter_reg_exp_changed)

		self.setFocus()

	def rebuild_list_model(self, taskFolders):
		self.sourceModel.clear()
		tasks = get_tasks_from_folders(taskFolders)

		for tsk in tasks:
			tsk_item = QStandardItem(tsk)
			self.sourceModel.appendRow(tsk_item)

	def filter_reg_exp_changed(self):
		regExp = QRegExp(self.filter.text(), Qt.CaseInsensitive)
		self.proxyModel.setFilterRegExp(regExp)

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Down and self.filter.hasFocus():
			# move to the first task show in list
			index = self.proxyModel.index(0,0)
			self.listView.setFocus()
			self.listView.setCurrentIndex(index)
			

			
class TaskListView(QListView):
	"""
	Task List View
	
	sub class from QListView, remove some mouse function

	"""
	def __init__(self, parent=None):
		super(TaskListView, self).__init__(parent)
	
	def keyPressEvent(self, event):
		if (event.key() == Qt.Key_Escape and
			event.modifiers() == Qt.NoModifier):
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QModelIndex())
		else:
			super(TaskListView, self).keyPressEvent(event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self._clear_selection()			
		super(TaskListView, self).mousePressEvent(event)

	def mouseDoubleClickEvent(self, event):
		pass

	def focusInEvent(self, event):
		super(TaskListView, self).focusInEvent(event)
		self.setCurrentIndex(QModelIndex()) # remove focus

	# def focusOutEvent(self, event):
	# 	super(TaskListView, self).focusOutEvent(event)
	# 	# clear selection when focus out
	# 	self._clear_selection()

	def _clear_selection(self):
		self.clearSelection()
		self.clearFocus()
		self.setCurrentIndex(QModelIndex())
		
		

#=================#
#    Function     #
#=================#
def get_tasks_from_folders(taskFolders):
	'''
	get all task paths from folders
	
	Args:
		taskFolders(list): task folder paths
						   need to be in python way
						   like 'dev.rigging.task.core'
	Return:
		taskPaths(list)
	'''
	taskPaths = []

	for folderPath in taskFolders:
		# get absolute path by import module
		folder_mod, func = modules.import_module(folderPath)
		if folder_mod:
			folderPath_abs = os.path.dirname(folder_mod.__file__)

			# get task files
			taskNames = files.get_files_from_path(folderPath_abs,
												  extension='.py',
												  exceptions='__init__',
												  fullPath=False)

			for tsk_n in taskNames:
				task = '{}.{}'.format(folderPath, tsk_n[:-3]) # remove extension .py
				taskPaths.append(task)

	taskPaths.sort()

	return taskPaths
