## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI
import os
try:
	from PySide import QtGui
	from PySide import QtCore
	from shiboken import wrapInstance
except:
	from PyQt4 import QtGui
	from PyQt4 import QtCore
	from sip import wrapinstance as wrapInstance

## libs Import
import common.workspaces as workspaces
import common.files as files
reload(workspaces)
reload(files)

## rig Build UI
class rigBuilderUI(QtGui.QWidget):
	"""docstring for rigBuilderUI"""
	VERSION, FILENAME = range(2)
	def __init__(self, sParent = None):
		super(rigBuilderUI, self).__init__()
		
		self.dAssetData = None
		self.sPath = None

		#Parent widget under Maya main window        
		self.setParent(sParent)       
		self.setWindowFlags(QtCore.Qt.Window)

		#Set the object name     
		self.setObjectName('rigBuilder_uniqueId')        
		self.setWindowTitle('Rig Builder')        
		self.setGeometry(100, 100, 1000, 800) 
		self.initUI()

	def initUI(self):
		QLayoutBase = QtGui.QHBoxLayout(self)
		self.setLayout(QLayoutBase)

		QFrame_left = QtGui.QFrame()
		QLayoutBase.addWidget(QFrame_left)
		QFrame_left.setFixedWidth(300)
		QVBoxLayout_left = QtGui.QVBoxLayout(QFrame_left)
		self.projectInfoUI(QVBoxLayout_left)
		self.tabWidgetUI(QVBoxLayout_left)

		QFrame_middle = QtGui.QFrame()
		QLayoutBase.addWidget(QFrame_middle)
		QFrame_middle.setMinimumWidth(600)
		QVBoxLayout_middle = QtGui.QVBoxLayout(QFrame_middle)
		self.rigBuildInfoUI(QVBoxLayout_middle)

		QFrame_right = QtGui.QFrame()
		QLayoutBase.addWidget(QFrame_right)
		QFrame_right.setFixedWidth(400)
		QVBoxLayout_right = QtGui.QVBoxLayout(QFrame_right)
		self.rigDataInfoUI(QVBoxLayout_right)
		self.progressBarUI(QVBoxLayout_right)

	## project info
	def projectInfoUI(self, QLayout):
		QGroupBox = QtGui.QGroupBox()
		QGroupBox.setTitle('Project Info')
		QLayout.addWidget(QGroupBox)

		QVBoxLayout = QtGui.QVBoxLayout(QGroupBox)

		for sName in ['Project', 'Asset']:
			QHBoxLayout_each = QtGui.QHBoxLayout()
			QVBoxLayout.addLayout(QHBoxLayout_each)

			QLabel_each = QtGui.QLabel('%s:' %sName)
			QLineEdit_each = QtGui.QLineEdit()
			QHBoxLayout_each.addWidget(QLabel_each)
			QHBoxLayout_each.addWidget(QLineEdit_each)

		QPushButton = QtGui.QPushButton('Load')
		QPushButton.setMinimumHeight(40)
		QVBoxLayout.addWidget(QPushButton)
		#QPushButton.setEnabled(False)
		QPushButton.setStyleSheet('background-color:rgb(255,100,100)')
		QPushButton.clicked.connect(self.__loadBuildScriptCmd)

	## components
	def tabWidgetUI(self, QLayout):
		QTabWidget = QtGui.QTabWidget()
		QLayout.addWidget(QTabWidget)

		# component
		oWidgetComponent = scrollableWidget()
		QTabWidget.addTab(oWidgetComponent.QWidget, 'Components')
		self.componentsUI(oWidgetComponent.QVBoxLayout)

		# publish
		oWidgetPublish = scrollableWidget()
		QTabWidget.addTab(oWidgetPublish.QWidget, 'Publish')
		self.publishUI(oWidgetPublish.QVBoxLayout)

		#load save
		oWidgetLoadSave = scrollableWidget()
		QTabWidget.addTab(oWidgetLoadSave.QWidget, 'Load/Save')
		self.loadSaveUI(oWidgetLoadSave.QVBoxLayout)

	def componentsUI(self, QLayout):

		QLayout.setAlignment(QtCore.Qt.AlignTop)

		lWidgetComponents = []
		for sComponent in ['All', 'Build Script', 'Blueprint', 'Rig Geometry', 'Deformers', 'Controller Shapes', 'Geo Hierarchy', 'Model']:
			oWidgetComponent = collapseWidget(sTitle = sComponent)
			QLayout.addWidget(oWidgetComponent)
			lWidgetComponents.append(oWidgetComponent)

		## All
		QPushButton_allMigrate = lWidgetComponents[0].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Migrate All Components'))
		QPushButton_allPull = lWidgetComponents[0].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Pull All Components'))
		QPushButton_allPush = lWidgetComponents[0].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Push All Components'))

		## Build Script
		self.componentsButtonSet(lWidgetComponents[1].QVBoxLayout_frame)
		QPushButton_template = lWidgetComponents[1].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Create Template'))

		## Blueprint
		self.componentsButtonSet(lWidgetComponents[2].QVBoxLayout_frame)
		QPushButton_importBp = lWidgetComponents[2].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Import Blueprint'))
		QPushButton_saveBp = lWidgetComponents[2].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Save Blueprint'))

		## Rig Geometry
		self.componentsButtonSet(lWidgetComponents[3].QVBoxLayout_frame)
		QPushButton_importRigGeo = lWidgetComponents[3].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Import Rig Geometry'))
		QPushButton_exportRigGeo = lWidgetComponents[3].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Export Selection'))

		## Deformers
		self.componentsButtonSet(lWidgetComponents[4].QVBoxLayout_frame)
		QPushButton_loadDeformers = lWidgetComponents[4].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Load Deformers'))
		QPushButton_saveDeformers = lWidgetComponents[4].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Save Deformers'))

		## Controller Shapes
		self.componentsButtonSet(lWidgetComponents[5].QVBoxLayout_frame)
		QPushButton_loadCtrlShapes = lWidgetComponents[5].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Load Controller Shapes'))
		QPushButton_saveCtrlShapes = lWidgetComponents[5].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Save Controller Shapes'))

		## Geo Hierarchy
		self.componentsButtonSet(lWidgetComponents[6].QVBoxLayout_frame)
		QPushButton_loadGeoHie = lWidgetComponents[6].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Load Geo Hierarchy'))
		QPushButton_saveGeoHie = lWidgetComponents[6].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Save Geo Hierarchy'))

		## Model
		QPushButton_importModel = lWidgetComponents[7].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Import Model'))
		QPushButton_refModel = lWidgetComponents[7].QVBoxLayout_frame.addWidget(QtGui.QPushButton('Reference Model'))

	def componentsButtonSet(self, QLayout):
		QHBoxLayout = QtGui.QHBoxLayout()
		QLayout.addLayout(QHBoxLayout)

		QPushButton_explore = QHBoxLayout.addWidget(QtGui.QPushButton('Explore'))
		QPushButton_pull = QHBoxLayout.addWidget(QtGui.QPushButton('Pull'))
		QPushButton_push = QHBoxLayout.addWidget(QtGui.QPushButton('Push'))

	def publishUI(self, QLayout):
		QLayout.setAlignment(QtCore.Qt.AlignTop)
		#Tag
		QLayoutTag = QtGui.QHBoxLayout(self)
		QLayout.addLayout(QLayoutTag)

		QLabelTag = QtGui.QLabel('Tag:')
		QLabelTag.setMaximumHeight(20)
		QLayoutTag.addWidget(QLabelTag)

		QLineEditTag = QtGui.QLineEdit()
		QLayoutTag.addWidget(QLineEditTag)

		#Comment
		QLayoutComment = QtGui.QVBoxLayout(self)
		QLayout.addLayout(QLayoutComment)

		QLabelComment = QtGui.QLabel('Comment:')
		QLabelComment.setMaximumHeight(20)
		QLayoutComment.addWidget(QLabelComment)

		QLineEditComment = QtGui.QLineEdit()
		QLineEditComment.setMinimumHeight(100)
		QLineEditComment.setAlignment(QtCore.Qt.AlignTop)
		QLayoutComment.addWidget(QLineEditComment)

		#Button
		QPushButton = QtGui.QPushButton('Publish')
		QPushButton.setMinimumHeight(60)
		QPushButton.setStyleSheet('background-color:rgb(255,100,100)')
		QLayout.addWidget(QPushButton)

	def loadSaveUI(self, QLayout):
		QLayout.setAlignment(QtCore.Qt.AlignTop)

		#Versions
		QSourceModel_version = QtGui.QStandardItemModel(0,2)
		QSourceModel_version.setHeaderData(rigBuilderUI.VERSION, QtCore.Qt.Horizontal, "Version")
		QSourceModel_version.setHeaderData(rigBuilderUI.FILENAME, QtCore.Qt.Horizontal, "File Name")
		QTreeView_version = fileTreeView()
		QTreeView_version.setRootIsDecorated(False)
		QTreeView_version.setAlternatingRowColors(True)
		QTreeView_version.setModel(QSourceModel_version)
		QTreeView_version.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		QLayout.addWidget(QTreeView_version)

		#load save button
		QHBoxLayout = QtGui.QHBoxLayout()
		QLayout.addLayout(QHBoxLayout)
		lPushButtons = []
		for sName in ['Open', 'Import', 'Reference', 'Save']:
			QPushButton = QtGui.QPushButton(sName)
			QHBoxLayout.addWidget(QPushButton)
			lPushButtons.append(QPushButton)

	def rigBuildInfoUI(self, QLayout):
		QGroupBox = QtGui.QGroupBox('Rig Build')
		QLayout.addWidget(QGroupBox)
		QVBoxLayout = QtGui.QVBoxLayout()
		QGroupBox.setLayout(QVBoxLayout)
		self.oRigBuildWidget = rigBuildInfoWidget()
		QVBoxLayout.addWidget(self.oRigBuildWidget)
		self.QBuidlScriptLayout = QVBoxLayout
		
	def progressBarUI(self, QLayout):
		QGroupBox = QtGui.QGroupBox('Rig Progress')
		QLayout.addWidget(QGroupBox)
		QVBoxLayout = QtGui.QVBoxLayout()
		QGroupBox.setLayout(QVBoxLayout)
		QProgressBar = QtGui.QProgressBar()
		QVBoxLayout.addWidget(QProgressBar)

	def rigDataInfoUI(self, QLayout):
		QGroupBox = QtGui.QGroupBox('Rig Data')
		QLayout.addWidget(QGroupBox)
		QVBoxLayout = QtGui.QVBoxLayout()
		QGroupBox.setLayout(QVBoxLayout)
		oRigDataWidget = rigDataInfoWidget()
		QVBoxLayout.addWidget(oRigDataWidget)

	def __loadBuildScriptCmd(self):
		QTreeWidget_buildScript = self.oRigBuildWidget.QTreeWidget
		dFunctions = loadBuildScript(QTreeWidget_buildScript)
		self.oRigBuildWidget.QTreeWidget.dFunctions = dFunctions
		

		





