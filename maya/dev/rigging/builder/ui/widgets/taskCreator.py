# IMPORT PACKAGES

# import system packages
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

# import utils
import utils.common.logUtils as logUtils
import utils.common.files as files
import utils.common.modules as modules
import utils.common.naming as naming

# CONSTANT
logger = logUtils.logger


# CLASS
class TaskCreator(QWidget):
    """widget to create task"""
    def __init__(self):
        super(TaskCreator, self).__init__()

        layout_base = QVBoxLayout()
        layout_base.setContentsMargins(0, 0, 0, 0)  # remove space between widgets and layout
        self.setLayout(layout_base)

        # filter
        self.filter = QLineEdit()
        self.filter.setPlaceholderText('Task Filter...')

        layout_base.addWidget(self.filter)

        # task list
        self.sourceModel = QStandardItemModel()
        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setSourceModel(self.sourceModel)

        self.listView = TaskListView()
        self.listView.setModel(self.proxyModel)

        layout_base.addWidget(self.listView)

        self.filter.textChanged.connect(self.filter_reg_exp_changed)

        self.setFocus()  # remove focus when open

    def rebuild_list_model(self, task_folders):
        self.sourceModel.clear()

        tasks = get_tasks_from_folders(task_folders)

        for tsk in tasks:
            tsk_item = QStandardItem(tsk)
            self.sourceModel.appendRow(tsk_item)

    def filter_reg_exp_changed(self):
        reg_exp = QRegExp(self.filter.text(), Qt.CaseInsensitive)
        self.proxyModel.setFilterRegExp(reg_exp)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down and self.filter.hasFocus():
            # move to the first task show in list
            index = self.proxyModel.index(0, 0)
            self.listView.setFocus()
            self.listView.setCurrentIndex(index)


class TaskListView(QListView):
    """
    Task List View

    sub class from QListView, remove some mouse function

    """
    def __init__(self, parent=None):
        super(TaskListView, self).__init__(parent)
        self.setFocusPolicy(Qt.NoFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and event.modifiers() == Qt.NoModifier:
            self.clearSelection()
            self.clearFocus()
            self.setCurrentIndex(QModelIndex())
        else:
            super(TaskListView, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        if not self.indexAt(event.pos()).isValid():
            self._clear_selection()
        super(TaskListView, self).mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        pass

    def focusInEvent(self, event):
        super(TaskListView, self).focusInEvent(event)
        self.setCurrentIndex(QModelIndex())  # remove focus

    def _clear_selection(self):
        self.clearSelection()
        self.clearFocus()
        self.setCurrentIndex(QModelIndex())


class TaskCreate(QDialog):
    """widget to create task"""

    def __init__(self, parent=None, title='', button='', set_name=True):
        super(TaskCreate, self).__init__(parent)

        self.setWindowTitle(title)
        self.setGeometry(100, 100, 250, 300)

        layout_base = QVBoxLayout()
        self.setLayout(layout_base)

        if set_name:
            # add task name and display name widget if set name, (different between task creation / task switch)

            # ask user to set side and description, so we can force the user follow the naming convention
            # this will make us easier to mirror the component
            # task side
            layout_side = QHBoxLayout()
            label = QLabel('Side:')
            label.setMaximumWidth(30)
            self.task_side = QComboBox()
            self.task_side.addItems(naming.Side.Key.all)
            self.index_side_default = self.task_side.findText(naming.Side.Key.m, Qt.MatchFixedString)
            self.task_side.setCurrentIndex(self.index_side_default)

            layout_side.addWidget(label)
            layout_side.addWidget(self.task_side)

            layout_base.addLayout(layout_side)

            # task description
            self.task_des = QLineEdit()
            self.task_des.setPlaceholderText('Task Description...')

            layout_base.addWidget(self.task_des)

            # task display name
            self.task_display = QLineEdit()
            self.task_display.setPlaceholderText('Display Name (Optional)...')

            layout_base.addWidget(self.task_display)

        # get task creator widget
        self.widget_task_creation = TaskCreator()
        layout_base.addWidget(self.widget_task_creation)

        # create button
        self.button = QPushButton(button)
        self.button.setFixedWidth(80)
        self.button.setEnabled(False)
        layout_base.addWidget(self.button)

        layout_base.setAlignment(self.button, Qt.AlignRight)

        # connect set button
        if set_name:
            self.task_des.textChanged.connect(self.set_button_with_name_check)
            self.widget_task_creation.listView.selectionModel().currentChanged.connect(self.set_button_with_name_check)
        else:
            self.widget_task_creation.listView.selectionModel().currentChanged.connect(self.set_button)

    def edit_folders_open(self):
        self.edit_folders_window.close()
        self.edit_folders_window.show()

    def set_button_with_name_check(self):
        des = self.task_des.text()
        task = self.widget_task_creation.listView.currentIndex().data()

        if des and task:
            self.button.setEnabled(True)
        else:
            self.button.setEnabled(False)

    def set_button(self):
        task = self.widget_task_creation.listView.currentIndex().data()
        if task:
            self.button.setEnabled(True)
        else:
            self.button.setEnabled(False)


# Function
def get_tasks_from_folders(task_folders):
    """
    get all task paths from folders

    Args:
        task_folders(list): task folder paths
                            need to be in python way, like 'dev.rigging.task.core'

    Returns:
        task_paths(list)
    """
    task_paths = []
    for folder_path in task_folders:
        # get absolute path by import module
        folder_mod, func = modules.import_module(folder_path)
        if folder_mod:
            folder_path_abs = os.path.dirname(folder_mod.__file__)

            # get task files
            task_names = files.get_files_from_path(folder_path_abs, extension='.py', exceptions='__init__',
                                                   full_paths=False)

            for tsk_n in task_names:
                task = '{}.{}'.format(folder_path, tsk_n[:-3])  # remove extension .py
                task_paths.append(task)

    task_paths.sort()

    return task_paths
