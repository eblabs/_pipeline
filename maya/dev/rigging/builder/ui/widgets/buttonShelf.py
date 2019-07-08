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

# import icon
import icons

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

SC_RELOAD = 'Ctrl+R'
SC_EXECUTE_ALL = 'Ctrl+Shift+Space'
SC_EXECUTE_PAUSE = 'Ctrl+Space'
SC_STOP = 'ESC'
SC_RELOAD_EXECUTE = 'Ctrl+Shift+R'

#=================#
#      CLASS      #
#=================#
class ButtonShelf(QWidget):
	"""docstring for ButtonShelf"""
	QSignalReload = Signal()
	QSignalExecute = Signal(list)
	QSignalPause = Signal()
	QSignalStop = Signal()
	QSignalExecuteAll = Signal(list)
	def __init__(self):
		super(ButtonShelf, self).__init__()
		
		self._pause = False
		self._running = False

		self.init_widget()

	def init_widget(self):
		layout_base = QHBoxLayout()
		self.setLayout(layout_base)
		layout_base.setSpacing(2)
		layout_base.setContentsMargins(2, 2, 2, 2)

		self.button_reload = Button(layout_base,
									 [icons.reload, 
									  icons.reload_disabled],
									 shortcut=SC_RELOAD,
									 toolTip='Reload Rig Builder[{}]'.format(SC_RELOAD))
		self.button_execute_all = Button(layout_base,
									 [icons.execute_all, 
									  icons.execute_all_disabled],
									  shortcut=SC_EXECUTE_ALL,
									  toolTip='Execute All Tasks[{}]'.format(SC_EXECUTE_ALL),
									  subMenu=True)
		self.button_execute_sel = Button(layout_base,
									   [icons.execute_select, 
									    icons.execute_select_disabled],
									   shortcut=SC_EXECUTE_PAUSE,
									   toolTip='Execute Selection[{}]'.format(SC_EXECUTE_PAUSE),
									   subMenu=True)
		self.button_reload_execute = Button(layout_base,
										 [icons.reload_execute, 
										  icons.reload_execute_disabled],
										  shortcut=SC_RELOAD_EXECUTE,
										  toolTip='Reload and Execute All[{}]'.format(SC_RELOAD_EXECUTE),
										  subMenu=True)
		self.button_pause_resume = Button(layout_base,
									   [icons.pause, 
									    icons.pause_disabled],
									   shortcut=SC_EXECUTE_PAUSE,
									   toolTip='Execute Selection[{}]'.format(SC_EXECUTE_PAUSE))
		self.button_stop = Button(layout_base,
								  [icons.stop, 
								   icons.stop_disabled],
								   shortcut=SC_STOP,
								   toolTip='Stop Execution[{}]'.format(SC_STOP))
		

		# set stop disabled
		self.button_pause_resume.setEnabled(False)
		self.button_stop.setEnabled(False)

		# connect signal
		self.button_reload.clicked.connect(self.reload_pressed)

		self.button_execute_all.clicked.connect(self.execute_all_pressed)
		self.button_execute_all.subMenu.QSignalSection.connect(self.execute_all_pressed)

		self.button_execute_sel.clicked.connect(self.execute_sel_pressed)
		self.button_execute_sel.subMenu.QSignalSection.connect(self.execute_sel_pressed)

		self.button_reload_execute.clicked.connect(self.reload_execute_pressed)
		self.button_reload_execute.subMenu.QSignalSection.connect(self.reload_execute_pressed)

		self.button_pause_resume.clicked.connect(self.pause_resume_pressed)

		self.button_stop.clicked.connect(self.stop_pressed)

		layout_base.addStretch() # add stretch so the buttons aligened from left

	def reload_pressed(self):
		self._pause = False
		self.QSignalReload.emit()

	# execute all button functions

	def execute_all_pressed(self, section=['pre_build', 
										'build', 
										'post_build']):
		#self.execute_button_set()
		self.QSignalExecuteAll.emit(section)

	# execute select button functions
	def execute_sel_pressed(self, section=['pre_build', 
										'build', 
										'post_build']):
		#self.execute_button_set()
		self.QSignalExecute.emit(section)

	# reload execute all button function
	def reload_execute_pressed(self, section=['pre_build', 
										   'build', 
										   'post_build']):
		#self.execute_button_set()
		self.QSignalReload.emit()
		self.QSignalExecuteAll.emit(section)

	def execute_button_set(self):
		self._set_button(reload_val=False, execute_all_val=False,
					execute_sel_val=False, pause_resume_val=True, 
					stop_val=True, reload_execute_val=False)
		self._pause_resume_set(pause_resume_val=False)

	def pause_resume_pressed(self):
		self._pause = not self._pause
		self._set_button(reload_val=False, execute_all_val=False,
					execute_sel_val=False, pause_resume_val=True, 
					stop_val=True, reload_execute_val=False)
		self._pause_resume_set(pause_resume_val=self._pause)
		self.QSignalPause.emit()

	def stop_pressed(self):
		self._pause = False
		self._set_button()
		self._pause_resume_set(pause_resume_val=False)
		self.QSignalStop.emit()

	def reset_all(self):
		self._pause = False
		self._set_button()

	def _set_button(self, reload_val=True, execute_all_val=True,
					execute_sel_val=True, pause_resume_val=False, 
					stop_val=False, reload_execute_val=True):
		# set reload button
		self.button_reload.setEnabled(reload_val)

		# set execute all button
		self.button_execute_all.setEnabled(execute_all_val)

		# set execute select button
		self.button_execute_sel.setEnabled(execute_sel_val)

		# set reload execute button
		self.button_reload_execute.setEnabled(reload_execute_val)

		# set pause resume button
		self.button_pause_resume.setEnabled(pause_resume_val)

		# set stop button
		self.button_stop.setEnabled(stop_val)

	def _pause_resume_set(self, pause_resume_val=False):
		if pause_resume_val:
			self.button_pause_resume.setIcon(QIcon(icons.resume))
		else:
			self.button_pause_resume.setIcon(QIcon(icons.pause))

