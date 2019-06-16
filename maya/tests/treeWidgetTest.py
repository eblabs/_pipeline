try:
	from PySide2 import QtCore, QtGui
	from shiboken2 import wrapInstance 
except ImportError:
	from PySide import QtCore, QtGui
	from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI

class TreeUI(QtGui.QWidget):
	def __init__(self, parent=None):
		super(TreeUI, self).__init__()
		self.initUI()

	def initUI(self):
		QHeader = QtGui.QTreeWidgetItem(['FUNCTION', 'STATUS'])


class TreeWidget(QtGui.QTreeWidget):
	"""docstring for TreeWidget"""
	def __init__(self, *arg, **kwargs):
		super(TreeWidget, self).__init__()
		self.initWidget()

	def initWidget(self):
		QHeader = QtGui.QTreeWidgetItem(['Function', 'Status'])
		self.setHeaderItem(QHeader)
		self.setRootIsDecorated(False)
		self.setAlternatingRowColors(True)
		self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.setHeaderHidden(True)
		self.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
		self.header().setStretchLastSection(False)
		self.setColumnWidth(1,40)
		#self.setStyleSheet("font: 10pt")

		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self._loadBuildScript()
	
	def _loadBuildScript(self):
		self._data = [{'task1': {'display': 'task1',
						 'children': [
						 			  {'task2': {'display': 'task2'}},
						 			  {'task3': {'display': 'task3',
						 			  			 'children': [{'task4': {'display': 'task4'}}]}}]}},
			  {'task5': {'display': 'task5'}},
			  {'task6': {'display': 'task6',
			  			 'children': [{'task7': {'display': 'task7'}},
			  			 			  {'task8': {'display': 'task8'}}]}}]
		for sectionInfo in zip(sections, ['PreBuild', 'Build', 'PostBuild']):
			QTreeWidgetItem_section = QtGui.QTreeWidgetItem(QTreeWidgetItem_asset)
			QTreeWidgetItem_section.setText(0, sectionInfo[1])
			QTreeWidgetItem_section.setFlags(QTreeWidgetItem_section.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
			QTreeWidgetItem_section.setCheckState(0, QtCore.Qt.Checked)
			self._setQTreeWidgetItemFontSize(QTreeWidgetItem_section, 12)

			for funcName in sectionInfo[0]['order']:
				QTreeWidgetItem_func = QtGui.QTreeWidgetItem()
				QTreeWidgetItem_func.setText(0, funcName)
				QTreeWidgetItem_func.setIcon(1, QtGui.QIcon(icon.QTreeWidgetItem_initial))
				QTreeWidgetItem_func.setFlags(QTreeWidgetItem_func.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
				QTreeWidgetItem_func.setCheckState(0, QtCore.Qt.Checked)
				self._setQTreeWidgetItemFontSize(QTreeWidgetItem_func, 10)

				QTreeWidgetItem_section.addChild(QTreeWidgetItem_func)

		self.expandAll()

	def _setQTreeWidgetItemFontSize(self, QTreeWidgetItem, size):
		QFont = QTreeWidgetItem.font(0)
		QFont.setPointSize(size)
		QTreeWidgetItem.setFont(0,QFont)