# IMPORT PACKAGES

# import os
import os

# import maya packages
# use the progress bar to escape from the loop
import maya.cmds as cmds
import maya.mel as mel

# import copy_reg, types to fix one pickle problem
import copy_reg
import types

# import ast
import ast

# import inspect
import inspect

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
import utils.common.modules as modules
import utils.common.files as files
import utils.common.naming as naming
import utils.common.attributes as attributes

# import icon
import icons

# import widget
import taskCreator

# import config
import config

# CONSTANT
logger = logUtils.logger

ROLE_TASK_INFO = Qt.UserRole + 1
ROLE_TASK_TYPE = Qt.UserRole + 2
ROLE_TASK_LOCK = Qt.UserRole + 3
ROLE_TASK_SAVE = Qt.UserRole + 4

ROLE_TASK_PRE = Qt.UserRole + 5
ROLE_TASK_RUN = Qt.UserRole + 6
ROLE_TASK_POST = Qt.UserRole + 7
ROLE_TASK_STATUS_INFO = Qt.UserRole + 8

CHECK_STATE = [Qt.Unchecked, Qt.Checked]

# icons
ICONS_STATUS = []  # convert icon image to pixel map so we can make it smaller in ui
for icon in [icons.grey, icons.green, icons.yellow, icons.red]:
    ICONS_STATUS.append(QIcon(icon).pixmap(QSize(15, 15)))

ICON_UNCHECK = QIcon(icons.unCheck).pixmap(QSize(15, 15))

ICONS_TASK = {'task': [icons.task_new, icons.task_reference],
              'callback': [icons.callback_new, icons.callback_reference],
              'method': [icons.method, icons.method]}

# warning color if any unskippable kwarg not set
COLOR_WARN = QColor(255, 0, 0)

# task folders
TASK_FOLDERS_CONFIG = os.path.join(os.path.dirname(config.__file__), 'TASK_FOLDERS.cfg')
TASK_FOLDERS = files.read_json_file(TASK_FOLDERS_CONFIG)

# shortcuts
KEY_CONFIG = os.path.join(os.path.dirname(config.__file__), 'KEY_SHORTCUT.cfg')
KEY_SHORTCUT = files.read_json_file(KEY_CONFIG)

# shortcuts
SC_RELOAD = KEY_SHORTCUT['reload']
SC_RUN_ALL = KEY_SHORTCUT['execute_all']
SC_RUN = KEY_SHORTCUT['execute']
SC_RELOAD_RUN = KEY_SHORTCUT['reload_execute']
SC_REMOVE = KEY_SHORTCUT['remove']
SC_DUPLICATE = KEY_SHORTCUT['duplicate']
SC_EXPAND_COLLAPSE = KEY_SHORTCUT['expand_collapse']


