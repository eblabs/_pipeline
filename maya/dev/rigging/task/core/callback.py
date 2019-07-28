#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import OrderedDict
from collections import OrderedDict

## import PySide widgets
try:
	from PySide2.QtWidgets import *
except ImportError:
	from PySide.QtGui import *

## import utils
import utils.common.logUtils as logUtils

#=================#
#   GLOBAL VARS   #
#=================#
logger = logUtils.get_logger()

_kwargs_ui = OrderedDict()
for section in ['pre_build', 'build', 'post_build']:
	_kwargs_ui.update({section: {'value': '',
							    'select': False,
							    'hint': 'Execute following code at '+section ,
							    'height': 100,
							    'widget': QPlainTextEdit}})

#=================#
#     FUNCTION    #
#=================#
def Callback(self, code):
	'''
	callback function

	used for tasks need callback

	it will show as QTreeWidgetItem(task) in the ui,
	but it's the only task not inherit from task class, just a function

	Args:
		self: this function will attached to the builder class, 
			  so we need self to get vars from builder
		code(str): the callback code we need to execute 
	'''
	if code:
		exec(code)




