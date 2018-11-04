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

# -- import lib
import assets.lib.rigs as rigs

class CreateRigDialog(QtGui.QDialog):
	"""docstring for CreateRigDialog"""
	QSignalClose = QtCore.Signal()
	QSignalCreate = QtCore.Signal()

	def __init__(self, *args, **kwargs):
		super(CreateRigDialog, self).__init__(*args, **kwargs)
		self.rigName = ''
		self.rigType = ''

		self.setWindowTitle('Create Rig')
		self.setFixedSize(200,100)
		self.setWindowModality(QtCore.Qt.WindowModal)

		self.initWidget()
	def initWidget(self):
		QVBoxLayout = QtGui.QVBoxLayout(self)

		# rig name
		QHBoxLayout = QtGui.QHBoxLayout()
		QVBoxLayout.addLayout(QHBoxLayout)
		QLabel = QtGui.QLabel('Name:')
		self.QLineEdit = QtGui.QLineEdit()
		QHBoxLayout.addWidget(QLabel)
		QHBoxLayout.addWidget(self.QLineEdit)

		# rig type
		QHBoxLayout = QtGui.QHBoxLayout()
		QVBoxLayout.addLayout(QHBoxLayout)
		QLabel = QtGui.QLabel('Type:')
		self.QComboBox = QtGui.QComboBox()
		QHBoxLayout.addWidget(QLabel)
		QHBoxLayout.addWidget(self.QComboBox, 1)

		rigTypes = rigs.listRigTypes()
		for r in rigTypes:
			self.QComboBox.addItem(r)

		# create button
		self.QPushButton = QtGui.QPushButton('Create')
		QVBoxLayout.addWidget(self.QPushButton)
		self.QPushButton.setEnabled(False)

		# connect signals
		self.QLineEdit.textChanged.connect(self._setQPushButton)
		self.QPushButton.clicked.connect(self._createRig)

	def _setQPushButton(self):
		rigName = self.QLineEdit.text()
		if rigName:
			self.QPushButton.setEnabled(True)

	def _createRig(self):
		rigName = self.QLineEdit.text()
		rigType = self.QComboBox.currentText()
		check = QtGui.QMessageBox.question(self, 'Create Rig', 'Name: {}\n Type: {}'.format(rigName, rigType), 
											QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
		if check == QtGui.QMessageBox.Yes:
			self.rigName = rigName
			self.rigType = rigType
			self.QSignalCreate.emit()

	def hideEvent(self, event):
		self.QSignalClose.emit()
		super(CreateRigDialog, self).hideEvent(event)
		


		