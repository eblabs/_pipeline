#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

# import PySide
from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance 

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#
class TreeWidget(QtWidgets.QTreeWidget):
	"""base class for TreeWidget"""
	def __init__(self, *args, **kwargs):
		super(TreeWidget, self).__init__(*args, **kwargs)
		
		# get kwargs
		self._header = kwargs.get('header', ['Task', 'Status'])

		self.init_widget()

	def init_widget(self):
		QHeader = QtWidgets.QTreeWidgetItem(self._header)
		self.setHeaderItem(QHeader)
		self.setRootIsDecorated(False)
		self.setAlternatingRowColors(True)
		self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
		self.setHeaderHidden(True)
		self.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
		self.header().setStretchLastSection(False)
		self.setColumnWidth(1,40)
		
	def add_tree_items(self, data, root='Root'):
		QTreeWidgetItem_root = QtWidgets.QTreeWidgetItem(self)
		QTreeWidgetItem_root.setText(0, root)
		QTreeWidgetItem_root.setFlags(QTreeWidgetItem_root.flags())

		self._add_child_item(QTreeWidgetItem_root, data)

		self.expandAll()

	def _add_child_item(self, QItem, data):
		for d in data:
			name = d.keys()[0]
			dataInfo = d[name]

			QTreeWidgetItem = QtWidgets.QTreeWidgetItem()
			QTreeWidgetItem.setText(0, name)
			QTreeWidgetItem.setFlags(QTreeWidgetItem.flags())

			QItem.addChild(QTreeWidgetItem)

			if 'children' in dataInfo:
				self._add_child_item(QTreeWidgetItem, dataInfo['children'])