# CLASS
class TaskTree(QTreeWidget):
    """base class for TreeWidget"""
    SIGNAL_PROGRESS_INIT = Signal(int)
    SIGNAL_PROGRESS = Signal(int)  # emit signal to update progress bar
    SIGNAL_ERROR = Signal()  # emit signal for error
    SIGNAL_CLEAR = Signal()
    SIGNAL_EXECUTE = Signal()
    SIGNAL_ATTR_NAME = Signal(QTreeWidgetItem)
    SIGNAL_TASK_TYPE = Signal(QTreeWidgetItem)
    SIGNAL_GET_BUILDER = Signal()
    SIGNAL_LOG_INFO = Signal(str, str)
    SIGNAL_RESET = Signal()  # emit signal to reset buttons

    def __init__(self,  **kwargs):
        super(TaskTree, self).__init__()

        self._expand = True
        self._display_items = []  # list of item display name to make sure no same name
        self._attr_items = []  # list of item attr name to make sure no same name
        self._change = False  # use to check if mouse is on checkbox or actual task

        # get kwargs
        self._header = kwargs.get('header', ['Task', 'Pre', 'Build', 'Post'])
        self.builder = kwargs.get('builder', None)  # builder object

        # task folders
        self.task_folders = TASK_FOLDERS[:]

        self.setFocusPolicy(Qt.NoFocus)

        header_item = QTreeWidgetItem(self._header)
        self.setHeaderItem(header_item)
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setHeaderHidden(True)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setStretchLastSection(False)
        self.setColumnWidth(1, 20)  # column for pre build icon
        self.setColumnWidth(2, 20)  # column for build icon
        self.setColumnWidth(3, 20)  # column for post build icon

        self.setSelectionMode(self.ExtendedSelection)
        self.setDragDropMode(self.InternalMove)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)

        self.setIconSize(QSize(25, 25))

        self._root = self.invisibleRootItem()

        # right clicked menu
        self.menu = QMenu(self)

        # maya progress bar, used to escape from loop
        self.maya_progress_bar = mel.eval('$tmp = $gMainProgressBar')

        # execute menu
        self.menu_execute_sel = SubMenu('Execute Selection', parent=self.menu, shortcut=SC_RUN)

        self.menu_execute_all = SubMenu('Execute All', parent=self.menu, shortcut=SC_RUN_ALL)

        self.menu_rebuild = SubMenu('Rebuild', parent=self.menu, shortcut=SC_RELOAD_RUN)

        self.menu.addMenu(self.menu_execute_sel)
        self.menu.addMenu(self.menu_execute_all)
        self.menu.addMenu(self.menu_rebuild)

        self.action_reload = self.menu.addAction('Reload')
        self.action_reload.setShortcut(SC_RELOAD)

        self.menu.addSeparator()

        self.action_save_data = self.menu.addAction('Save Data')

        self.menu.addSeparator()

        self.action_create = self.menu.addAction('Create')
        self.action_create.setShortcut('Ctrl+n')
        self.action_duplicate = self.menu.addAction('Duplicate')
        self.action_duplicate.setShortcut(SC_DUPLICATE)
        self.action_remove = self.menu.addAction('Remove')
        self.action_remove.setShortcut(SC_REMOVE)

        self.menu.addSeparator()

        self.action_display = self.menu.addAction('Display Name')
        self.action_color_background = self.menu.addAction('Background Color')
        self.action_color_reset = self.menu.addAction('Reset Color')

        self.menu.addSeparator()

        self.action_expand = self.menu.addAction('Expand/Collapse')
        self.action_expand.setShortcut(SC_EXPAND_COLLAPSE)

        # set enable/disable
        self._menu_widgets = [self.menu_execute_sel, self.menu_execute_all, self.action_duplicate, self.action_remove,
                              self.action_display, self.action_color_background, self.action_color_reset]

        for widget in self._menu_widgets:
            widget.setEnabled(False)

        self.action_save_data.setEnabled(False)

        # connect functions
        self.action_reload.triggered.connect(self.reload_tasks)
        self.menu_execute_sel.SIGNAL_SECTION.connect(self.run_sel_tasks)
        self.menu_execute_all.SIGNAL_SECTION.connect(self.run_all_tasks)
        self.menu_rebuild.SIGNAL_SECTION.connect(self.rebuild_tasks)

        self.action_save_data.triggered.connect(self._save_task_data)

        self.action_duplicate.triggered.connect(self.duplicate_tasks)
        self.action_remove.triggered.connect(self.remove_tasks)

        self.action_display.triggered.connect(self.set_display_name)
        self.action_color_background.triggered.connect(self.set_background_color)
        self.action_color_reset.triggered.connect(self.reset_background_color)

        self.action_expand.triggered.connect(self.expand_collapse)

        # task creation window
        self.task_create_window = TaskCreate()
        self.action_create.triggered.connect(self.task_create_window_open)
        self.task_create_window.SIGNAL_TASK_CREATION.connect(self._create_task)

        # task switch window
        self.task_switch_window = TaskSwitch()
        self.task_switch_window.SIGNAL_TASK_SWITCH.connect(self.set_task_type)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

        # short cut
        QShortcut(QKeySequence(SC_DUPLICATE), self, self.duplicate_tasks)
        QShortcut(QKeySequence(SC_REMOVE), self, self.remove_tasks)
        QShortcut(QKeySequence(SC_EXPAND_COLLAPSE), self, self.expand_collapse)

        self.itemChanged.connect(self._item_data_changed)
        self.itemPressed.connect(self._item_data_changed_reset)
        self.itemClicked.connect(self._show_log_status_info)

    def add_tree_items(self):
        self._add_child_item(self._root,
                             self.builder.tree_hierarchy())

        self.expandAll()

    def dropEvent(self, event):
        if event.source() == self:
            QAbstractItemView.dropEvent(self, event)

    def dropMimeData(self, parent, row, data, action):
        if action == Qt.MoveAction:
            return self.move_selection(parent, row)
        return False

    def move_selection(self, parent, position):
        """
        got drag drop function code here
        https://riverbankcomputing.com/pipermail/pyqt/2009-December/025379.html
        """
        selection = [QPersistentModelIndex(i)
                     for i in self.selectedIndexes()]
        parent_index = self.indexFromItem(parent)
        if parent_index in selection:
            return False

        # save the drop location in case it gets moved
        target = self.model().index(position, 0, parent_index).row()
        if target < 0:
            target = position

        # remove the selected items
        taken = []
        for index in reversed(selection):
            item = self.itemFromIndex(QModelIndex(index))
            if item is None or item.parent() is None:
                taken.append(self.takeTopLevelItem(index.row()))
            else:
                taken.append(item.parent().takeChild(index.row()))

        # insert the selected items at their new positions
        while taken:
            if position == -1:
                # append the items if position not specified
                if parent_index.isValid():
                    parent.insertChild(
                        parent.childCount(), taken.pop(0))
                else:
                    self.insertTopLevelItem(
                        self.topLevelItemCount(), taken.pop(0))
            else:
                # insert the items at the specified position
                if parent_index.isValid():
                    parent.insertChild(min(target,
                                           parent.childCount()), taken.pop(0))
                else:
                    self.insertTopLevelItem(min(target,
                                                self.topLevelItemCount()), taken.pop(0))
        return True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and event.modifiers() == Qt.NoModifier:
            self._clear_selection()

    def mousePressEvent(self, event):
        if not self.indexAt(event.pos()).isValid():
            self._clear_selection()

        super(TaskTree, self).mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        # double click to run the task
        if self.indexAt(event.pos()).isValid():
            if not self._change:
                self.run_sel_tasks()

    def show_menu(self, pos):
        top_item_count = self.topLevelItemCount()  # only show right click menu when builder loaded
        if top_item_count:
            select_items = self.selectedItems() # check if has task selected
            if not select_items:
                # disable actions for select task (duplicate, rename etc..)
                for widget in self._menu_widgets:
                    widget.setEnabled(False)
                self.action_save_data.setEnabled(False)
            else:
                for widget in self._menu_widgets:
                    widget.setEnabled(True)

                duplicate = False
                remove = False
                save = False

                # loop in each item to check if we can enable these function
                for item in select_items:
                    task_type = item.data(0, ROLE_TASK_TYPE)
                    task_lock = item.data(0, ROLE_TASK_LOCK)
                    task_save = item.data(0, ROLE_TASK_SAVE)

                    if task_type != 'method':
                        # we can't duplicate in class method
                        duplicate = True
                        if not task_lock:
                            # we can only remove task not inherited, and not in class method
                            remove = True

                    if task_save:
                        save = True

                    if duplicate and remove and save:
                        # if all True, no need to continue the loop
                        break

                self.action_duplicate.setEnabled(duplicate)
                self.action_remove.setEnabled(remove)
                self.action_save_data.setEnabled(save)

            self.menu.move(QCursor.pos())  # move menu to right clicked position

            self.menu.show()

    # task functions to connect with button and menu
    def run_sel_tasks(self, section=None):
        if section is None:
            section = ['pre_build', 'build', 'post_build']
        items = self.selectedItems()
        if items:
            self._run_task(items=items, section=section)
            self.SIGNAL_EXECUTE.emit()

    def run_all_tasks(self, section=None):
        if section is None:
            section = ['pre_build', 'build', 'post_build']
        top_item_count = self.topLevelItemCount()
        if top_item_count:
            # builder loaded
            self._run_task(section=section)
            self.SIGNAL_EXECUTE.emit()

    def rebuild_tasks(self, section=None):
        if section is None:
            section = ['pre_build', 'build', 'post_build']
        self.reload_tasks()
        self._run_task(section=section)
        self.SIGNAL_EXECUTE.emit()

    def reload_tasks(self):
        self._display_items = []
        self._attr_items = []

        self._expand = True

        if self.builder:
            self._remove_all_tasks()
            self.add_tree_items()
        # refresh progress bar, shoot signal
        # the range doesn't matter, will re-init when run the task
        self.SIGNAL_PROGRESS_INIT.emit(1)

    def set_display_name(self):
        item = self.currentItem()
        current_name = item.text(0)
        text, ok = QInputDialog.getText(self, 'Display Name', 'Set Display Name', text=current_name)
        if text and ok and text != current_name:
            update_name = self._get_unique_name(current_name, text, self._display_items)
            item.setText(0, update_name)
            # update task info
            task_info = item.data(0, ROLE_TASK_INFO)
            task_info.update({'display': update_name})
            item.setData(0, ROLE_TASK_INFO, task_info)

    def set_background_color(self):
        items = self.selectedItems()
        background_col = items[-1].background(0).color()
        col = QColorDialog.getColor(background_col, self, 'Background Color')
        if col.isValid():
            for item in items:
                items_collect = self._collect_items(item)
                for item_setCol in items_collect:
                    item_setCol.setBackground(0, col)

    def reset_background_color(self):
        items = self.selectedItems()
        for item in items:
            items_collect = self._collect_items(item)
            for item_setCol in items_collect:
                item_setCol.setData(0, Qt.BackgroundRole, None)

    def set_attr_name(self, name):
        title = "Change task's object name in the builder"
        # check if name already exists
        if name in self._attr_items:
            text = 'object name already exists'
            QMessageBox.warning(self, title, text)
            return
        else:
            # check if the string starts with letter
            try:
                ast.literal_eval(name[0])  # not letter
                check = False
            except ValueError:
                check = True  # letter
            except SyntaxError:
                check = False  # unknown type

            if not check:
                # raise warning box
                text = 'task object name is illegal, must start with letter'
                QMessageBox.warning(self, title, text)
                return
            else:
                # convert name to snake case
                name = naming.convert_camel_case(name, output_format='snake_case')
                # set attr name
                item = self.currentItem()
                task_info = item.data(0, ROLE_TASK_INFO)
                current_name = task_info['attr_name']
                task_info.update({'attr_name': name})
                item.setData(0, ROLE_TASK_INFO, task_info)
                # remove previous name, add new name
                self._attr_items.remove(current_name)
                self._attr_items.append(name)

                # check task type
                task_type = item.data(0, ROLE_TASK_TYPE)
                if task_type != 'callback':
                    # it's a task object
                    # attach the task object to builder as new attr name, remove the previous one
                    task_obj = getattr(self.builder, current_name)  # get object from the previous attr
                    setattr(self.builder, name, task_obj)  # attach with the new name
                    delattr(self.builder, current_name)  # remove the previous one

                # shoot signal to reset task info
                self.SIGNAL_ATTR_NAME.emit(item)

    def set_task_type(self, task_path):
        item = self.selectedItems()[0]
        task_info = item.data(0, ROLE_TASK_INFO)
        task_type_orig = item.data(0, ROLE_TASK_TYPE)
        task_name = task_info['attr_name']
        task_path_orig = task_info['task_path']
        # compare if changed
        if task_path != task_path_orig:
            # get obj
            # imported task, get task object
            task_import, task_function = modules.import_module(task_path)
            task = getattr(task_import, task_function)

            # kwargs
            if task_type_orig == 'callback':
                task_kwargs = task_import.kwargs_ui.copy()  # get a copy of kwargs
            else:
                task_kwargs = task().kwargs_ui.copy()  # get a copy of kwargs

            kwargs_orig = task_info['task_kwargs']  # get original kwargs to see if any can be swapped
            for key in kwargs_orig:
                if key in task_kwargs:
                    dv_orig = kwargs_orig[key]['default']
                    dv = task_kwargs[key]['default']
                    if type(dv_orig) == type(dv):
                        # same type of input, swap
                        task_kwargs[key]['default'] = dv_orig
                        # check if value, if value, swap
                        if 'value' in kwargs_orig[key]:
                            task_kwargs[key].update({'value': kwargs_orig[key]['value']})

            task_info.update({'task_path': task_path,
                              'task': task,
                              'task_kwargs': task_kwargs})

            set_item_data(item, **task_info)

            task_type = item.data(0, ROLE_TASK_TYPE)  # get the update task type
            if task_type != 'callback':
                # attach to builder
                task_obj = task(name=task_name, builder=self.builder)
                setattr(self.builder, task_name, task_obj)
            else:
                # object switched from task object to callback, need to remove the task object attached to builder
                delattr(self.builder, task_name)

            # shoot signal to reset task info
            self.SIGNAL_TASK_TYPE.emit(item)

    def duplicate_tasks(self):
        items = self.selectedItems()
        for item in items:
            # get task info
            task_info = item.data(0, ROLE_TASK_INFO)
            task_type = item.data(0, ROLE_TASK_TYPE)

            if task_type != 'method':
                # can't duplicate in class method
                display = task_info['display']
                attr_name = task_info['attr_name']
                display = self._get_unique_name('', display, self._display_items)
                attr_name = self._get_unique_name('', attr_name, self._attr_items)

                task_info.update({'display': display,
                                  'attr_name': attr_name})

                self._create_item(**task_info)

    def remove_tasks(self):
        for item in self.selectedItems():
            # check type, can't delete in class method or task referenced from parented classes
            task_type = item.data(0, ROLE_TASK_TYPE)
            task_lock = item.data(0, ROLE_TASK_LOCK)

            if task_type != 'method' and not task_lock:
                # re-parent child if any is method, and get remove list
                remove_items = self._re_parent_children(item=item)

                for itm in remove_items:
                    task_info = itm.data(0, ROLE_TASK_INFO)
                    display = itm.text(0)
                    attr_name = task_info['attr_name']

                    # remove names from list
                    if display in self._display_items:
                        self._display_items.remove(display)
                    if attr_name in self._attr_items:
                        self._attr_items.remove(attr_name)

                    # remove object from builder
                    if hasattr(self.builder, attr_name):
                        delattr(self.builder, attr_name)

                    index = self.indexFromItem(itm)
                    if index.row() >= 0:
                        # index >= 0 means still in ui, remove it
                        parent = itm.parent()
                        if not parent:
                            parent = self._root
                        parent.removeChild(itm)

    def expand_collapse(self):
        self._expand = not self._expand
        if not self._expand:
            self.collapseAll()
        else:
            self.expandAll()

    def reload_builder(self, builder_path):
        builder_module, builder_function = modules.import_module(builder_path)
        reload(builder_module)
        self.builder = getattr(builder_module, builder_function)()
        self.builder.registration()
        self.reload_tasks()

    def check_save(self):
        if self.builder and self.topLevelItemCount():
            title = "Saving Check"
            text = "Reload builder will lose any unsaved data, do you want to save first?"
            reply = QMessageBox.warning(self, title, text, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                        defaultButton=QMessageBox.Cancel)

            if reply == QMessageBox.Yes:
                self.export_current_builder()
                self.SIGNAL_GET_BUILDER.emit()
            elif reply == QMessageBox.No:
                self.SIGNAL_GET_BUILDER.emit()
        else:
            self.SIGNAL_GET_BUILDER.emit()

    def export_current_builder(self, export_file=True):
        """
        export task info file
        Keyword Args:
            export_file(bool): will only print out the export tasks info if set to False, for debugging only,
                               default is True
        """
        if self.builder:
            items = self._collect_items()
            export_data = []

            task_previous = 0  # save the previous task attr_name, use this to order the tasks
            for item in items:
                task_info = item.data(0, ROLE_TASK_INFO)
                task_name = task_info['attr_name']
                parent = item.parent()
                check = item.checkState(0)

                background_color_role = item.data(0, Qt.BackgroundRole)

                if not background_color_role:
                    background_color = None
                else:
                    background_color = [item.background(0).color().red(),
                                        item.background(0).color().green(),
                                        item.background(0).color().blue()]

                if check == Qt.Checked:
                    check = 1
                else:
                    check = 0

                if parent:
                    parent_task_info = parent.data(0, ROLE_TASK_INFO)
                    parent = parent_task_info['attr_name']
                else:
                    parent = ''

                task_info.update({'parent': parent,
                                  'index': task_previous,
                                  'check': check,
                                  'background_color': background_color})

                export_data.append({task_name: task_info})
                task_previous = task_name

            # save data
            self.builder.export_tasks_info(export_data, save_file=export_file)

    def task_create_window_open(self):
        # get task folders
        task_folders = self.task_folders[:]
        task_folders.append(self._get_project_task_folder(self.builder))

        # try close window in case it's opened
        self.task_create_window.close()
        self.task_create_window.refresh_widgets()
        self.task_create_window.widget_task_creation.rebuild_list_model(task_folders)
        self.task_create_window.move(QCursor.pos())
        self.task_create_window.show()

    def task_switch_window_open(self):
        # try close window in case it's opened
        self.task_switch_window.close()

        # check if task is referenced or in class method
        item = self.selectedItems()[0]
        # check if item is referenced
        lock = item.data(0, ROLE_TASK_LOCK)
        task_type_orig = item.data(0, ROLE_TASK_TYPE)
        title = "Change task's type"
        if task_type_orig == 'method':
            text = "task is a in-class method, can't switch type"
            QMessageBox.warning(self, title, text)
            return
        elif lock:
            text = "task is inherited from parent class or registered in class, can't switch type"
            QMessageBox.warning(self, title, text)
            return
        else:
            # get task folders
            task_folders = self.task_folders[:]
            task_folders.append(self._get_project_task_folder(self.builder))

            self.task_switch_window.refresh_widgets()
            self.task_switch_window.widget_task_creation.rebuild_list_model(task_folders)
            self.task_switch_window.move(QCursor.pos())
            self.task_switch_window.show()

    def _add_child_item(self, item, data):
        for d in data:
            name = d.keys()[0]
            data_info = d[name]
            data_info.update({'attr_name': name})  # put attr name in kwargs for further use
            task_item = TaskItem(**data_info)

            self._display_items.append(data_info['display'])  # add to list for later check
            self._attr_items.append(name)  # add to list for later check

            item.addChild(task_item)

            if 'children' in data_info:
                self._add_child_item(task_item, data_info['children'])

    def _re_parent_children(self, item):
        """
        re parent children if upper parent got removed
        """
        item_children = self._collect_items(item=item)
        item_hold = []
        item_remove = [item]

        for itm in item_children[1:]:
            task_type = itm.data(0, ROLE_TASK_TYPE)
            task_lock = itm.data(0, ROLE_TASK_LOCK)
            if task_type == 'method' or task_lock:
                item_hold.append(itm)
            else:
                item_remove.append(itm)

        # check if item_hold parent need to be removed or not
        for itm in item_hold:
            itm_search = itm
            while True:
                parent = itm_search.parent()
                if not parent or parent not in set(item_remove):
                    # reach top level
                    index = self.indexFromItem(itm_search)

                    # to add the item to upper level, we need take it out first
                    index_orig = self.indexFromItem(itm)
                    itm.parent().takeChild(index_orig.row())

                    # add item to upper level
                    if not parent:
                        self.insertTopLevelItem(index.row(), itm)
                    else:
                        parent.insertChild(index.row(), itm)
                    break

                else:
                    itm_search = parent

        return item_remove

    def _run_task(self, items=None, collect=True, section=None, ignore_check=False):
        """
        run task

        Keyword Args:
            items(QItem): None will be the root, default is None
            collect(bool): loop downstream tasks, default is True
            section(list): run for specific section, None will run for all, default is None
                           ['pre_build', 'build', 'post_build']
            ignore_check(bool): ignore the item's check state if True, default is False
        """
        if section is None:
            section = ['pre_build', 'build', 'post_build']

        running_role = {'pre_build': ROLE_TASK_PRE,
                        'build': ROLE_TASK_RUN,
                        'post_build': ROLE_TASK_POST}

        # collect items
        if isinstance(items, list):
            items_run = []
            for item in items:
                if collect and item not in set(items_run):
                    items_run += self._collect_items(item)
                    ignore_check = False
                else:
                    items_run = items
                    ignore_check = True
        else:
            # because the function can be only triggered by ui,
            # it can only happens at None with collect set to True, or single item with/without collect
            if collect:
                items_run = self._collect_items(item=items)
                ignore_check = False
            else:
                items_run = [items]
                ignore_check = True

        progress_max = len(items_run)*len(section)

        clear_maya_progress_bar_cache(self.maya_progress_bar, progress_max)  # clear out the cache

        # shoot signal to progress bar
        self.SIGNAL_PROGRESS_INIT.emit(len(items_run) * len(section))

        # loop in each task
        item_count = float(len(items_run))
        break_checker = False  # escape the loop if maya progress bar end by user (ESC pressed)
        for i, sec in enumerate(section):
            if break_checker:
                break
            role = running_role[sec]
            for j, item in enumerate(items_run):
                # get task info
                task_info = item.data(0, ROLE_TASK_INFO)
                task_type = item.data(0, ROLE_TASK_TYPE)
                task_display = item.text(0)
                check_state = item.checkState(0)

                # reduce task kwargs, because original one contains lots of ui info we don't need
                task_kwargs = {}
                for key, data in task_info['task_kwargs'].iteritems():
                    if 'value' in data and data['value'] is not None:
                        val = data['value']
                    else:
                        val = data['default']
                    attr_name = data['attr_name']
                    task_kwargs.update({attr_name: val})

                # check if the item is unchecked
                if check_state == Qt.Checked or ignore_check:
                    # get task running state, skipped if already run
                    item_running_state = item.data(0, role)
                    if item_running_state == 0:
                        # item haven't run, start running task
                        # check progress bar
                        if cmds.progressBar(self.maya_progress_bar, query=True, isCancelled=True):
                            # escape from loop
                            self.SIGNAL_ERROR.emit()
                            logger.warning('Task process is stopped by the user')
                            break_checker = True
                            break

                        # check item type
                        if task_type == 'method':
                            # get section registered
                            section_init = task_info['section']

                            if sec != section_init:
                                # skip
                                item.setData(0, role, 1)
                            else:
                                # try to run in class method
                                try:
                                    task_func = task_info['task']
                                    task_return = task_func(**task_kwargs)
                                    message = ''
                                    task_return_state = 1  # success
                                    if isinstance(task_return, basestring):
                                        message = task_return  # override message to store in icon
                                    self._execute_setting(item, task_return_state, 'method', task_display, role, sec,
                                                          message)
                                except Exception as exc:
                                    self._error_setting(item, exc, role)

                        # check if registered function is a function (mainly for callback)
                        elif task_type == 'callback':
                            # try to run function
                            try:
                                if task_kwargs[sec]:
                                    # if section has callback code
                                    task_func = task_info['task']
                                    task_func(task_kwargs[sec])
                                self._execute_setting(item, 1, 'function', task_display, role, sec, '')
                            except Exception as exc:
                                self._error_setting(item, exc, role)
                        else:
                            # Task is an imported task
                            # try to run task
                            try:
                                # get task name
                                task_name = task_info['attr_name']
                                task_obj = getattr(self.builder, task_name)

                                if sec == 'pre_build':
                                    # register input data
                                    task_obj.kwargs_input = task_kwargs

                                    # check if task is duplicate
                                    if task_type == 'copy':
                                        # check target task is a pack or not
                                        attr_name_target = task_kwargs.get('duplicate_component', None)
                                        if attr_name_target:
                                            task_target = modules.get_obj_attr(self.builder, attr_name_target)
                                            if task_target:
                                                # check if the target is pack, override the parameter if so
                                                task_type = task_target.task_type

                                    # check if task is pack
                                    if task_type == 'pack':
                                        # get child count
                                        child_count = item.childCount()

                                        # loop downstream
                                        for index_child in range(child_count):
                                            # get item
                                            child_item = item.child(index_child)
                                            # get child task info
                                            child_task_info = child_item.data(0, ROLE_TASK_INFO)
                                            # get check state
                                            child_check_state = child_item.checkState(0)
                                            # add to pack if checked
                                            if child_check_state == Qt.Checked:
                                                task_obj.sub_components_attrs.append(child_task_info['attr_name'])

                                # run task
                                func = getattr(task_obj, sec)
                                func()
                                return_signal = task_obj.signal
                                message = task_obj.message

                                self._execute_setting(item, return_signal, 'task', task_display, role, sec, message)
                            except Exception as exc:
                                self._error_setting(item, exc, role)

                # progress bar grow
                cmds.progressBar(self.maya_progress_bar, edit=True, step=1)

                # emit signal
                self.SIGNAL_PROGRESS.emit(item_count * i + j + 1)

        # end progress bar
        cmds.progressBar(self.maya_progress_bar, edit=True, endProgress=True)

        # emit reset signal
        self.SIGNAL_RESET.emit()

    def _error_setting(self, item, exc, role):
        # error raises
        item.setData(0, role, 3)
        # emit error signal
        self.SIGNAL_ERROR.emit()
        # emit reset signal
        self.SIGNAL_RESET.emit()
        logger.error(exc)

        # save log info for display
        self._save_log_status_info(item, exc, role)

        # end maya progress bar
        cmds.progressBar(self.maya_progress_bar, edit=True, endProgress=True)

        raise RuntimeError()

    def _execute_setting(self, item, task_return, function_name, display, role, section, message):
        if task_return == 2:
            # warning raises
            item.setData(0, role, 2)
        else:
            # run successfully
            item.setData(0, role, 1)

        if message:
            # save log info for display
            self._save_log_status_info(item, message, role)

        # log
        logger.info('[{}] -- Run {} "{}" successfully'.format(section, function_name, display))

    def _collect_items(self, item=None):
        """
        collect items parented to the item in order [item included]

        collect items from root if item is None
        """

        if item:
            items = [item]
        else:
            items = []
            item = self._root

        # get child count
        child_count = item.childCount()

        # loop downstream
        for i in range(child_count):
            items += self._collect_items(item=item.child(i))

        return items

    def _create_item(self, item=None, **kwargs):
        """
        create QTreeWidgetItem
        """
        if not item:
            item = self._root

        item_create = TaskItem(**kwargs)

        item.addChild(item_create)

    def _create_task(self, task_info):
        attr_name = task_info[0]
        display = task_info[1]
        task_path = task_info[2]

        save_data = False

        attr_name = self._get_unique_name('', attr_name, self._attr_items)
        self._attr_items.append(attr_name)

        if not display:
            display = attr_name
        display = self._get_unique_name('', display, self._display_items)
        self._display_items.append(display)

        # imported task, get task object
        task_import, task_function = modules.import_module(task_path)
        task = getattr(task_import, task_function)

        if inspect.isfunction(task):
            # function, normally is callback
            task_kwargs = task_import.kwargs_ui
        else:
            # task class
            task_obj = task(name=attr_name, builder=self.builder)
            task_kwargs = task_obj.kwargs_ui
            save_data = task_obj.save
            # attach to builder
            setattr(self.builder, attr_name, task_obj)

        kwargs = {'display': display,
                  'attr_name': attr_name,
                  'task_path': task_path,
                  'task': task,
                  'task_kwargs': task_kwargs,
                  'check': 1,
                  'lock': False,
                  'save_data': save_data}

        item = self.selectedItems()
        if item:
            item = item[0]

        self._create_item(item=item, **kwargs)

    def _remove_all_tasks(self):
        item_count = self.topLevelItemCount()
        for i in range(item_count):
            self.takeTopLevelItem(0)

    def _clear_selection(self):
        self.clearSelection()
        self.clearFocus()
        self.setCurrentIndex(QModelIndex())

        # shoot clear signal
        self.SIGNAL_CLEAR.emit()

    def _item_data_changed(self, *args):
        self._change = True

    def _item_data_changed_reset(self, *args):
        self._change = False

    def _show_log_status_info(self, *args):
        item = self.currentItem()
        col = self.currentColumn()
        log_status_info = item.data(0, ROLE_TASK_STATUS_INFO)
        if col > 0:
            log_info = log_status_info[col-1]
            level_index = item.data(0, [ROLE_TASK_PRE, ROLE_TASK_RUN, ROLE_TASK_POST][col-1])
            level = ['info', 'warning', 'error'][level_index - 1]
            check = item.checkState(0)
            if check == Qt.Checked and log_info:
                self.SIGNAL_LOG_INFO.emit(log_info, level)

    def _save_task_data(self, *args):
        for item in self.selectedItems():
            task_save = item.data(0, ROLE_TASK_SAVE)  # check if task has saving function
            if task_save:
                task_info = item.data(0, ROLE_TASK_INFO)
                task_name = task_info['attr_name']
                task_kwargs = task_info['task_kwargs']

                # get task obj from builder
                task_obj = getattr(self.builder, task_name)

                # register kwargs
                # some saving function need the input information to save data for specific node
                task_obj.kwargs_task = task_kwargs
                task_obj.register_inputs()

                # trigger save data function
                task_obj.save_data()

    @ staticmethod
    def _get_unique_name(name_orig, name_new, name_list):
        i = 1
        name_new_add = name_new
        while name_new_add in name_list:
            name_new_add = name_new + str(i)
            i += 1
        name_list.append(name_new_add)
        if name_orig:
            name_list.remove(name_orig)
        return name_new_add

    @ staticmethod
    def _get_project_task_folder(builder):
        if builder:
            return 'projects.{}.scripts.tasks'.format(builder.project)

    @ staticmethod
    def _save_log_status_info(item, message, role):
        if role == ROLE_TASK_PRE:
            index = 0
        elif role == ROLE_TASK_RUN:
            index = 1
        else:
            index = 2

        log_status_info = item.data(0, ROLE_TASK_STATUS_INFO)
        log_status_info[index] = message
        item.setData(0, ROLE_TASK_STATUS_INFO, log_status_info)

    @ staticmethod
    def _get_item_children_attr_names(item):
        """
        get item's children's attr names as list
        Args:
            item(TaskItem)

        Returns:
            attr_name_children(list)
        """
        # get child count
        child_count = item.childCount()

        attr_name_children = []
        # loop downstream
        for index_child in range(child_count):
            # get item
            child_item = item.child(index_child)
            # get child task info
            child_task_info = child_item.data(0, ROLE_TASK_INFO)
            # get check state
            child_check_state = child_item.checkState(0)
            # add to pack if checked
            if child_check_state == Qt.Checked:
                attr_name_children.append(child_task_info['attr_name'])

        return attr_name_children