class scrollableWidget(QtGui.QWidget):
	"""docstring for scrollableWidget"""
	def __init__(self):
		super(scrollableWidget, self).__init__()

		QWidget = QtGui.QWidget()
		QWidgetScroll = QtGui.QWidget()
		QVBoxLayout = QtGui.QVBoxLayout(QWidget)
		QVBoxLayout.setAlignment(QtCore.Qt.AlignTop)

		QWidgetScroll.setLayout(QVBoxLayout)

		QScroll = QtGui.QScrollArea()
		QScroll.setWidgetResizable(True)
		QScroll.setFocusPolicy(QtCore.Qt.NoFocus)
		QScroll.setWidget(QWidgetScroll)

		QVBoxLayoutScroll = QtGui.QVBoxLayout(QWidget)
		QVBoxLayoutScroll.addWidget(QScroll)
		QWidget.setLayout(QVBoxLayoutScroll)

		self.QWidget = QWidget
		self.QVBoxLayout = QVBoxLayout

class collapseWidget(QtGui.QGroupBox):
	"""docstring for collapseWidget"""
	def __init__(self, sTitle = ''):
		super(collapseWidget, self).__init__(sTitle)

		QVBoxLayout = QtGui.QVBoxLayout(self)
		QVBoxLayout.setContentsMargins(0,7,0,0)
		QVBoxLayout.setSpacing(0)
		self.bCollapse = True
		self.sTitle = sTitle
		self.setMinimumHeight(20)
		self.setMaximumHeight(20)

		self.QFrame = QtGui.QFrame()
		self.QFrame.setFrameShape(QtGui.QFrame.Panel)
		self.QFrame.setFrameShadow(QtGui.QFrame.Plain)
		self.QFrame.setLineWidth(0)
		self.QFrame.setVisible(False)
		QVBoxLayout.addWidget(self.QFrame)

		self.QVBoxLayout_frame = QtGui.QVBoxLayout()
		self.QFrame.setLayout(self.QVBoxLayout_frame)

	def expandCollapseRect(self):
		return QtCore.QRect(0, 0, self.width(), 20)

	def mouseReleaseEvent(self, event):
		if self.expandCollapseRect().contains(event.pos()):
			self.toggleCollapsed()
			event.accept()
		else:
			event.ignore()

	 
	def toggleCollapsed(self):
		self.setCollapsed(not self.bCollapse)
		 
	def setCollapsed(self, bState=True):
		self.bCollapse = bState
		print self.bCollapse
 
		if bState:
			self.setMinimumHeight(20)
			self.setMaximumHeight(20)
			self.QFrame.setVisible(False)
		else:
			self.setMinimumHeight(0)
			self.setMaximumHeight(1000000)
			self.QFrame.setVisible(True)

	def paintEvent(self, event):
		painter = QtGui.QPainter()
		painter.begin(self)
		 
		font = painter.font()
		font.setBold(True)
		painter.setFont(font)
 
		x = self.rect().x()
		y = self.rect().y()
		w = self.rect().width()
		offset = 25
		 
		painter.setRenderHint(painter.Antialiasing)
		painter.fillRect(self.expandCollapseRect(), QtGui.QColor(93, 93, 93))
		painter.drawText(
			x + offset, y + 3, w, 16,
			QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop,
			self.sTitle
			)
		self._drawTriangle(painter, x, y)#(1)
		painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
		painter.end()

	def _drawTriangle(self, painter, x, y):#(2)        
		if not self.bCollapse:#(3)
			points = [  QtCore.QPoint(x+10,  y+6 ),
						QtCore.QPoint(x+20, y+6 ),
						QtCore.QPoint(x+15, y+11)
						]
			 
		else:
			points = [  QtCore.QPoint(x+10, y+4 ),
						QtCore.QPoint(x+15, y+9 ),
						QtCore.QPoint(x+10, y+14)
						]
			 
		currentBrush = painter.brush()#(4)
		currentPen   = painter.pen()
		 
		painter.setBrush(
			QtGui.QBrush(
				QtGui.QColor(187, 187, 187),
				QtCore.Qt.SolidPattern
				)
			)#(5)
		painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))#(6)
		painter.drawPolygon(QtGui.QPolygon(points))#(7)
		painter.setBrush(currentBrush)#(8)
		painter.setPen(currentPen)

