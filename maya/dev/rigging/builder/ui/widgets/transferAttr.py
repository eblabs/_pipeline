# IMPORT PACKAGES

# import os
import os

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


# CLASS
class TransferAttr(QWidget):
    """
    widget to transfer task's attributes from one to others
    """
    SIGNAL_ATTR_TRANSFER = Signal(list)

    def __init__(self, parent=None):
        super(TransferAttr, self).__init__(parent)

        self.task_orig = ''
        self.task_target = []
        self.task_attrs = []

        self.setWindowTitle('Transfer Task Attributes')
        self.setGeometry(100, 100, 250, 300)

        layout_base = QVBoxLayout()
        self.setLayout(layout_base)

        # label
        self.label = QLabel('')

        # list view
        self.attr_list_widget = TaskAttrList()

        # button
        self.button = QPushButton('Transfer')
        self.button.setFixedWidth(80)

        layout_base.addWidget(self.label)
        layout_base.addWidget(self.attr_list_widget)
        layout_base.addWidget(self.button)
        layout_base.setAlignment(self.button, Qt.AlignRight)

        self.button.clicked.connect(self.transfer_attrs)

    def show(self):
        target_str = ''
        for task in self.task_target:
            target_str += '{}, '.format(task)
        target_str = target_str[:-2]
        # reset label
        self.label.setText('{}\n   to\n{}'.format(self.task_orig, target_str))
        # reset attr list
        self.attr_list_widget.attr_list = self.task_attrs
        super(TransferAttr, self).show()

    def transfer_attrs(self):
        # get selections
        attr_list = self.attr_list_widget.get_selection()
        self.SIGNAL_ATTR_TRANSFER.emit(attr_list)
        self.close()


class TaskAttrList(QListView):
    """
    widget to list task's attributes
    """

    def __init__(self, parent=None):
        super(TaskAttrList, self).__init__(parent)
        self._attr_list = []
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    @ property
    def attr_list(self):
        return self._attr_list

    @ attr_list.setter
    def attr_list(self, val):
        self._attr_list = val
        self.model.clear()
        for attr in self._attr_list:
            item = QStandardItem(attr)
            self.model.appendRow(item)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and event.modifiers() == Qt.NoModifier:
            self.clearSelection()
            self.clearFocus()
            self.setCurrentIndex(QModelIndex())
        else:
            super(TaskAttrList, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        if not self.indexAt(event.pos()).isValid():
            self._clear_selection()
        super(TaskAttrList, self).mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        pass

    def focusInEvent(self, event):
        super(TaskAttrList, self).focusInEvent(event)
        self.setCurrentIndex(QModelIndex())  # remove focus

    def get_selection(self):
        indexes = self.selectedIndexes()
        if indexes:
            attr_list = []
            for index in indexes:
                item = self.model.itemFromIndex(index)
                attr = item.text()
                attr_list.append(attr)
        else:
            attr_list = self._attr_list
        return attr_list

    def _clear_selection(self):
        self.clearSelection()
        self.clearFocus()
        self.setCurrentIndex(QModelIndex())