class TaskItem(QTreeWidgetItem):
    def __init__(self, **kwargs):
        super(TaskItem, self).__init__()
        background_color = kwargs.get('background_color', None)

        self.setFlags(self.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

        # get task kwargs keys as list,
        # because QTreeWidgetItem can't save order dictionary, we need the list to store the keys order
        task_kwargs = kwargs.get('task_kwargs', {})
        task_kwargs_keys = task_kwargs.keys()
        kwargs.update({'task_kwargs_keys': task_kwargs_keys})

        # initialize each icon, set to fresh status,
        # we need to set icon info first, because it override setData function
        self.setData(0, ROLE_TASK_PRE, 0)
        self.setData(0, ROLE_TASK_RUN, 0)
        self.setData(0, ROLE_TASK_POST, 0)
        self.setData(0, ROLE_TASK_STATUS_INFO, ['', '', ''])  # save log info for display

        # carry the task's kwargs for further use
        self.setData(0, ROLE_TASK_INFO, kwargs)

        # set item info
        set_item_data(self, **kwargs)

        # set background color
        if background_color is not None:
            background_qcolor = QColor()
            background_qcolor.setRgb(background_color[0], background_color[1], background_color[2])
            self.setBackground(0, background_qcolor)
        else:
            self.setData(0, Qt.BackgroundRole, None)

        font = QFont()
        font.setPointSize(9)
        self.setFont(0, font)

    def setData(self, column, role, value):
        super(TaskItem, self).setData(column, role, value)
        # change icons if item is checked/unchecked
        if role == Qt.CheckStateRole:
            state = self.checkState(column)
            if state == Qt.Checked:
                # checked, go back to the icons previous
                task_return_pre = self.data(0, ROLE_TASK_PRE)
                task_return_run = self.data(0, ROLE_TASK_RUN)
                task_return_post = self.data(0, ROLE_TASK_POST)
                self.setIcon(1, ICONS_STATUS[task_return_pre])
                self.setIcon(2, ICONS_STATUS[task_return_run])
                self.setIcon(3, ICONS_STATUS[task_return_post])
            else:
                # unchecked, set icon to uncheck
                self.setIcon(1, ICON_UNCHECK)
                self.setIcon(2, ICON_UNCHECK)
                self.setIcon(3, ICON_UNCHECK)

        elif role == ROLE_TASK_PRE:
            # set icon for the pre build
            self.setIcon(1, ICONS_STATUS[value])

        elif role == ROLE_TASK_RUN:
            # set icon for the build
            self.setIcon(2, ICONS_STATUS[value])

        elif role == ROLE_TASK_POST:
            # set icon for the post build
            self.setIcon(3, ICONS_STATUS[value])

        elif role == ROLE_TASK_INFO:
            # normally happens when property editor send back the kwargs set by user
            # check if has any unskippable kwarg not being set
            task_info = self.data(0, ROLE_TASK_INFO)
            warn = False
            for key, item in task_info['task_kwargs'].iteritems():
                warn = item.get('warn', False)
                if warn:
                    break
            if warn:
                self.setForeground(0, COLOR_WARN)
            else:
                self.setData(0, Qt.ForegroundRole, None)


class SubMenu(QMenu):
    """
    subMenu for right click menu
    include All, Pre-Build, Build, Post-Build
    and emit custom signal for further use
    """
    SIGNAL_SECTION = Signal(list)

    def __init__(self, title, parent=None, shortcut=''):
        super(SubMenu, self).__init__(title, parent)

        self.all = self.addAction('All')

        if shortcut:
            self.all.setShortcut(shortcut)

        self.pre = self.addAction('Pre-Build')
        self.build = self.addAction('Build')
        self.post = self.addAction('Post-Build')

        self.all.triggered.connect(self._all_triggered)
        self.pre.triggered.connect(self._pre_triggered)
        self.build.triggered.connect(self._build_triggered)
        self.post.triggered.connect(self._post_triggered)

    def _all_triggered(self):
        self.SIGNAL_SECTION.emit(['pre_build', 'build', 'post_build'])

    def _pre_triggered(self):
        self.SIGNAL_SECTION.emit(['pre_build'])

    def _build_triggered(self):
        self.SIGNAL_SECTION.emit(['build'])

    def _post_triggered(self):
        self.SIGNAL_SECTION.emit(['post_build'])


class TaskCreate(taskCreator.TaskCreate):
    """widget to create task"""
    SIGNAL_TASK_CREATION = Signal(list)

    def __init__(self, parent=None):
        super(TaskCreate, self).__init__(parent, title='Create Task', button='Create', set_name=True)

        self.button.clicked.connect(self._get_select_task)

    def refresh_widgets(self):
        self.task_side.setCurrentIndex(self.index_side_default)
        self.task_des.setText('')
        self.task_display.setText('')
        self.widget_task_creation.filter.setText('')
        self.setFocus()

    def _get_select_task(self):
        side = self.task_side.currentText()
        description = self.task_des.text()
        name = naming.Namer(type=naming.Type.task, side=side, description=description).name
        display = self.task_display.text()
        task = self.widget_task_creation.listView.currentIndex().data()

        self.SIGNAL_TASK_CREATION.emit([name, display, task])

        self.close()


class TaskSwitch(taskCreator.TaskCreate):
    """widget to switch task type"""
    SIGNAL_TASK_SWITCH = Signal(str)

    def __init__(self, parent=None):
        super(TaskSwitch, self).__init__(parent, title='Change Task Type', button='Set', set_name=False)

        self.button.clicked.connect(self._get_select_task)

    def refresh_widgets(self):
        self.widget_task_creation.filter.setText('')
        self.setFocus()

    def _get_select_task(self):
        task = self.widget_task_creation.listView.currentIndex().data()

        self.SIGNAL_TASK_SWITCH.emit(task)

        self.close()


# SUB FUNCTION
def set_item_data(item, **kwargs):
    """
    set TaskItem's data

    Args:
        item(TaskItem): task item object
    """
    display = kwargs.get('display', None)
    task_path = kwargs.get('task_path', None)
    task = kwargs.get('task', None)
    lock = kwargs.get('lock', None)
    check = kwargs.get('check', None)
    save_data = kwargs.get('save_data', False)

    if display is not None:
        item.setText(0, display)

    if lock is not None:
        item.setData(0, ROLE_TASK_LOCK, lock)

    # we need save info in task item so it's easier to check when we right click
    # other wise we have to loop in each kwargs to get the value, which is unnecessary
    item.setData(0, ROLE_TASK_SAVE, save_data)

    if task is not None:
        if inspect.ismethod(task):
            item.setData(0, ROLE_TASK_TYPE, 'method')
            task_icons = [icons.method, icons.method]
        elif inspect.isfunction(task):
            item.setData(0, ROLE_TASK_TYPE, 'callback')
            task_icons = [icons.callback_new, icons.callback_reference]
        else:
            item.setData(0, ROLE_TASK_TYPE, task_path)  # normally user will given task_path and task together
            task_icons = task().icons

        if lock is None:
            lock = 0

        item.setIcon(0, QIcon(task_icons[lock]))  # set task's icon

    if check is not None:
        item.setCheckState(0, CHECK_STATE[check])


def clear_maya_progress_bar_cache(progress_bar, progress_max):
    """
    there seems a maya bug that after cancelled the progress bar with multiple ESC, maya didn't clear the cache
    when the progress end, so we have to create/end progress bar one or two times to clear the cache

    Args:
        progress_bar(str): maya progress bar name
        progress_max(int): maya progress bar max value
    """

    for i in range(10):
        # I don't want to have infinity loop, normally it should be only one or two times to clear out
        # create progress bar
        cmds.progressBar(progress_bar, edit=True, beginProgress=True, isInterruptable=True,
                         status='Tasks Running ...', maxValue=progress_max)
        # check if still has cache
        if cmds.progressBar(progress_bar, query=True, isCancelled=True):
            # end progress bar and re loop in
            cmds.progressBar(progress_bar, edit=True, endProgress=True)
        else:
            # cache cleared out, finish the loop
            break


# Fix
"""
For some reason, when I middle mouse drag the tasks, it freeze the ui,
and gave me an error when I try to use QWidget.close()

Base on what stack overflow said
    https://stackoverflow.com/questions/1816958/cant-pickle-type-instancemethod-when-using-multiprocessing-pool-map
    
    The problem is that multiprocessing must pickle things to sling them among processes, 
    and bound methods are not picklable. 
    The workaround (whether you consider it "easy" or not)
    is to add the infrastructure to your program to allow such methods to be pickled, 
    registering it with the copy_reg standard library method

Don't really know what this is, but it seems work well
"""


def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)


def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)


copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)