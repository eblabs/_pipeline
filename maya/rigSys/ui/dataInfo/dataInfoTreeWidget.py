# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# import PySide
try:
	from PySide2 import QtCore, QtGui
	from shiboken2 import wrapInstance 
except ImportError:
	from PySide import QtCore, QtGui
	from shiboken import wrapInstance

class DataInfoTreeWidget(QtGui.QTreeView):
	"""docstring for DataInfoTreeWidget"""
	def __init__(self, *args, **kwargs):
		super(DataInfoTreeWidget, self).__init__(*args, **kwargs)
		
		self.QSourceModel = QtGui.QStandardItemModel(0,2)
		self.QSourceModel.setHeaderData(0, QtCore.Qt.Horizontal, "Parameter")
		self.QSourceModel.setHeaderData(1, QtCore.Qt.Horizontal, "Value")
		self.setRootIsDecorated(False)
		self.setAlternatingRowColors(True)
		self.setHeaderHidden(True)
		self.setModel(self.QSourceModel)
		self.setSourceModelVal()

	def setSourceModelVal(self):
		valDict = {'parameters': {'file': ['test', 'all'],
								  'debug': False,
								  'name': 'nameTest'},
				   'order': ['file', 'debug', 'name']}

		if 'order' not in valDict:
			valDict.update(valDict['parameters'].keys())

		#valDict['order'].reverse()

		for i, parm in enumerate(valDict['order']):
			self.QSourceModel.insertRow(0)
			self.QSourceModel.setData(self.QSourceModel.index(0, 0), parm)
			self.QSourceModel.setData(self.QSourceModel.index(0, 1), valDict['parameters'][parm])
			# QItem_parm = QtGui.QStandardItem(parm)
			# QItem_val = QtGui.QStandardItem(str(valDict['parameters'][parm]))
			# #QItem_val.setData(valDict['parameters'][parm], QtCore.Qt.UserRole)
			# self.QSourceModel.appendRow([QItem_parm, QItem_val])
		