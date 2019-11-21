from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import __version__
from shiboken2 import wrapInstance


class AttrView(QTreeView):
    def __init__(self):
        super(AttrView, self).__init__()

        self._model = QStandardItemModel(0, 2)
        self.setModel(self._model)

        col_item = QStandardItem('space')
        col_item.setEditable(False)
        val_item = QStandardItem('dict')
        val_item.setEditable(False)

        self._model.appendRow([col_item, val_item])

        # control
        col_item_ctrl = QStandardItem('controls[0]')
        col_item_ctrl.setCheckable(True)
        val_item_ctrl = QStandardItem('dict')
        val_item_ctrl.setEditable(False)

        col_item.appendRow([col_item_ctrl, val_item_ctrl])

        # space type
        col_item_space = QStandardItem('point')
        col_item_space.setCheckable(True)
        col_item_space.setEditable(False)
        val_item_space = QStandardItem('list')
        val_item_space.setEditable(False)

        col_item_ctrl.appendRow([col_item_space, val_item_space])

        # space obj
        col_item_space_obj = QStandardItem('fk')
        col_item_space_obj.setCheckable(True)
        val_item_space_obj = QStandardItem('ctrl_01')

        col_item_space.appendRow([col_item_space_obj, val_item_space_obj])


attr_view = AttrView()
attr_view.show()