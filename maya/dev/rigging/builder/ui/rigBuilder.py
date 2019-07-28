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
		self.widget_rigInfo = rigInfo.RigInfo()
		self.widget_shelf = buttonShelf.ButtonShelf()
		self.widget_tree = treeWidget.TreeWidget()
		self.widget_progress = rigProgress.RigProgress()
		self.widget_taskInfo = taskInfo.TaskInfo()
		self.widget_propertyEditor = propertyEditor.PropertyEditor()
	
		# attach widget
		self.attach_rig_widget(self.widget_rigInfo, 'Rig Info', layout_left)
		self.attach_rig_widget(self.widget_shelf, '', layout_left, noSpace=True)
		self.attach_rig_widget(self.widget_tree, 'Build Info', layout_left)
		self.attach_rig_widget(self.widget_progress, '', layout_left)

		self.attach_rig_widget(self.widget_taskInfo, 'Task Info', layout_right)
		self.attach_rig_widget(self.widget_propertyEditor, 'Property Editor', layout_right)

		# connect signal
		self.connect_signals()

		# so it won't focus on QLineEidt when startup
		self.setFocus()

	def attach_rig_widget(self, widget, title, layout, noSpace=False):
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

	def connect_signals(self):
		# hook up buttons
		self.widget_shelf.QSignalReload.connect(self.tempLoad)
		self.widget_shelf.QSignalReload.connect(self.widget_propertyEditor.refresh)
		self.widget_shelf.QSignalReload.connect(self.widget_taskInfo.refresh)
		
		self.widget_shelf.QSignalExecute.connect(self.widget_tree.run_sel_tasks)
		self.widget_shelf.QSignalExecuteAll.connect(self.widget_tree.run_all_tasks)
		self.widget_shelf.QSignalPause.connect(self.widget_tree.pause_resume_tasks)
		self.widget_shelf.QSignalStop.connect(self.widget_tree.stop_tasks)

		# reset buttons to initial once task running completed
		self.widget_tree.itemRunner.finished.connect(self.widget_shelf.reset_all)
		# reset buttons to initial if error
		self.widget_tree.itemRunner.QSignalError.connect(self.widget_shelf.reset_all)
		
		# disable buttons when execute tasks
		self.widget_tree.QSignalExecute.connect(self.widget_shelf.execute_button_set)

		# progress bar
		# init progress bar settings
		self.widget_tree.QSignalProgressInit.connect(self.widget_progress.init_setting)
		# update progress
		self.widget_tree.itemRunner.QSignalProgress.connect(self.widget_progress.update_progress)
		# pause progress
		self.widget_shelf.QSignalPause.connect(self.widget_progress.pause_progress)
		# stop progress
		self.widget_tree.itemRunner.QSignalError.connect(self.widget_progress.stop_progress)
		
		# task info
		self.widget_tree.itemPressed.connect(self.widget_taskInfo.set_label)

		# task info edit attr name
		self.widget_taskInfo.QSignalAttrName.connect(self.widget_tree.set_attr_name)

		# reset attr name once updated
		self.widget_tree.QSignalAttrName.connect(self.widget_taskInfo.set_label)

		# property editor
		self.widget_tree.itemPressed.connect(self.widget_propertyEditor.init_property)

		# clear when not select anything
		self.widget_tree.QSignalClear.connect(self.widget_propertyEditor.refresh)
		self.widget_tree.QSignalClear.connect(self.widget_taskInfo.refresh)

		# disable/enable widgets
		self.widget_tree.itemRunner.started.connect(self.widget_rigInfo.enable_widget)
		self.widget_tree.itemRunner.started.connect(self.widget_taskInfo.enable_widget)
		self.widget_tree.itemRunner.started.connect(self.widget_propertyEditor.enable_widget)
		
		self.widget_tree.itemRunner.finished.connect(self.widget_rigInfo.enable_widget)
		self.widget_tree.itemRunner.finished.connect(self.widget_taskInfo.enable_widget)
		self.widget_tree.itemRunner.finished.connect(self.widget_propertyEditor.enable_widget)


	def tempLoad(self):
		path_builder = 'tests.chrTest'
		module, func = modules.import_module(path_builder)
		reload(module)
		builder = getattr(module, func)()
		builder.registertion()
		self.widget_tree.builder = builder
		self.widget_tree.reload_tasks()


		