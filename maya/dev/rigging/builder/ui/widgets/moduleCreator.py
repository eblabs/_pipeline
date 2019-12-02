# IMPORT PACKAGES

# import os
import os

# import inspect
import inspect

# import ast
import ast

# import json
import json

# import OrderedDict
from collections import OrderedDict

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
import utils.common.assets as assets
import utils.common.naming as naming
import utils.common.modules as modules

# import module
import dev.rigging.task.component.core.module as module_tsk

# import taskCreator
import taskCreator

# icons
import icons

# config
import config

# CONSTANT
logger = logUtils.logger

# task folders
TASK_FOLDERS_CONFIG = os.path.join(os.path.dirname(config.__file__), 'TASK_FOLDERS.cfg')
TASK_FOLDERS = files.read_json_file(TASK_FOLDERS_CONFIG)

# User Role
ROLE_TASK_KWARGS_INFO = Qt.UserRole + 1
ROLE_TASK_KWARGS_KEYS = Qt.UserRole + 2
ROLE_TASK_NAME = Qt.UserRole + 3


# CLASS
class ModuleCreator(QWidget):
    """
    create/edit module
    """
    def __init__(self):
        super(ModuleCreator, self).__init__()

        self.project = None
        self.module_name = None

        self.setWindowTitle('Create/Edit Module')
        self.setGeometry(100, 100, 250, 300)
        self.setMinimumSize(800, 600)

        layout_base = QGridLayout()
        self.setLayout(layout_base)

        # splitter
        splitter_base = QSplitter()
        layout_base.addWidget(splitter_base)

        # frame top
        frame_top = QFrame()
        # add layout to top frame
        layout_top = QVBoxLayout(frame_top)

        # button shelf
        # button shelf has create/load/save/delete
        self.button_shelf = ButtonShelf()
        layout_top.addWidget(self.button_shelf)

        # module info
        self.module_info = ModuleInfo()
        layout_top.addWidget(self.module_info)

        # module attr
        # module attr contains all the attribute we want to promote to ui, and connect with sub tasks
        self.module_attrs = ModuleAttrs()
        group_module_attrs = attach_group_box(self.module_attrs, 'Module Attrs')
        # add to widget
        layout_top.addWidget(group_module_attrs)

        # sub tasks
        # show all sub tasks in the module,
        # it contains two list, left show task name and task path, user can edit them, add right click to add/remove
        # right show select task's attributes and default values, user can edit the values and promote to module as
        # module attr, also it can be added to module attr to make connection
        self.sub_task_info = SubTaskInfo()

        # attach to splitter
        splitter_base.addWidget(frame_top)
        splitter_base.addWidget(self.sub_task_info)

        # splitter settings
        splitter_base.setOrientation(Qt.Vertical)
        splitter_base.setCollapsible(0, False)
        splitter_base.setCollapsible(1, False)
        splitter_base.setStretchFactor(0, 1)
        splitter_base.setStretchFactor(1, 1)

        # sub windows
        self.window_create_module = CreateModule(parent=self)
        self.window_load_module = LoadModule(parent=self)

        # connect signal
        # button connection
        self.button_shelf.button_create.clicked.connect(self.open_create_module_window)
        self.button_shelf.button_load.clicked.connect(self.open_load_module_window)
        self.button_shelf.button_save.clicked.connect(self.save_module_info)
        # set module info
        self.window_create_module.SIGNAL_MODULE_INFO.connect(self.set_module_info)
        self.window_load_module.SIGNAL_MODULE_INFO.connect(self.set_module_info)
        # promote sub task attr to module
        self.sub_task_info.sub_task_attrs.SIGNAL_ATTR_PROMOTE.connect(self.module_attrs.add_attr)
        # connect attr/disconnect attr
        self.sub_task_info.sub_task_attrs.SIGNAL_ATTR_CONNECT.connect(self.module_attrs.connect_attr)
        self.module_attrs.SIGNAL_ATTR_CONNECT.connect(self.sub_task_info.sub_task_attrs.connect_attr)
        self.sub_task_info.sub_task_attrs.SINGAL_ATTR_DISCONNECT.connect(self.module_attrs.disconnect_attr)
        self.module_attrs.SIGNAL_ATTR_DISCONNECT.connect(self.sub_task_info.sub_task_attrs.disconnect_attr)
        self.module_attrs.SIGNAL_ATTR_CONNECT_TASK.connect(self.sub_task_info.sub_task_attrs.connect_attr_with_module)
        self.module_attrs.SIGNAL_ATTR_DISCONNECT_TASK.connect(self.sub_task_info.sub_task_attrs.disconnect_attr_with_module)

    def open_create_module_window(self):
        """
        open create module window to set module info
        """
        self.window_create_module.reset_info()
        self.window_create_module.close()
        self.window_create_module.move(QCursor.pos())
        self.window_create_module.show()

    def open_load_module_window(self):
        """
        open load module window to set module info
        """
        self.window_load_module.reset_info()
        self.window_load_module.close()
        self.window_load_module.move(QCursor.pos())
        self.window_load_module.show()

    def set_module_info(self, project, module_name, module_info):
        """
        set module info to ui
        """
        self.module_info.label_project.setText(project)
        self.module_info.label_name.setText(module_name)

        self.sub_task_info.sub_tasks.project = project

        self.project = project
        self.module_name = module_name

    def save_module_info(self):
        if self.project and self.module_name:
            save = True
            # try to get module info
            module_info = module_tsk.get_module_info(self.project, self.module_name)
            if module_info:
                # ask user if want to override
                title = "Module Already Exists"
                text = ("Module {} already exists in project {}\n"
                        "Are you sure you want to override existing module?".format(self.module_name, self.project))
                reply = QMessageBox.warning(self, title, text, QMessageBox.Yes | QMessageBox.Cancel,
                                            defaultButton=QMessageBox.Cancel)
                if reply != QMessageBox.Yes:
                    save = False

            if save:
                # save module info
                # get module attr info
                module_attrs_info = self.module_attrs.get_attrs_info()
                # get sub tasks info
                sub_tasks_info = self.sub_task_info.sub_tasks.get_sub_tasks_info()
                # save module info
                module_tsk.export_module_info(self.project, self.module_name, module_attrs_info, sub_tasks_info)