class Button(QPushButton):
	"""docstring for Button"""
	def __init__(self, layout, icons, shortcut='', toolTip='', subMenu=False):
		super(Button, self).__init__()
		self._icons = icons
		self._shortcut = shortcut
		self._toolTip = toolTip
		self._subMenu = subMenu
		self.init_widget()
		layout.addWidget(self)

	def init_widget(self):
		size = 25
		self.setIcon(QIcon(self._icons[0]))
		self.setIconSize(QSize(size,size))
		# resize button so no gap for the icon
		self.setFixedHeight(size) 
		self.setFixedWidth(size)

		if self._shortcut:
			self.setShortcut(self._shortcut)
		if self._toolTip:
			self.setToolTip('{} [{}]'.format(self._toolTip, self._shortcut))
		if self._subMenu:
			self.subMenu = SubMenu()
			self.setContextMenuPolicy(Qt.CustomContextMenu)
			self.customContextMenuRequested.connect(self._show_menu)			

	def setEnabled(self, arg):
		super(Button, self).setEnabled(arg)
		if arg:
			# push button enabled
			self.setIcon(QIcon(self._icons[0]))
		else:
			# push button disabled
			self.setIcon(QIcon(self._icons[1]))

	def _show_menu(self, QPos):
		pos_parent = self.mapToGlobal(QPoint(0, 0))        
		self.subMenu.move(pos_parent + QPos)

		self.subMenu.show()

class SubMenu(QMenu):
	"""
	sub menu for buttons, 
	include pre-build-post
	emit custom signal for furthur use
	"""
	QSignalSection = Signal(list)
	def __init__(self):
		super(SubMenu, self).__init__()
		
		self.pre = self.addAction('Pre-Build')
		self.build = self.addAction('Build')
		self.post = self.addAction('Post-Build')

		self.pre.triggered.connect(self._pre_triggered)
		self.build.triggered.connect(self._build_triggered)
		self.post.triggered.connect(self._post_triggered)

	def _pre_triggered(self):
		self.QSignalSection.emit(['pre_build'])

	def _build_triggered(self):
		self.QSignalSection.emit(['build'])

	def _post_triggered(self):
		self.QSignalSection.emit(['post_build'])
		

		