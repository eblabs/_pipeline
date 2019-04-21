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

# import lib
import lib.common.packages as packages
import rigSys.ui.icon as icon
reload(icon)

class RigBuildInfoTreeWidget(QtGui.QTreeWidget):
	"""docstring for RigBuilderTreeWidget"""
	def __init__(self, *args, **kwargs):
		super(RigBuildInfoTreeWidget, self).__init__(*args, **kwargs)
		self.initWidget()

		# rig info
		self.project = None
		self.asset = None
		self.rig = None
		self.mode = 'publish'

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
		self.customContextMenuRequested.connect(self._rightClickedMenu)

		self._loadBuildScript()

	def _loadBuildScript(self):
		import rigSys.templates.animationRig as animationRig
		reload(animationRig)
		Build = animationRig.AnimationRig()
		Build.registertion()

		preBuildDict = Build._preBuild
		buildDict = Build._build
		postBuildDict = Build._postBuild

		sections = [preBuildDict, buildDict, postBuildDict]

		QTreeWidgetItem_asset = QtGui.QTreeWidgetItem(self)
		QTreeWidgetItem_asset.setText(0, 'Asset')
		QTreeWidgetItem_asset.setFlags(QTreeWidgetItem_asset.flags())
		self._setQTreeWidgetItemFontSize(QTreeWidgetItem_asset, 15)
			

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

	def _rightClickedMenu(self, QPos):
		QMenu= QtGui.QMenu(self)
		QAction_execute = QMenu.addAction('Execute')
		QAction_refresh = QMenu.addAction('Refresh')
		QAction_rebuild = QMenu.addAction('Rebuild')

		parentPosition = self.mapToGlobal(QtCore.QPoint(0, 0))        
		QMenu.move(parentPosition + QPos)

		QMenu.show()
		
	def keyPressEvent(self, event):
		if (event.key() == QtCore.Qt.Key_Escape and
			event.modifiers() == QtCore.Qt.NoModifier):
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		else:
			QtGui.QTreeWidget.keyPressEvent(self, event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		super(RigBuildInfoTreeWidget, self).mousePressEvent(event)

	def mouseDoubleClickEvent(self, event):
		pass
		