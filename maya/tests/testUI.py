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


class Window(QWidget):
    #changeStyleTriggered = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        self.createTree()
        self.connectSlots()

    def createTree(self):
        data = ['A', 'B', 'C', 'D', 'E', 'F']
        model = MyTreeView(data)
        self.treeView = QTreeView()
        self.treeView.setModel(model)
        layout = QVBoxLayout()
        layout.addWidget(self.treeView)
        self.changeIconPushButton = QPushButton("Change a single icon")
        layout.addWidget(self.changeIconPushButton)
        self.setLayout(layout)

    def fireChangeStyleSignal(self):
        #self.changeStyleTriggered.emit()
        pass

    @pyqtSlot()
    def changeStyleSignal(self):
        print(">>changeStyleSignal()")
        self.setStyleSheet("QTreeView::indicator:unchecked {image: url(:/icons/image.png);}")

    def connectSlots(self):
        #self.changeStyleTriggered.connect(self.changeStyleSignal)
        self.changeIconPushButton.clicked.connect(self.fireChangeStyleSignal)

class TestItem():
    def __init__(self, name, checked):
        self.checked = checked
        self.name = name

class MyTreeView(QAbstractListModel):
    def __init__(self, args, parent=None):
        super(StbTreeView, self).__init__(parent)

        self.args = []
        for item_name in args:
            self.args.append(TestItem(item_name, False))

        for item in self.args:
            print (item.name)

    def rowCount(self, parent):
        return len(self.args)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return "Nodes"

    def flags(self, index):
        return  Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            print (self.args[row].name)
            return self.args[row].name

        if role == Qt.CheckStateRole:
            row = index.row()
            print (self.args[row].checked)
            if self.args[row].checked == False:
                return Qt.Unchecked
            else:
                return Qt.Checked

    def setData(self, index, value, role):
        if role == Qt.CheckStateRole:
            row = index.row()
            self.args[row].checked = not self.args[row].checked             
        return True


window = Window()
window.show()