class CreateModule(QDialog):
    """
    window to create new module
    """
    SIGNAL_MODULE_INFO = Signal(str, str, dict)

    def __init__(self, parent=None):
        super(CreateModule, self).__init__(parent)

        self.setWindowTitle('Create Module')
        self.setGeometry(100, 100, 250, 300)
        self.setFixedSize(200, 100)

        layout_base = QVBoxLayout()
        self.setLayout(layout_base)

        # project
        self.line_edit_project = ProjectFilter()
        # module name
        self.line_edit_module = QLineEdit()
        self.line_edit_module.setFrame(False)
        self.line_edit_module.setAlignment(Qt.AlignCenter)
        self.line_edit_module.setStyleSheet('border-radius: 4px')
        self.line_edit_module.setPlaceholderText('Module Name')

        # create button
        self.button = QPushButton('Create')
        self.button.setFixedWidth(80)
        self.button.setEnabled(False)

        # add widget to layout
        layout_base.addWidget(self.line_edit_project)
        layout_base.addWidget(self.line_edit_module)
        layout_base.addWidget(self.button)

        layout_base.setAlignment(self.button, Qt.AlignRight)

        # get all projects
        projects_list = assets.get_all_projects()
        self.line_edit_project.completer.setModel(QStringListModel(projects_list))

        # set button
        self.line_edit_project.textChanged.connect(self.set_button)
        self.line_edit_module.textChanged.connect(self.set_button)

        # connect button
        self.button.clicked.connect(self.set_module_info)

        # so it won't focus on QLineEdit when startup
        self.setFocus()

    def set_button(self):
        project = self.line_edit_project.text()
        module_name = self.line_edit_module.text()
        if project and module_name:
            # check if project exists
            if assets.get_project_path(project, warning=False):
                self.button.setEnabled(True)
            else:
                self.button.setEnabled(False)
        else:
            self.button.setEnabled(False)

    def reset_info(self):
        self.line_edit_project.setText('')
        self.line_edit_module.setText('')

    def set_module_info(self):
        project = self.line_edit_project.text()
        module_name = self.line_edit_module.text()
        # check if module exists or not, if exist, get module info
        module_info = module_tsk.get_module_info(project, module_name)
        if module_info:
            # exist, check if want to load module info instead
            title = "Module Already Exists"
            text = ("Module {} already exists in project {}\n" 
                    "Do you want to load existing module info instead?".format(module_name, project))
            reply = QMessageBox.warning(self, title, text, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                        defaultButton=QMessageBox.Cancel)
            if reply != QMessageBox.Cancel:
                # shoot signal
                if reply == QMessageBox.No:
                    module_info = {}
                self.SIGNAL_MODULE_INFO.emit(project, module_name, module_info)
                self.close()
        else:
            self.SIGNAL_MODULE_INFO.emit(project, module_name, {})
            self.close()


class LoadModule(QDialog):
    """
    window to load module
    """
    SIGNAL_MODULE_INFO = Signal(str, str, dict)

    def __init__(self, parent=None):
        super(LoadModule, self).__init__(parent)
        self.setWindowTitle('Load Module')
        self.setGeometry(100, 100, 250, 300)
        self.setFixedSize(300, 400)

        layout_base = QVBoxLayout()
        self.setLayout(layout_base)

        # project
        self.line_edit_project = ProjectFilter()
        # module filter
        self.module_list = ModuleListView()

        # create button
        self.button = QPushButton('Load')
        self.button.setFixedWidth(80)
        self.button.setEnabled(False)

        # add widget to layout
        layout_base.addWidget(self.line_edit_project)
        layout_base.addWidget(self.module_list)
        layout_base.addWidget(self.button)

        layout_base.setAlignment(self.button, Qt.AlignRight)

        # get all projects
        projects_list = assets.get_all_projects()
        self.line_edit_project.completer.setModel(QStringListModel(projects_list))

        # set button
        self.line_edit_project.textChanged.connect(self.rebuild_module_list)
        self.module_list.listView.selectionModel().currentChanged.connect(self.set_button)

        # so it won't focus on QLineEdit when startup
        self.setFocus()

    def set_button(self):
        module_name = self.module_list.listView.currentIndex().data()
        if module_name:
            self.button.setEnabled(True)
        else:
            self.button.setEnabled(False)

    def rebuild_module_list(self):
        project = self.line_edit_project.text()
        # get module folder path
        module_folder_path = assets.get_project_task_path(project, warning=False)
        self.module_list.rebuild_list_model(module_folder=module_folder_path)

    def reset_info(self):
        self.line_edit_project.setText('')
        self.module_list.filter.setText('')

    def set_module_info(self):
        project = self.line_edit_project.text()
        module_name = self.module_list.listView.currentIndex().data()
        module_info = module_tsk.get_module_info(project, module_name)
        self.SIGNAL_MODULE_INFO.emit(project, module_name, module_info)
        self.close()


