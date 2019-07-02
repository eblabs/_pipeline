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
	def __init__(self):
		super(TaskInfo, self).__init__()
		
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

	def _set_label(self, item):
		name = item.data(0, ROLE_TASK_NAME)
		func_name = item.data(0, ROLE_TASK_FUNC_NAME)
		self.label_name.setText(name)
		self.label_type.setText(func_name)

	def _refresh(self):
		self.label_name.setText('')
		self.label_type.setText('')

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

		