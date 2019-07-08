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

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

TT_TASK_NAME = 'Task Name used in the build script as attribute'
TT_TASK_TYPE = 'Task function path'

ROLE_TASK_NAME = Qt.UserRole + 1
ROLE_TASK_FUNC_NAME = Qt.UserRole + 2

#=================#
#      CLASS      #
#=================#
class TaskInfo(QWidget):
	"""
	class for task info widget
	
	use this widget to show task's important information
	task name
	task type
	"""
	QSignalAttrName = Signal(str)
	def __init__(self):
		super(TaskInfo, self).__init__()
		self._enable = True
		self.init_widget()

	def init_widget(self):
		layout_base = QVBoxLayout()
		self.setLayout(layout_base)

		for section, tip in zip(['name', 'type'],
								[TT_TASK_NAME, TT_TASK_TYPE]):
			# task label
			label_section = TaskLabel(toolTip=tip)

			# add obj to class for further use
			setattr(self, 'label_'+section, label_section)

			# add section to base layout
			layout_base.addWidget(label_section)

		self.label_name.action_edit.triggered.connect(self.edit_name_widget)

	def set_label(self, item):
		name = item.data(0, ROLE_TASK_NAME)
		func_name = item.data(0, ROLE_TASK_FUNC_NAME)
		self.label_name.setText(name)
		self.label_type.setText(func_name)

	def refresh(self):
		self.setEnabled(True)
		self.label_name.setText('')
		self.label_type.setText('')

	def enable_widget(self):
		self._enable = not self._enable
		self.setEnabled(self._enable)

	def edit_name_widget(self):
		title = "Change task's attribute name in the builder"
		text = "This will break all functions call this attribute in the builder, \nare you sure you want to change it?"
		reply = QMessageBox.warning(self, title, text, 
							QMessageBox.Ok | QMessageBox.Cancel, 
							defaultButton=QMessageBox.Cancel)
		
		if reply != QMessageBox.Ok:
			return

		# change the attr name
		current_name = self.label_name.text()
		text, ok = QInputDialog.getText(self, 'Attribute Name','Set Attribute Name', text=current_name)
		if text and ok and text != current_name:
			self.QSignalAttrName.emit(text)

class TaskLabel(QLabel):
	"""
	label to show task info for each section

	"""
	def __init__(self, toolTip=''):
		super(TaskLabel, self).__init__()

		self._toolTip = toolTip
		
		self.init_widget()

	def init_widget(self):
		# set stylesheet
		self.setStyleSheet("""border: 1.3px solid black;
							border-radius: 2px""")
		if self._toolTip:
			self.setToolTip(self._toolTip)

		self.right_click_menu()

		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self._show_menu)

	def right_click_menu(self):
		self.menu = QMenu()
		self.action_edit = self.menu.addAction('Edit')

	def _show_menu(self, QPos):
		if self.text():
			pos_parent = self.mapToGlobal(QPoint(0, 0))        
			self.menu.move(pos_parent + QPos)

			self.menu.show()


		