class ProjectFilter(QLineEdit):
    """
    QLineEdit widget to get project name with a completer
    """
    def __init__(self):
        super(ProjectFilter, self).__init__()
        self.setFrame(False)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('border-radius: 4px')
        self.setPlaceholderText('Project')

        self.completer = QCompleter()
        self.setCompleter(self.completer)

        self.project_checker = False
        self.textChanged.connect(self.check_project)

    def check_project(self):
        project = self.text()
        self.project_checker = assets.get_project_path(project, warning=False)
        self.set_text_color(self, self.project_checker)

    @staticmethod
    def set_text_color(line_edit, checker):
        """
        set line edit text color, white if available, else is red

        Args:
            line_edit(QLineEdit): rig info widget
            checker(bool): True/False
        """
        palette = QPalette()
        if checker:
            palette.setColor(QPalette.Text, Qt.white)
        else:
            palette.setColor(QPalette.Text, Qt.red)
        line_edit.setPalette(palette)


class ModuleListView(taskCreator.TaskCreator):
    """
    list view to show all modules in folder
    """
    def __init__(self):
        super(ModuleListView, self).__init__()
        self.filter.setPlaceholderText('Module Filter...')

    def rebuild_list_model(self, module_folder=None, tasks=None):
        """
        override rebuild list model function to only list modules
        """
        self.sourceModel.clear()

        if module_folder:
            module_names = module_tsk.get_all_module_in_folder(module_folder)

            for name in module_names:
                item = QStandardItem(name)
                self.sourceModel.appendRow(item)


class ButtonShelf(QWidget):
    """
    button shelf widget for module
    """
    def __init__(self):
        super(ButtonShelf, self).__init__()

        self.setMaximumWidth(130)

        layout_base = QHBoxLayout()
        self.setLayout(layout_base)
        layout_base.setSpacing(4)
        layout_base.setContentsMargins(2, 2, 2, 2)  # remove space between button and layout

        self.button_create = Button(layout_base, icons.create_module, 'Create Module')
        self.button_load = Button(layout_base, icons.load_module, 'Load Module')
        self.button_save = Button(layout_base, icons.save_module, 'Save Current Module')
        self.button_delete = Button(layout_base, icons.delete_module, 'Delete Module')


class Button(QPushButton):
    """
    sub class for QPushButton, contains information and functions needed for buttons shelf
    """

    def __init__(self, layout, icon_button, tool_tip=''):
        super(Button, self).__init__()
        size = 30  # button size

        self._icon = icon_button
        self._tool_tip = tool_tip

        self.setIcon(QIcon(self._icon))  # set enabled icon by default
        self.setIconSize(QSize(size, size))  # set icon size

        # resize button so no gap for the icon
        self.setFixedHeight(size)
        self.setFixedWidth(size)

        # tool tip
        if self._tool_tip:
            self.setToolTip(self._tool_tip)

        layout.addWidget(self)


class ModuleInfoLabel(QLabel):
    """
    widget to display module name/docstring
    """
    def __init__(self):
        super(ModuleInfoLabel, self).__init__()

        # set stylesheet
        self.setStyleSheet("""border: 1.3px solid black; border-radius: 2px""")


class ModuleInfo(QWidget):
    """
    widget contains module info, project, module name, docstring etc..
    """
    def __init__(self):
        super(ModuleInfo, self).__init__()
        # base layout
        layout_base = QGridLayout(self)
        self.setLayout(layout_base)

        # module info
        frame_module_info = QFrame()
        layout_module_info = QVBoxLayout(frame_module_info)

        # project
        layout_project = QHBoxLayout()
        label = QLabel('Project:')
        label.setMaximumWidth(100)
        self.label_project = ModuleInfoLabel()
        layout_project.addWidget(label)
        layout_project.addWidget(self.label_project)

        # module name
        layout_name = QHBoxLayout()
        label = QLabel('Module Name:')
        label.setMaximumWidth(100)
        self.label_name = ModuleInfoLabel()
        layout_name.addWidget(label)
        layout_name.addWidget(self.label_name)

        # attach layout
        layout_module_info.addLayout(layout_project)
        layout_module_info.addLayout(layout_name)

        # put in a group box
        group_module_info = attach_group_box(frame_module_info, 'Module Info')
        layout_base.addWidget(group_module_info)
        layout_base.setContentsMargins(0, 0, 0, 0)


