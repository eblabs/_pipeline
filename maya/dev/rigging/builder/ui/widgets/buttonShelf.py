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

SC_REFRESH = 'Ctrl+r'
SC_RUN_ALL = 'Ctrl+Shift+Space'
SC_RUN_PAUSE = 'Ctrl+Space'
SC_STOP = 'ESC'
SC_REFRESH_RUN = 'Ctrl+Shift+r'

#=================#
#      CLASS      #
#=================#
class ButtonShelf(QWidget):
	"""docstring for ButtonShelf"""
	def __init__(self):
		super(ButtonShelf, self).__init__()
		
		self._pause = True
		self._run_all = False

		self.init_widget()

	def init_widget(self):
		layout_base = QHBoxLayout()
		self.setLayout(layout_base)

		self.button_refresh = Button(layout_base,
									 [icons.refresh, 
									  icons.refresh_disable],
									 shortcut=SC_REFRESH,
									 toolTip='Reload Rig Builder')
		self.button_run_all = Button(layout_base,
									 [icons.run_all, 
									  icons.run_all_disable],
									  shortcut=SC_RUN_ALL,
									  toolTip='Execute All Tasks')
		self.button_run_pause = Button(layout_base,
									   [icons.run, 
									    icons.pause],
									   shortcut=SC_RUN_PAUSE,
									   toolTip='Execute/Pause')
		self.button_stop = Button(layout_base,
								  [icons.stop, 
								   icons.stop_disable],
								   shortcut=SC_STOP,
								   toolTip='Stop Execution')
		self.button_refresh_run = Button(layout_base,
										 [icons.refresh_run, 
										  icons.refresh_run_disable],
										  shortcut=SC_REFRESH_RUN,
										  toolTip='Reload and Execute All')

		# set stop disabled
		self.button_stop.setEnabled(False)

		# connect signal
		self.button_run_all.clicked.connect(self.run_all_button_pressed)
		self.button_run_pause.clicked.connect(self.run_pause_button_pressed)
		self.button_stop.clicked.connect(self.stop_button_pressed)
		self.button_refresh_run.clicked.connect(self.refresh_run_button_pressed)

		# set shortcut
		self.button_refresh.setShortcut(SC_REFRESH)
		self.button_run_all.setShortcut(SC_RUN_ALL)
		self.button_run_pause.setShortcut(SC_RUN_PAUSE)
		self.button_stop.setShortcut(SC_STOP)
		self.button_refresh_run.setShortcut(SC_REFRESH_RUN)

		layout_base.addStretch() # add stretch so the buttons aligened from left

	def run_all_button_pressed(self):
		self._pause = False
		self._set_button(refresh=False, run_all=False,
						 run_pause=False, stop=True, refresh_run=False)

	def run_pause_button_pressed(self):
		self._pause = not self._pause
		if self._pause:
			# show run icon
			self._set_button(refresh=False, run_all=False,
							 run_pause=True, stop=True, refresh_run=False)
		else:
			# show pause
			self._set_button(refresh=False, run_all=False,
							 run_pause=False, stop=True, refresh_run=False)		

	def stop_button_pressed(self):
		self._pause = True
		self._set_button()

	def refresh_run_button_pressed(self):
		self._pause = False
		self._set_button(refresh=False, run_all=False,
						 run_pause=False, stop=True, refresh_run=False)

	def _set_button(self, refresh=True, run_all=True,
					run_pause=True, stop=False, refresh_run=True):
		# set refresh
		self.button_refresh.setEnabled(refresh)

		# set run all
		self.button_run_all.setEnabled(run_all)

		# set run pause
		if run_pause:
			self.button_run_pause.setIcon(QIcon(icons.run))
		else:
			self.button_run_pause.setIcon(QIcon(icons.pause))

		# set stop
		self.button_stop.setEnabled(stop)

		# set refresh run
		self.button_refresh_run.setEnabled(refresh_run)

class Button(QPushButton):
	"""docstring for Button"""
	def __init__(self, layout, icons, shortcut='', toolTip=''):
		super(Button, self).__init__()
		self._icons = icons
		self._shortcut = shortcut
		self._toolTip = toolTip
		self.init_widget()
		layout.addWidget(self)

	def init_widget(self):
		self.setIcon(QIcon(self._icons[0]))
		self.setIconSize(QSize(30,30))
		sizePolicy = QSizePolicy(QSizePolicy.Fixed, 
								 QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(True)
		self.setSizePolicy(sizePolicy)

		if self._shortcut:
			self.setShortcut(self._shortcut)
		if self._toolTip:
			self.setToolTip('{} [{}]'.format(self._toolTip, self._shortcut))

	def setEnabled(self, arg):
		super(Button, self).setEnabled(arg)
		if arg:
			# push button enabled
			self.setIcon(QIcon(self._icons[0]))
		else:
			# push button disabled
			self.setIcon(QIcon(self._icons[1]))

		