class fileTreeView(QtGui.QTreeView):
	def __init__(self, parent=None):
		super(fileTreeView, self).__init__(parent)

	def keyPressEvent(self, event):
		if (event.key() == QtCore.Qt.Key_Escape and
			event.modifiers() == QtCore.Qt.NoModifier):
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		else:
			QtGui.QTreeView.keyPressEvent(self, event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		QtGui.QTreeView.mousePressEvent(self, event)

	def mouseDoubleClickEvent(self, event):
		pass

class buildInfoTreeView(QtGui.QTreeWidget):
	def __init__(self, parent=None):
		super(buildInfoTreeView, self).__init__(parent)

		self.dFunctions = {}

	def keyPressEvent(self, event):
		if (event.key() == QtCore.Qt.Key_Escape and
			event.modifiers() == QtCore.Qt.NoModifier):
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		else:
			QtGui.QTreeView.keyPressEvent(self, event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		QtGui.QTreeView.mousePressEvent(self, event)

	def mouseDoubleClickEvent(self, event):
		sFunction = self.currentItem().text(0)
		mFunction = self.dFunctions[sFunction]
		mFunction()

class rigBuildInfoWidget(QtGui.QWidget):
	#FUNCTION, STATUS = range(2)
	def __init__(self):
		super(rigBuildInfoWidget, self).__init__()

		QHeader = QtGui.QTreeWidgetItem(['Function', 'Status'])
		self.QTreeWidget = buildInfoTreeView()
		self.QTreeWidget.setHeaderItem(QHeader)
		self.QTreeWidget.setRootIsDecorated(False)
		self.QTreeWidget.setAlternatingRowColors(True)
		self.QTreeWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.QTreeWidget.setHeaderHidden(True)
		self.QTreeWidget.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
		self.QTreeWidget.header().setStretchLastSection(False)
		self.QTreeWidget.setColumnWidth(1,30)
		QLayout = QtGui.QVBoxLayout()
		QLayout.addWidget(self.QTreeWidget)
		self.setLayout(QLayout)

		self.QTreeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.QTreeWidget.customContextMenuRequested.connect(self.listItemRightClicked)

	def listItemRightClicked(self, QPos):
		QListMenu= QtGui.QMenu(self.QTreeWidget)
		QMenuItem_execute = QListMenu.addAction('Execute Select Function')
		QMenuItem_refresh = QListMenu.addAction('Refresh Build Script')
		QMenuItem_reBuild = QListMenu.addAction('Rerun Build Script')

		parentPosition = self.QTreeWidget.mapToGlobal(QtCore.QPoint(0, 0))        
		QListMenu.move(parentPosition + QPos)

		QListMenu.show()

class rigDataTreeView(QtGui.QTreeView):
	def __init__(self, parent=None):
		super(rigDataTreeView, self).__init__(parent)

	def keyPressEvent(self, event):
		if (event.key() == QtCore.Qt.Key_Escape and
			event.modifiers() == QtCore.Qt.NoModifier):
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		else:
			QtGui.QTreeView.keyPressEvent(self, event)

	def mousePressEvent(self, event):
		if not self.indexAt(event.pos()).isValid():
			self.clearSelection()
			self.clearFocus()
			self.setCurrentIndex(QtCore.QModelIndex())
		QtGui.QTreeView.mousePressEvent(self, event)

class rigDataInfoWidget(QtGui.QWidget):
	KEY, VALUE = range(2)
 	"""docstring for rigDataInfoWidget"""
 	def __init__(self):
 		super(rigDataInfoWidget, self).__init__()

 		QSourceModel = QtGui.QStandardItemModel(0,2)
		QSourceModel.setHeaderData(rigDataInfoWidget.KEY, QtCore.Qt.Horizontal, 'Key')
		QSourceModel.setHeaderData(rigDataInfoWidget.VALUE, QtCore.Qt.Horizontal, 'Value')

		self.QTreeView = rigDataTreeView()
		self.QTreeView.setRootIsDecorated(False)
		self.QTreeView.setAlternatingRowColors(True)
		self.QTreeView.setModel(QSourceModel)
		self.QTreeView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.QTreeView.setHeaderHidden(True)

		QLayout = QtGui.QVBoxLayout()
		QLayout.addWidget(self.QTreeView)
		self.setLayout(QLayout)

		self.QTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.QTreeView.customContextMenuRequested.connect(self.listItemRightClicked)

	def listItemRightClicked(self, QPos):
		QListMenu= QtGui.QMenu(self.QTreeView)
		QMenuItem_add = QListMenu.addAction('Add Component')
		QMenuItem_remove = QListMenu.addAction('Remove Component')
		QMenuItem_check = QListMenu.addAction('Check Components')
		QMenuItem_refresh = QListMenu.addAction('Refresh Rig Data')

		parentPosition = self.QTreeView.mapToGlobal(QtCore.QPoint(0, 0))        
		QListMenu.move(parentPosition + QPos)

		QListMenu.show()
 		
 		 
### sub functions
def loadBuildScript(QTreeWidget):
	## load build script
	import rigBuild.baseHierarchy as baseHierarchy
	reload(baseHierarchy)
	oBuildScript = baseHierarchy.baseHierarchy()
	oBuildScript.importFunctions()

	dFunctions = oBuildScript.dFunctions

	## ------------- test functions
	print dFunctions

	oBuildScript.sAsset = 'chrTest'
	## ------------- test functions end ------------
	
	dFunctionsWidget = {}

	QAsset = QtGui.QTreeWidgetItem(QTreeWidget)
	QAsset.setText(0, oBuildScript.sAsset)

	for sSection in ['Pre Build', 'Build', 'Post Build']:
		QSection = QtGui.QTreeWidgetItem(QAsset)
		QSection.setText(0, sSection)
		QSection.setFlags(QSection.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
		QSection.setCheckState(0, QtCore.Qt.Checked)

	for dFunctionEach in dFunctions['lFunctions']:
		sFunctionName = dFunctionEach.keys()[0]
		sParent = dFunctionEach[sFunctionName]['sParent']
		sAfter = dFunctionEach[sFunctionName]['sAfter']
		lColor = dFunctionEach[sFunctionName]['lColor']
		
		## find parent
		QParents = QTreeWidget.findItems(sParent, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)
		if QParents:
			QItem = QtGui.QTreeWidgetItem()
			QItem.setText(0, sFunctionName)
			QItem.setFlags(QItem.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
			QItem.setCheckState(0, QtCore.Qt.Checked)

			dFunctionsWidget.update({sFunctionName: dFunctionEach[sFunctionName]['mFunction']})

			#QItem.setText(1, 'T')
			#QItem.setForeground(1, QtGui.QBrush(QtGui.QColor('green')))
			#QItem.setTextAlignment(1, QtCore.Qt.AlignCenter)
			if lColor:
				QItem.setForeground(0, QtGui.QBrush(QtGui.QColor.fromRgb(lColor[0], lColor[1], lColor[2])))			
			if isinstance(sAfter, basestring):
				QAfter = QTreeWidget.findItems(sAfter, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)
				if QAfter and (QAfter[0].parent().text(0) == QParents[0].text(0)):
					iIndex = QParents[0].indexOfChild(QAfter[0])
					QParents[0].insertChild(iIndex + 1, QItem)
				else:
					QParents[0].addChild(QItem)
			elif isinstance(sAfter, int):
				QParents[0].insertChild(sAfter, QItem)
			elif not sAfter:
				QParents[0].addChild(QItem)

	QTreeWidget.expandAll()

	return dFunctionsWidget