class ModuleAttrs(QTreeView):
    """
    widget to show module attributes

    row:
        attr's display name, attr's in class name, attr's default value, attr's hint, attr's destination connections
    """
    SIGNAL_ATTR_CONNECT = Signal(str)
    SIGNAL_ATTR_DISCONNECT = Signal()
    SIGNAL_ATTR_CONNECT_TASK = Signal()
    SIGNAL_ATTR_DISCONNECT_TASK = Signal()

    def __init__(self):
        super(ModuleAttrs, self).__init__()

        # different color each row
        self.setAlternatingRowColors(True)
        # show header so user can adjust the first column width
        self.setHeaderHidden(False)

        # QStandardItemModel
        self._model = QStandardItemModel(0, 5)
        self._model.setHeaderData(0, Qt.Horizontal, 'Display Name')
        self._model.setHeaderData(1, Qt.Horizontal, 'In Class Name')
        self._model.setHeaderData(2, Qt.Horizontal, 'Default Value')
        self._model.setHeaderData(3, Qt.Horizontal, 'Hint')
        self._model.setHeaderData(4, Qt.Horizontal, 'Connections')
        self.setModel(self._model)

        # right click menu
        self.menu = QMenu()
        self.action_remove = self.menu.addAction('Remove Attr')
        self.action_up = self.menu.addAction('Move Up')
        self.action_down = self.menu.addAction('Move Down')
        self.action_connect = self.menu.addAction('Connect')
        self.action_disconnect = self.menu.addAction('Disconnect')
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        # connect signal
        self.action_remove.triggered.connect(self.remove_attr)
        self.action_up.triggered.connect(self.move_up_attr)
        self.action_down.triggered.connect(self.move_down_attr)
        self.action_connect.triggered.connect(self.connect_attr_with_sub_task)
        self.action_disconnect.triggered.connect(self.disconnect_attr_with_sub_task)

    def add_attr(self, display_name, task_kwarg_info):
        """
        add module attribute to ui
        """
        attr_name = task_kwarg_info['attr_name']
        default_value = task_kwarg_info['default']
        hint = task_kwarg_info['hint']
        connect = task_kwarg_info.get('output', [])

        item_display = QStandardItem(display_name)
        item_attr = AttrItem(attr_name)
        value = convert_data_to_str(default_value)
        item_value = AttrItem(value)
        item_hint = AttrItem(hint)
        connect_str = convert_data_to_str(connect)
        item_connect = AttrItem(connect_str)

        item_connect.setEditable(False)

        item_display.setData(task_kwarg_info, role=ROLE_TASK_KWARGS_INFO)

        # connect signal
        item_attr.connector.SIGNAL_EMIT.connect(self.update_attr_name)
        item_value.connector.SIGNAL_EMIT.connect(self.update_value)
        item_hint.connector.SIGNAL_EMIT.connect(self.update_hint)
        item_connect.connector.SIGNAL_EMIT.connect(self.update_connection)

        self._model.appendRow([item_display, item_attr, item_value, item_hint, item_connect])

    def remove_attr(self):
        # need to remove connected attrs
        index = self.selectedIndexes()[0]
        self._model.removeRow(index.row())

    def move_up_attr(self):
        index = self.selectedIndexes()[0]
        row_move = index.row() - 1
        if row_move >= 0:
            row_items = self._model.takeRow(index.row())
            self._model.insertRow(row_move, row_items)
            row_index = self._model.index(row_move, index.column())
            self.setCurrentIndex(row_index)

    def move_down_attr(self):
        index = self.selectedIndexes()[0]
        row_count = self._model.rowCount()
        if index.row() < row_count - 1:
            row_move = index.row() + 1
            row_items = self._model.takeRow(index.row())
            self._model.insertRow(row_move, row_items)
            row_index = self._model.index(row_move, index.column())
            self.setCurrentIndex(row_index)

    def get_kwarg_info(self):
        if self.selectedIndexes():
            index_display = self.selectedIndexes()[0]
            item_display = self._model.itemFromIndex(index_display)
            # get kwarg info
            kwarg_info = item_display.data(role=ROLE_TASK_KWARGS_INFO)
            return kwarg_info, item_display
        else:
            return None, None

    def connect_attr_with_sub_task(self):
        self.SIGNAL_ATTR_CONNECT_TASK.emit()

    def disconnect_attr_with_sub_task(self):
        self.SIGNAL_ATTR_DISCONNECT_TASK.emit()

    def connect_attr(self, input_attr):
        kwarg_info, item_display = self.get_kwarg_info()

        if item_display:
            output_attrs = kwarg_info.get('output', [])

            if input_attr not in output_attrs:
                output_attrs.append(input_attr)
            # set to item connect, it will automatically update the kwarg info on item_display
            index_connect = self.selectedIndexes()[-1]
            item_connect = self._model.itemFromIndex(index_connect)
            output_attrs_str = convert_data_to_str(output_attrs)
            item_connect.setText(output_attrs_str)

            # get attr name
            attr_name = kwarg_info['attr_name']
            # shoot signal
            self.SIGNAL_ATTR_CONNECT.emit(attr_name)

    def disconnect_attr(self, input_attr):
        kwarg_info, item_display = self.get_kwarg_info()

        if item_display:
            output_attrs = kwarg_info.get('output', [])

            if input_attr in output_attrs:
                output_attrs.remove(input_attr)
            # set to item connect, it will automatically update the kwarg info on item_display
            index_connect = self.selectedIndexes()[-1]
            item_connect = self._model.itemFromIndex(index_connect)
            output_attrs_str = convert_data_to_str(output_attrs)
            item_connect.setText(output_attrs_str)

            # shoot signal
            self.SIGNAL_ATTR_DISCONNECT.emit()

    def update_attr_name(self, orig_text, update_text):
        kwarg_info, item_display = self.get_kwarg_info()
        kwarg_info['attr_name'] = update_text
        item_display.setData(kwarg_info, role=ROLE_TASK_KWARGS_INFO)
        # need to update connected attrs

    def update_value(self, orig_text, update_text):
        kwarg_info, item_display = self.get_kwarg_info()
        value = convert_data(update_text)
        kwarg_info['default'] = value
        item_display.setData(kwarg_info, role=ROLE_TASK_KWARGS_INFO)

    def update_hint(self, orig_text, update_text):
        kwarg_info, item_display = self.get_kwarg_info()
        kwarg_info['hint'] = update_text
        item_display.setData(kwarg_info, role=ROLE_TASK_KWARGS_INFO)

    def update_connection(self, orig_text, update_text):
        kwarg_info, item_display = self.get_kwarg_info()
        output_attrs = convert_data(update_text)
        kwarg_info.update({'output': output_attrs})
        item_display.setData(kwarg_info, role=ROLE_TASK_KWARGS_INFO)

    def get_attrs_info(self):
        """
        get module attrs information
        """
        attrs_info = OrderedDict()
        for row in self._model.rowCount():
            item = self._model.itemFromIndex(row, 0)
            display_name = item.text()
            kwarg_info = item.data(role=ROLE_TASK_KWARGS_INFO)
            attrs_info.update({display_name: kwarg_info})
        return attrs_info

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and event.modifiers() == Qt.NoModifier:
            self.clearSelection()
            self.clearFocus()
            self.setCurrentIndex(QModelIndex())
        else:
            super(ModuleAttrs, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        if not self.indexAt(event.pos()).isValid():
            self._clear_selection()
        super(ModuleAttrs, self).mousePressEvent(event)

    def _clear_selection(self):
        self.clearSelection()
        self.clearFocus()
        self.setCurrentIndex(QModelIndex())

    def _show_menu(self, pos):
        if self.selectedIndexes():
            pos = self.viewport().mapToGlobal(pos)
            self.menu.move(pos)
            self.menu.show()


class SubTasks(QTreeView):
    """
    widget to show module's sub task list, with right click menu to add/edit/remove tasks
    """
    SIGNAL_TASK_ATTRS = Signal(list, dict, QStandardItem)
    SIGNAL_TASK_ATTRS_CLEAR = Signal()

    def __init__(self):
        super(SubTasks, self).__init__()

        # different color each row
        self.setAlternatingRowColors(True)
        self.setHeaderHidden(False)

        self.project = None
        self.task_tree = None
        self.task_folders = TASK_FOLDERS[:]
        self.builder_tasks_info = {}

        # QStandardItemModel
        self._model = QStandardItemModel(0, 2)
        self._model.setHeaderData(0, Qt.Horizontal, 'Task Name')
        self._model.setHeaderData(1, Qt.Horizontal, 'Task Path')
        self.setModel(self._model)

        # right click menu
        self.menu = QMenu()
        self.action_add = self.menu.addAction('Add Task')
        self.action_builder_add = self.menu.addAction('Add Task From Builder')
        self.action_remove = self.menu.addAction('Remove Task')
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        # task list
        self.window_task_list = TaskList(parent=self)
        self.window_builder_task_list = BuilderTaskList(parent=self)

        # connect signal
        self.action_add.triggered.connect(self.open_task_list_window)
        self.action_builder_add.triggered.connect(self.open_builder_task_list_window)
        self.action_remove.triggered.connect(self.remove_sub_task)
        self.window_task_list.SIGNAL_TASK_ADD.connect(self.add_sub_task)
        self.window_builder_task_list.SIGNAL_TASK_ADD.connect(self.add_sub_task_from_builder)
        self.selectionModel().selectionChanged.connect(self.item_pressed)

    def _show_menu(self, pos):
        if self.project:
            self.action_add.setEnabled(True)

            if self.task_tree:
                self.action_builder_add.setEnabled(True)
            else:
                self.action_builder_add.setEnabled(False)

            index = self.currentIndex()
            item = self._model.itemFromIndex(index)
            if item:
                self.action_remove.setEnabled(True)
            else:
                self.action_remove.setEnabled(False)

            pos = self.viewport().mapToGlobal(pos)
            self.menu.move(pos)
            self.menu.show()

    def reset_model(self):
        self._model.clear()

    def open_task_list_window(self):
        # close window
        self.window_task_list.close()
        # get task folders
        task_folders = self.task_folders[:] + ['projects.{}.scripts.tasks'.format(self.project)]
        # reset
        self.window_task_list.refresh_widgets()
        self.window_task_list.widget_task_creation.rebuild_list_model(task_folders=task_folders)
        # show window
        self.window_task_list.move(QCursor.pos())
        self.window_task_list.show()

    def open_builder_task_list_window(self):
        # close window
        self.window_builder_task_list.close()
        # get tasks
        self.builder_tasks_info = self.task_tree.get_task_info_for_module()
        # reset
        self.window_builder_task_list.refresh_widgets()
        self.window_builder_task_list.widget_task_creation.rebuild_list_model(tasks=self.builder_tasks_info.keys())
        # show window
        self.window_builder_task_list.move(QCursor.pos())
        self.window_builder_task_list.show()

    def add_sub_task(self, task_name, task_path, task_kwargs=None):
        if not task_kwargs:
            # get task object
            task_import, task_function = modules.import_module(task_path)
            task_obj = getattr(task_import, task_function)
            if inspect.isfunction(task_obj):
                # function, normally is callback
                task_kwargs = task_import.kwargs_ui
            else:
                # task class
                task_obj = task_obj(name=task_name)
                task_kwargs = task_obj.kwargs_ui

        # add to task model list
        item_task_name = QStandardItem(task_name)
        item_task_path = QStandardItem(task_path)
        item_task_name.setData(task_kwargs, role=ROLE_TASK_KWARGS_INFO)
        item_task_name.setData(task_kwargs.keys(), role=ROLE_TASK_KWARGS_KEYS)
        item_task_path.setEditable(False)
        self._model.appendRow([item_task_name, item_task_path])

    def add_sub_task_from_builder(self, task_name):
        task_path = self.builder_tasks_info[task_name]['task_path']
        task_kwargs = self.builder_tasks_info[task_name]['task_kwargs']
        self.add_sub_task(task_name, task_path, task_kwargs=task_kwargs)

    def remove_sub_task(self):
        index = self.selectedIndexes()[0]
        self._model.removeRow(index.row())

    def get_sub_tasks_info(self):
        """
        get module sub tasks information
        """
        sub_tasks_info = {}
        for row in self._model.rowCount():
            item = self._model.itemFromIndex(row, 0)
            task_name = item.text()
            task_kwargs_info = item.data(role=ROLE_TASK_KWARGS_INFO)
            # reduce task kwargs
            task_kwargs_info_reduce = {}
            for key, info in task_kwargs_info.iteritems():
                value = info.get('value', None)
                if value is None:
                    value = info.get('default', None)
                task_kwargs_info_reduce.update({key: value})
            sub_tasks_info.update({task_name: {'task_path': task_kwargs_info['task_path'],
                                               'task_kwargs': task_kwargs_info_reduce}})
        return sub_tasks_info

    def item_pressed(self):
        # get current index
        indexes = self.selectedIndexes()
        # clear attr ui
        self.SIGNAL_TASK_ATTRS_CLEAR.emit()

        # get item
        if indexes:
            index = indexes[0]
            item = self._model.itemFromIndex(index)
            # get kwargs info, kwargs keys
            kwargs_info = item.data(role=ROLE_TASK_KWARGS_INFO)
            kwargs_keys = item.data(role=ROLE_TASK_KWARGS_KEYS)
            # shoot signal
            self.SIGNAL_TASK_ATTRS.emit(kwargs_keys, kwargs_info, item)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and event.modifiers() == Qt.NoModifier:
            self.clearSelection()
            self.clearFocus()
            self.setCurrentIndex(QModelIndex())
        else:
            super(SubTasks, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        if not self.indexAt(event.pos()).isValid():
            self._clear_selection()
        super(SubTasks, self).mousePressEvent(event)

    def _clear_selection(self):
        self.clearSelection()
        self.clearFocus()
        self.setCurrentIndex(QModelIndex())


class TaskList(taskCreator.TaskCreate):
    """widget to add task"""
    SIGNAL_TASK_ADD = Signal(str, str)

    def __init__(self, parent=None):
        super(TaskList, self).__init__(parent, title='Add Task', button='Add', set_name=True, display=False)

        self.button.clicked.connect(self._get_select_task)

    def refresh_widgets(self):
        self.task_name_widget.task_side.setCurrentIndex(self.task_name_widget.index_side_default)
        self.task_name_widget.task_des.setText('')
        self.widget_task_creation.filter.setText('')
        self.setFocus()

    def _get_select_task(self):
        side = self.task_name_widget.side
        description = self.task_name_widget.description
        name = naming.Namer(type=naming.Type.task, side=side, description=description).name
        task = self.widget_task_creation.listView.currentIndex().data()

        self.SIGNAL_TASK_ADD.emit(name, task)
        self.close()


class BuilderTaskList(taskCreator.TaskCreate):
    """widget to add task from builder"""
    SIGNAL_TASK_ADD = Signal(str)

    def __init__(self, parent=None):
        super(BuilderTaskList, self).__init__(parent, title='Add Task From Builder', button='Add', set_name=False)
        self.button.clicked.connect(self._get_select_task)

    def refresh_widgets(self):
        self.widget_task_creation.filter.setText('')
        self.setFocus()

    def _get_select_task(self):
        task = self.widget_task_creation.listView.currentIndex().data()

        self.SIGNAL_TASK_ADD.emit(task)
        self.close()


class SubTaskAttrs(QTreeView):
    """
    widget to show sub task's attributes

    row: attr's display name, attr's default value, attr's input connection
    """
    SIGNAL_ATTR_PROMOTE = Signal(str, dict)
    SIGNAL_ATTR_CONNECT = Signal(str)
    SINGAL_ATTR_DISCONNECT = Signal(str)

    def __init__(self):
        super(SubTaskAttrs, self).__init__()

        # different color each row
        self.setAlternatingRowColors(True)

        self.setHeaderHidden(False)

        # store sub task item to update kwargs info
        self.sub_task_item = None

        # QStandardItemModel
        self._model = QStandardItemModel(0, 4)
        self._model.setHeaderData(0, Qt.Horizontal, 'Display Name')
        self._model.setHeaderData(1, Qt.Horizontal, 'In-Class Name')
        self._model.setHeaderData(2, Qt.Horizontal, 'Default Value')
        self._model.setHeaderData(3, Qt.Horizontal, 'Input Connection')
        self.setModel(self._model)

        # right click menu
        self.menu = QMenu()
        self.action_promote = self.menu.addAction('Promote')
        self.action_connect = self.menu.addAction('Connect')
        self.action_disconnect = self.menu.addAction('Disconnect')
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        # connect signal
        self.action_promote.triggered.connect(self.promote_attr)
        self.action_connect.triggered.connect(self.connect_attr_with_module)
        self.action_disconnect.triggered.connect(self.disconnect_attr_with_module)

    def show_sub_task_attrs(self, task_kwargs_keys, task_kwargs, task_item):
        """
        show selected sub task's attributes
        """
        self.sub_task_item = task_item
        task_name = task_item.text()
        for kwarg_name in task_kwargs_keys:
            # kwarg_name is display name
            # get attr name, default value and input connection
            kwarg_attr_name = task_kwargs[kwarg_name]['attr_name']
            kwarg_value = task_kwargs[kwarg_name].get('value', None)
            if kwarg_value is None:
                kwarg_value = task_kwargs[kwarg_name]['default']
            # input connection is not part of the task kwargs, we add it back to sub task item when we set connections
            # between sub task attribute and module attribute, that means, the task_kwargs may not have this key,
            # so we need to use get here to avoid error
            input_connection = task_kwargs[kwarg_name].get('input_connection', '')

            item_display = QStandardItem(kwarg_name)
            item_attr = QStandardItem(kwarg_attr_name)
            value = convert_data_to_str(kwarg_value)
            item_value = AttrItem(value)
            item_input = AttrItem(input_connection)

            item_display.setEditable(False)
            item_attr.setEditable(False)
            item_input.setEditable(False)

            item_display.setData(task_kwargs[kwarg_name], role=ROLE_TASK_KWARGS_INFO)
            item_display.setData(task_name, role=ROLE_TASK_NAME)

            # connect signal
            item_value.connector.SIGNAL_EMIT.connect(self.value_update)
            item_input.connector.SIGNAL_EMIT.connect(self.connection_update)

            self._model.appendRow([item_display, item_attr, item_value, item_input])

    def get_task_attr(self):
        index_display = self.selectedIndexes()[0]
        index_attr_name = self.selectedIndexes()[1]
        item_display = self._model.itemFromIndex(index_display)
        item_attr = self._model.itemFromIndex(index_attr_name)

        # get task name
        task_name = item_display.data(role=ROLE_TASK_NAME)
        task_attr = item_attr.text()

        # compose as attribute
        attr = '{}.{}'.format(task_name, task_attr)

        return attr

    def connect_attr_with_module(self):
        attr = self.get_task_attr()
        self.SIGNAL_ATTR_CONNECT.emit(attr)

    def disconnect_attr_with_module(self):
        attr = self.get_task_attr()
        self.SINGAL_ATTR_DISCONNECT.emit(attr)

    def connect_attr(self, attr_name):
        if self.selectedIndexes():
            index = self.selectedIndexes()[-1]
            item = self._model.itemFromIndex(index)
            item.setText(attr_name)

    def disconnect_attr(self):
        if self.selectedIndexes():
            index = self.selectedIndexes()[-1]
            item = self._model.itemFromIndex(index)
            item.setText('')

    def value_update(self, orig_text, update_text):
        kwarg_info, item_display = self.get_kwarg_info()
        value = convert_data(update_text)
        kwarg_info.update({'default': value})

        self.update_sub_task_kwargs_info(kwarg_info, item_display)

    def connection_update(self, orig_text, update_text):
        kwarg_info, item_display = self.get_kwarg_info()
        kwarg_info.update({'input_connection': update_text})

        self.update_sub_task_kwargs_info(kwarg_info, item_display)

    def get_kwarg_info(self):
        index = self.selectedIndexes()[0]
        item = self._model.itemFromIndex(index)
        kwarg_info = item.data(role=ROLE_TASK_KWARGS_INFO)
        return kwarg_info, item

    def update_sub_task_kwargs_info(self, kwarg_info, item_display):
        item_display.setData(kwarg_info, role=ROLE_TASK_KWARGS_INFO)
        display_name = item_display.text()
        kwargs_info_task = self.sub_task_item.data(role=ROLE_TASK_KWARGS_INFO)
        kwargs_info_task.update({display_name: kwarg_info})
        self.sub_task_item.setData(kwargs_info_task, role=ROLE_TASK_KWARGS_INFO)

    def refresh_list(self):
        self._model.clear()
        self._model = QStandardItemModel(0, 4)
        self._model.setHeaderData(0, Qt.Horizontal, 'Display Name')
        self._model.setHeaderData(1, Qt.Horizontal, 'In-Class Name')
        self._model.setHeaderData(2, Qt.Horizontal, 'Default Value')
        self._model.setHeaderData(3, Qt.Horizontal, 'Input Connection')
        self.setModel(self._model)

    def _show_menu(self, pos):
        indexes = self.selectedIndexes()
        if indexes:
            pos = self.viewport().mapToGlobal(pos)
            self.menu.move(pos)
            self.menu.show()

    def promote_attr(self):
        index = self.selectedIndexes()[0]
        item = self._model.itemFromIndex(index)
        # get display name and kwarg info
        display_name = item.text()
        kwarg_info = item.data(role=ROLE_TASK_KWARGS_INFO)
        # shoot signal
        self.SIGNAL_ATTR_PROMOTE.emit(display_name, kwarg_info)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and event.modifiers() == Qt.NoModifier:
            self.clearSelection()
            self.clearFocus()
            self.setCurrentIndex(QModelIndex())
        else:
            super(SubTaskAttrs, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        if not self.indexAt(event.pos()).isValid():
            self._clear_selection()
        super(SubTaskAttrs, self).mousePressEvent(event)

    def _clear_selection(self):
        self.clearSelection()
        self.clearFocus()
        self.setCurrentIndex(QModelIndex())


class SubTaskInfo(QWidget):
    """
    widget to show sub tasks info
    """
    def __init__(self):
        super(SubTaskInfo, self).__init__()

        # base layout
        layout_base = QGridLayout(self)
        self.setLayout(layout_base)

        # splitter
        splitter_base = QSplitter()
        layout_base.addWidget(splitter_base)

        # sub tasks
        self.sub_tasks = SubTasks()
        group_sub_tasks = attach_group_box(self.sub_tasks, 'Sub Tasks')

        # sub task attributes
        self.sub_task_attrs = SubTaskAttrs()
        group_sub_task_attr = attach_group_box(self.sub_task_attrs, 'Sub Task Attrs')

        # attach to splitter
        splitter_base.addWidget(group_sub_tasks)
        splitter_base.addWidget(group_sub_task_attr)

        # stretch factor
        splitter_base.setCollapsible(0, False)
        splitter_base.setCollapsible(1, False)
        splitter_base.setStretchFactor(0, 0)
        splitter_base.setStretchFactor(1, 1)

        # connect signal
        self.sub_tasks.SIGNAL_TASK_ATTRS_CLEAR.connect(self.sub_task_attrs.refresh_list)
        self.sub_tasks.SIGNAL_TASK_ATTRS.connect(self.sub_task_attrs.show_sub_task_attrs)


class Connector(QObject):
    SIGNAL_EMIT = Signal(str, str)


class AttrItem(QStandardItem):
    """
    sub class for QStandardItem, a signal will be shoot out when set text, signal contains original text and update text
    """
    def __init__(self, *args, **kwargs):
        super(AttrItem, self).__init__(*args, **kwargs)
        self.connector = Connector()

    def setText(self, text):
        text_orig = self.text()
        super(AttrItem, self).setText(text)
        self.connector.SIGNAL_EMIT.emit(text_orig, text)

    def setData(self, value, role):
        text_orig = self.text()
        super(AttrItem, self).setData(value, role)
        if role == 2:  # seems 2 is set text with double click, not sure what's the role object it is
            self.connector.SIGNAL_EMIT.emit(text_orig, value)


# functions
def attach_group_box(widget, title):
    """
    attach widget to a group box

    Args:
        widget(QWidget): widget need to be attached
        title(str): group box title
    Returns:
        group_box(QGroupBox)
    """
    group_box = QGroupBox(title)
    group_box.setStyleSheet("""QGroupBox {
                                            border: 1px solid gray;
                                            border-radius: 2px;
                                            margin-top: 0.5em;
                                        }

                                        QGroupBox::title {
                                            subcontrol-origin: margin;
                                            left: 10px;
                                            padding: 0 3px 0 3px;
                                        }""")

    layout_widget = QGridLayout(group_box)

    layout_widget.addWidget(widget)  # add widget to group box
    return group_box


def convert_data(value):
    if value:
        try:
            value = ast.literal_eval(value)
        except ValueError:
            # given value is str
            pass
    return value


def convert_data_to_str(value):
    if isinstance(value, list) or isinstance(value, dict):
        value = json.dumps(value)
    else:
        value = str(value)
    return value
