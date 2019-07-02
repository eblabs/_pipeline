#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import PySide
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

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.uiUtils as uiUtils

## import widgets
import widgets.treeWidget as treeWidget
import widgets.propertyEditor as propertyEditor
import widgets.buttonShelf as buttonShelf
import widgets.rigInfo as rigInfo
import widgets.rigProgress as rigProgress
import widgets.taskInfo as taskInfo

# import common
import utils.common.modules as modules

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#

class RigBuilder(uiUtils.BaseWindow):
	"""class for RigBuilder UI"""
	def __init__(self, **kwargs):
		super(RigBuilder, self).__init__(**kwargs)
			
	def init_UI(self):
		self._title = 'Rig Builder'
		super(RigBuilder, self).init_UI()
		'''
		rig builder layout
		'''

		# base layout
		layout_base = QGridLayout(self)
		self.setLayout(layout_base)

		# splitter
		splitter_base = QSplitter()
		layout_base.addWidget(splitter_base)

		# left layout
		frame_left = QFrame()
		frame_left.setMinimumSize(320, 700)
		layout_left = QVBoxLayout(frame_left)

		# rig layout
		frame_right = QFrame()
		frame_right.setMinimumSize(320, 700)
		layout_right = QVBoxLayout(frame_right)

		# attach frame
		splitter_base.addWidget(frame_left)
		splitter_base.addWidget(frame_right)

		# splitter setting
		splitter_base.setCollapsible(0, False)
		splitter_base.setCollapsible(1, False)
		splitter_base.setStretchFactor(0, 1)
		splitter_base.setStretchFactor(1, 2)


		# widgets
		self._widget_rigInfo = rigInfo.RigInfo()
		self._widget_shelf = buttonShelf.ButtonShelf()
		self._widget_tree = treeWidget.TreeWidget()
		self._widget_progress = rigProgress.RigProgress()
		self._widget_taskInfo = taskInfo.TaskInfo()
		self._widget_propertyEditor = propertyEditor.PropertyEditor()
	
		# attach widget
		self._attach_rig_widget(self._widget_rigInfo, 'Rig Info', layout_left)
		self._attach_rig_widget(self._widget_shelf, '', layout_left, noSpace=True)
		self._attach_rig_widget(self._widget_tree, 'Build Info', layout_left)
		self._attach_rig_widget(self._widget_progress, '', layout_left)

		self._attach_rig_widget(self._widget_taskInfo, 'Task Info', layout_right)
		self._attach_rig_widget(self._widget_propertyEditor, 'Property Editor', layout_right)

		# connect signal
		self._connect_signals()

		# so it won't focus on QLineEidt when startup
		self.setFocus()

	def _attach_rig_widget(self, widget, title, layout, noSpace=False):
		groupBox = QGroupBox(title)
		groupBox.setStyleSheet("""QGroupBox {
												border: 1px solid gray;
												border-radius: 2px;
												margin-top: 0.5em;
											}

											QGroupBox::title {
												subcontrol-origin: margin;
												left: 10px;
												padding: 0 3px 0 3px;
											}""")
		layout_widget = QGridLayout(groupBox)
		if noSpace:
			layout_widget.setContentsMargins(0,0,0,0)
		layout_widget.addWidget(widget)
		layout.addWidget(groupBox)

	def _connect_signals(self):
		# hook up buttons
		self._widget_shelf.QSignalRun.connect(self._widget_tree._run_tasks)
		self._widget_shelf.QSignalPause.connect(self._widget_tree._pause_tasks)
		self._widget_shelf.QSignalRunAll.connect(self._widget_tree._run_all_tasks)
		self._widget_shelf.QSignalStop.connect(self._widget_tree._stop_tasks)
		
		# reset buttons to initial once task running completed
		self._widget_tree._itemRunner.finished.connect(self._widget_shelf._reset_all)
		# reset buttons to initial if error
		self._widget_tree._itemRunner.QSignalError.connect(self._widget_shelf._reset_all)
		
		# progress bar
		# init progress bar settings
		self._widget_tree.QSignalProgressInit.connect(self._widget_progress._init_setting)
		# update progress
		self._widget_tree._itemRunner.QSignalProgress.connect(self._widget_progress._update_progress)
		# pause progress
		self._widget_tree._itemRunner.QSignalPause.connect(self._widget_progress._pause_progress)
		# stop progress
		self._widget_tree._itemRunner.QSignalError.connect(self._widget_progress._stop_progress)
		
		# task info
		self._widget_tree.itemClicked.connect(self._widget_taskInfo._set_label)

		# property editor
		self._widget_tree.itemClicked.connect(self._widget_propertyEditor._init_property)

		# refresh
		self._widget_shelf.QSignalRefresh.connect(self.tempLoad)
		self._widget_shelf.QSignalRefresh.connect(self._widget_propertyEditor._refresh)
		self._widget_shelf.QSignalRefresh.connect(self._widget_taskInfo._refresh)

		# double click
		self._widget_tree.QSignalDoubleClick.connect(self._widget_shelf.run_pause_button_pressed)
		
	def tempLoad(self):
		path_builder = 'tests.chrTest'
		module, func = modules.import_module(path_builder)
		reload(module)
		builder = getattr(module, func)()
		builder.registertion()
		self._widget_tree._Builder = builder
		self._widget_tree._refresh_tasks()


		