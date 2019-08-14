# IMPORT PACKAGES

# import maya.utils
# maya commands are not thread safe, need to use maya.utils.executeInMainThreadWithResult(function) to execute it
import maya.utils

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

# import icon
import icons

# import widget
import taskCreator

# CONSTANT
logger = logUtils.get_logger(name='rig_build', level='info')

ROLE_TASK_NAME = Qt.UserRole + 1
ROLE_TASK_PATH = Qt.UserRole + 2
ROLE_TASK_FUNC = Qt.UserRole + 3
ROLE_TASK_KWARGS = Qt.UserRole + 4
ROLE_TASK_KWARGS_KEY = Qt.UserRole + 5
ROLE_TASK_PRE = Qt.UserRole + 6
ROLE_TASK_RUN = Qt.UserRole + 7
ROLE_TASK_POST = Qt.UserRole + 8
ROLE_TASK_SECTION = Qt.UserRole + 9
ROLE_TASK_TYPE = Qt.UserRole + 10
ROLE_TASK_INHERITANCE = Qt.UserRole + 11

# icons
ICONS_STATUS = []  # convert icon image to pixel map so we can make it smaller in ui
for icon in [icons.grey, icons.green, icons.yellow, icons.red]:
    ICONS_STATUS.append(QIcon(icon).pixmap(QSize(15, 15)))

ICON_UNCHECK = QIcon(icons.unCheck).pixmap(QSize(15, 15))

ICONS_TASK = {'task': [icons.task_new, icons.task_reference],
              'callback': [icons.callback_new, icons.callback_reference],
              'method': [icons.method, icons.method]}

# shortcuts
SC_RELOAD = 'Ctrl+R'
SC_RUN_ALL = 'Ctrl+Shift+Space'
SC_RUN_PAUSE = 'Ctrl+Space'
SC_RELOAD_RUN = 'Ctrl+Shift+R'
SC_REMOVE = 'delete'
SC_DUPLICATE = 'Ctrl+D'
SC_EXPAND_COLLAPSE = 'CTRL+K'


# CLASS
class TreeWidget(QTreeWidget):
    """base class for TreeWidget"""
    SIGNAL_PROGRESS_INIT = Signal(int)
    SIGNAL_CLEAR = Signal()
    SIGNAL_EXECUTE = Signal()
    SIGNAL_ATTR_NAME = Signal(QTreeWidgetItem)
    SIGNAL_TASK_TYPE = Signal(QTreeWidgetItem)
    SIGNAL_GET_BUILDER = Signal()

    def __init__(self,  **kwargs):
        super(TreeWidget, self).__init__()

        self.item_runner = ItemRunner(self)
        self.stop = False
        self.pause = False
        self._expand = True
        self._display_items = []  # list of item display name to make sure no same name
        self._attr_items = []  # list of item attr name to make sure no same name
        self._change = False  # use to check if mouse is on checkbox or actual task
        self._pos = None  # save the mouse position when right click, so the task create window will pop up correct

        # get kwargs
        self._header = kwargs.get('header', ['Task', 'Pre', 'Build', 'Post'])
        self.builder = kwargs.get('builder', None)  # builder object

        # task folders
        self.task_folders = ['dev.rigging.task.core',
                             'dev.rigging.task.base',
                             'dev.rigging.task.test']

        header_item = QTreeWidgetItem(self._header)
        self.setHeaderItem(header_item)
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setHeaderHidden(True)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setStretchLastSection(False)
        self.setColumnWidth(1, 20)
        self.setColumnWidth(2, 20)
        self.setColumnWidth(3, 20)

        self.setSelectionMode(self.ExtendedSelection)
        self.setDragDropMode(self.InternalMove)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)

        self.setIconSize(QSize(25, 25))

        self._root = self.invisibleRootItem()

        # right clicked menu
        self.menu = QMenu(self)

        # execute
        self.menu_execute_sel = SubMenu('Execute Selection', parent=self.menu, shortcut=SC_RUN_PAUSE)

        self.menu_execute_all = SubMenu('Execute All', parent=self.menu, shortcut=SC_RUN_ALL)

        self.menu_rebuild = SubMenu('Rebuild', parent=self.menu, shortcut=SC_RELOAD_RUN)

        self.menu.addMenu(self.menu_execute_sel)
        self.menu.addMenu(self.menu_execute_all)
        self.menu.addMenu(self.menu_rebuild)

        self.action_reload = self.menu.addAction('Reload')
        self.action_reload.setShortcut(SC_RELOAD)

        self.menu.addSeparator()

        self.action_create = self.menu.addAction('Create')
        self.action_create.setShortcut('Ctrl+n')
        self.action_duplicate = self.menu.addAction('Duplicate')
        self.action_duplicate.setShortcut(SC_DUPLICATE)
        self.action_remove = self.menu.addAction('Remove')
        self.action_remove.setShortcut(SC_REMOVE)

        self.menu.addSeparator()

        self.action_display = self.menu.addAction('Display Name')
        self.action_color = self.menu.addAction('Display Color')
        self.action_color_text = self.menu.addAction('Text Color')
        self.action_color_reset = self.menu.addAction('Reset Color')

        self.menu.addSeparator()

        self.action_expand = self.menu.addAction('Expand/Collapse')
        self.action_expand.setShortcut(SC_EXPAND_COLLAPSE)

        # set enable/disable
        self._menu_widgets = [self.menu_execute_sel, self.menu_execute_all, self.action_duplicate, self.action_remove,
                              self.action_display, self.action_color, self.action_color_text, self.action_color_reset]

        for widget in self._menu_widgets:
            widget.setEnabled(False)

        # connect functions
        self.action_reload.triggered.connect(self.reload_tasks)
        self.menu_execute_sel.SIGNAL_SECTION.connect(self.run_sel_tasks)
        self.menu_execute_all.SIGNAL_SECTION.connect(self.run_all_tasks)
        self.menu_rebuild.SIGNAL_SECTION.connect(self.rebuild_tasks)

        self.action_duplicate.triggered.connect(self.duplicate_tasks)
        self.action_remove.triggered.connect(self.remove_tasks)

        self.action_display.triggered.connect(self.set_display_name)
        self.action_color.triggered.connect(self.set_display_color)
        self.action_color_text.triggered.connect(self.set_text_color)
        self.action_color_reset.triggered.connect(self.reset_display_color)

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

        super(TreeWidget, self).mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        # double click to run the task
        if self.indexAt(event.pos()).isValid():
            if not self._change:
                self.run_sel_tasks()

    def show_menu(self, pos):
        current_item = self.currentIndex().data()
        if not current_item:
            for widget in self._menu_widgets:
                widget.setEnabled(False)
        else:
            for widget in self._menu_widgets:
                widget.setEnabled(True)
            # disable duplicate and remove for in class method
            current_item = self.currentItem()
            task_type = current_item.data(0, ROLE_TASK_TYPE)
            inheritance = current_item.data(0, ROLE_TASK_INHERITANCE)
            if task_type == 'method' or inheritance:
                self.action_remove.setEnabled(False)
                if task_type == 'method':
                    self.action_duplicate.setEnabled(False)

        self._pos = self.mapToGlobal(pos)
        self.menu.move(self._pos)  # move menu to right clicked position

        self.menu.show()

    # task functions to connect with button and menu
    def run_sel_tasks(self, section=None):
        if section is None:
            section = ['pre_build', 'build', 'post_build']
        items = self.selectedItems()
        self._run_task(items=items, section=section)
        self.SIGNAL_EXECUTE.emit()

    def run_all_tasks(self, section=None):
        if section is None:
            section = ['pre_build', 'build', 'post_build']
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

    def pause_resume_tasks(self):
        self.pause = not self.pause

    def stop_tasks(self):
        self.stop = True

    def set_display_name(self):
        item = self.currentItem()
        current_name = item.text(0)
        text, ok = QInputDialog.getText(self, 'Display Name', 'Set Display Name', text=current_name)
        if text and ok and text != current_name:
            update_name = self._get_unique_name(current_name, text, self._displayItems)
            item.setText(0, update_name)

    def set_display_color(self):
        items = self.selectedItems()
        background_col = items[-1].background(0).color()
        col = QColorDialog.getColor(background_col, self, 'Display Color')
        if col.isValid():
            for item in items:
                items_collect = self._collect_items(item)
                for item_setCol in items_collect:
                    item_setCol.setBackground(0, col)

    def set_text_color(self):
        items = self.selectedItems()
        foreground_col = items[-1].foreground(0).color()
        col = QColorDialog.getColor(foreground_col, self, 'Text Color')
        if col.isValid():
            for item in items:
                items_collect = self._collect_items(item)
                for item_setCol in items_collect:
                    item_setCol.setForeground(0, col)

    def set_attr_name(self, name):
        title = "Change task's attribute name in the builder"
        # check if name already exists
        if name in self._attr_items:
            text = 'attribute name already exists'
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
                text = 'attribute name is illegal, must start with letter'
                QMessageBox.warning(self, title, text)
                return
            else:
                # set attr name
                item = self.currentItem()
                current_name = item.data(0, ROLE_TASK_NAME)
                set_item_data(attr_name=current_name)
                # remove previous name, add new name
                self._attr_items.remove(current_name)
                self._attr_items.append(name)
                # shoot signal to reset task info
                self.SIGNAL_ATTR_NAME.emit(item)

    def set_task_type(self, task_path):
        item = self.selectedItems()[0]

        task_path_orig = item.data(0, ROLE_TASK_PATH)
        # compare if changed
        if task_path != task_path_orig:
            # get obj
            # imported task, get task object
            task_import, task_function = modules.import_module(task_path)
            task = getattr(task_import, task_function)

            # kwargs
            if inspect.isfunction(task):
                # function, normally is callback
                task_kwargs = task_import.kwargs_ui.copy()  # get a copy of kwargs
            else:
                task_kwargs = task().kwargs_ui.copy()  # get a copy of kwargs

            kwargs_orig = item.data(0, ROLE_TASK_KWARGS)  # get original kwargs to see if any can be swapped
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

            set_item_data(item, task_path=task_path, task=task, task_kwargs=task_kwargs)

            # shoot signal to reset task info
            self.SIGNAL_TASK_TYPE.emit(item)

    def reset_display_color(self):
        items = self.selectedItems()
        for item in items:
            items_collect = self._collect_items(item)
            for item_setCol in items_collect:
                item_setCol.setData(0, Qt.BackgroundRole, None)
                item_setCol.setData(0, Qt.ForegroundRole, None)

    def duplicate_tasks(self):
        items = self.selectedItems()
        for item in items:
            # get item data
            display = item.text(0)
            attr_name = item.data(0, ROLE_TASK_NAME)
            task_path = item.data(0, ROLE_TASK_PATH)
            task = item.data(0, ROLE_TASK_FUNC)
            task_kwargs = item.data(0, ROLE_TASK_KWARGS)
            check = item.checkState(0)
            section = item.data(0, ROLE_TASK_SECTION)
            task_type = item.data(0, ROLE_TASK_TYPE)

            if task_type != 'method':
                display = self._get_unique_name('', display, self._display_items)
                attr_name = self._get_unique_name('', attr_name, self._attr_items)

                kwargs = {'display': display,
                          'attr_name': attr_name,
                          'task_path': task_path,
                          'task': task,
                          'task_kwargs': task_kwargs,
                          'check': check,
                          'section': section,
                          'inheritance': False}

                self._create_item(**kwargs)

    def remove_tasks(self):
        for item in self.selectedItems():
            # check type, can't delete in class method or task referenced from parented classes
            task_type = item.data(0, ROLE_TASK_TYPE)
            task_inheritance = item.data(0, ROLE_TASK_INHERITANCE)

            if task_type != 'method' and not task_inheritance:
                # re-parent child if any is method, and get remove list
                remove_items = self._re_parent_children(item=item)

                for itm in remove_items:
                    display = itm.text(0)
                    attr_name = itm.data(0, ROLE_TASK_NAME)

                    # remove names from list
                    if display in self._display_items:
                        self._display_items.remove(display)
                    if attr_name in self._attr_items:
                        self._attr_items.remove(attr_name)

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
        if self.builder:
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

    def export_current_builder(self):
        if self.builder:
            items = self._collect_items()
            export_data = []

            index_previous = 0
            for item in items:
                task = item.data(0, ROLE_TASK_NAME)
                display = item.text(0)
                task_kwargs = item.data(0, ROLE_TASK_KWARGS)
                task_path = item.data(0, ROLE_TASK_PATH)
                parent = item.parent()
                if parent:
                    parent = parent.text(0)
                else:
                    parent = ''
                export_data.append({task: {'display': display,
                                           'task_path': task_path,
                                           'task_kwargs': task_kwargs,
                                           'parent': parent,
                                           'index': index_previous}})
                index_previous = task

            # save data
            self.builder.export_tasks_info(export_data)

    def _add_child_item(self, item, data):
        for d in data:
            name = d.keys()[0]
            data_info = d[name]
            data_info.update({'attr_name': name})
            task_item = TaskItem(**data_info)

            display = task_item.text(0)  # get display name
            attr_name = task_item.data(0, ROLE_TASK_NAME)  # get attr name

            self._display_items.append(display)  # add to list for later check
            self._attr_items.append(attr_name)  # add to list for later check

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
            task_inheritance = itm.data(0, ROLE_TASK_INHERITANCE)
            if task_type == 'method' or task_inheritance:
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

    def _run_task(self, items=None, collect=True, section=None):
        """
        run task

        Keyword Args:
            items(QItem): None will be the root, default is None
            collect(bool): loop downstream tasks, default is True
            section(list): run for specific section, None will run for all, default is None
                           ['pre_build', 'build', 'post_build']
        """
        if section is None:
            section = ['pre_build', 'build', 'post_build']

        # reset value
        self.stop = False
        self.pause = False

        ignore_check = False

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
            if collect:
                items_run = self._collect_items(item=items)
                ignore_check = False
            else:
                items_run = [items]
                ignore_check = True

        # register in itemRunner
        self.item_runner.items = items_run
        self.item_runner.ignore_check = ignore_check
        self.item_runner.section = section

        # shoot signal to progress bar
        self.SIGNAL_PROGRESS_INIT.emit(len(items_run)*len(section))

        # start run tasks
        self.item_runner.start()

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
        print 'task_info'
        print task_info
        attr_name = task_info[0]
        display = task_info[1]
        task_path = task_info[2]

        # imported task, get task object
        task_import, task_function = modules.import_module(task_path)
        task = getattr(task_import, task_function)

        if inspect.isfunction(task):
            # function, normally is callback
            task_kwargs = task_import.kwargs_ui
        else:
            # task class
            task_obj = task()
            task_kwargs = task_obj.kwargs_ui

        attr_name = self._get_unique_name('', attr_name, self._attr_items)
        self._attr_items.append(attr_name)

        if not display:
            display = attr_name
        display = self._get_unique_name('', display, self._display_items)
        self._display_items.append(display)

        kwargs = {'display': display,
                  'attr_name': attr_name,
                  'task_path': task_path,
                  'task': task,
                  'task_kwargs': task_kwargs,
                  'check': Qt.Checked,
                  'inheritance': False}

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

    def task_create_window_open(self):
        # try close window in case it's opened
        self.task_create_window.close()
        self.task_create_window.refresh_widgets()
        self.task_create_window.widget_task_creation.rebuild_list_model(self.task_folders)
        self.task_create_window.move(self._pos)
        self.task_create_window.show()

    def task_switch_window_open(self, pos):
        # try close window in case it's opened
        self.task_switch_window.close()

        # check if task is referenced or in class method
        item = self.selectedItems()[0]
        # check if item is referenced
        inheritance = item.data(0, ROLE_TASK_INHERITANCE)
        task_type_orig = item.data(0, ROLE_TASK_TYPE)
        title = "Change task's type"
        if task_type_orig == 'method':
            text = "task is a in-class method, can't switch type"
            QMessageBox.warning(self, title, text)
            return
        elif inheritance:
            text = "task is inherited from parent class, can't switch type"
            QMessageBox.warning(self, title, text)
            return
        else:
            self.task_switch_window.refresh_widgets()
            self.task_switch_window.widget_task_creation.rebuild_list_model(self.task_folders)
            self.task_switch_window.move(pos)
            self.task_switch_window.show()

    @staticmethod
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


class TaskItem(QTreeWidgetItem):
    def __init__(self, **kwargs):
        super(TaskItem, self).__init__()

        display = kwargs.get('display', 'task1')
        attr_name = kwargs.get('attr_name', 'task1')
        task_path = kwargs.get('task_path', '')
        task = kwargs.get('task', None)
        task_kwargs = kwargs.get('task_kwargs', {})
        check = kwargs.get('check', Qt.Checked)
        section = kwargs.get('section', '')
        inheritance = kwargs.get('inheritance', False)

        set_item_data(self, display=display, attr_name=attr_name, task_path=task_path, task=task,
                      task_kwargs=task_kwargs, section=section, inheritance=inheritance)

        self.setData(0, ROLE_TASK_PRE, 0)
        self.setData(0, ROLE_TASK_RUN, 0)
        self.setData(0, ROLE_TASK_POST, 0)

        self.setFlags(self.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        self.setCheckState(0, check)

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


class ItemRunner(QThread):
    """
    QThread to run items one by one

    use multi-threading so the ui won't be frozen,
    and can be stopped anytime
    """
    SIGNAL_PROGRESS = Signal(int)  # emit signal to update progress bar
    SIGNAL_ERROR = Signal()  # emit signal for error
    SIGNAL_PAUSE = Signal()  # emit signal to pause

    def __init__(self, parent):
        super(ItemRunner, self).__init__(parent)
        self._parent = parent
        self.items = []
        self.ignore_check = False
        self.section = ['pre_build', 'build', 'post_build']
        self._roles = {'pre_build': ROLE_TASK_PRE,
                       'build': ROLE_TASK_RUN,
                       'post_build': ROLE_TASK_POST}

    def run(self):
        self.run_task()

    def run_task(self):
        # disable treeWidget when running
        self._parent.setEnabled(False)

        item_count = float(len(self.items))
        for i, section in enumerate(self.section):
            role = self._roles[section]
            for j, item in enumerate(self.items):
                if self._parent.pause:
                    self.SIGNAL_PAUSE.emit()

                while self._parent.pause:
                    # in case need to be stopped from pause
                    if self._parent.stop:
                        self._parent.pause = False
                    self.sleep(1)  # pause the process

                # check if need to be stopped
                if self._parent.stop:
                    break

                self._run_task_on_single_item(item, ignore_check=self.ignore_check, section=section, role=role)

                # emit signal
                self.SIGNAL_PROGRESS.emit(item_count*i + j + 1)

            if self._parent.stop:
                # emit signal if need stop
                self.SIGNAL_ERROR.emit()
                logger.warn('Task process is stopped by the user')
                self._parent.setEnabled(True)  # enable back widget if error
                break

        self._parent.setEnabled(True)  # enable back widget when finished

    def _run_task_on_single_item(self, item, ignore_check=False, section='pre_build', role=ROLE_TASK_PRE):
        # get attributes from item
        display = item.text(0)
        name = item.data(0, ROLE_TASK_NAME)
        task = item.data(0, ROLE_TASK_FUNC)
        kwargs = item.data(0, ROLE_TASK_KWARGS)
        check_state = item.checkState(0)

        kwargs_run = {}
        for key, data in kwargs.iteritems():
            if 'value' in data and data['value'] is not None:
                val = data['value']
            else:
                val = data['default']
            kwargs_run.update({key: val})

        if not ignore_check and check_state != Qt.Checked:
            # skip unchecked task
            return

            # get section status, if already run, skipped
        task_return = item.data(0, role)

        if task_return > 0:
            # skip, task already run
            return

        # check if registered function is a method
        if inspect.ismethod(task):
            # get section registered
            section_init = item.data(0, ROLE_TASK_SECTION)

            if section != section_init:
                # skip
                item.setData(0, role, 1)
            else:
                # try to run function
                try:
                    maya.utils.executeInMainThreadWithResult(task, kwargs_run[section])

                    self._execute_setting(item, 1, 'method', display, role, section)

                except Exception as exc:
                    self._error_setting(item, exc, role)

        # check if registered function is a function (mainly for callback)
        elif inspect.isfunction(task):
            # try to run function
            try:
                if kwargs_run[section]:
                    maya.utils.executeInMainThreadWithResult(task, kwargs_run[section])

                self._execute_setting(item, 1, 'function', display, role, section)

            except Exception as exc:
                self._error_setting(item, exc, role)

        else:
            # Task is an imported task
            # try to run task
            try:
                if not hasattr(self._parent.builder, name):
                    # normally because it is just created in ui
                    # get obj
                    task_obj = task()
                    # attach obj to builder
                    setattr(self._parent.builder, name, task_obj)
                else:
                    task_obj = getattr(self._parent.builder, name)

                if section == 'pre_build':
                    for key, val in kwargs_run.iteritems():
                        setattr(task_obj, key, val)

                # run task
                func = getattr(task_obj, section)
                maya.utils.executeInMainThreadWithResult(func)
                return_signal = task_obj.signal

                self._execute_setting(item, return_signal, 'task', display, role, section)

            except Exception as exc:
                self._error_setting(item, exc, role)

    def _error_setting(self, item, exc, role):
        # error raises
        item.setData(0, role, 3)
        # emit error signal
        self.SIGNAL_ERROR.emit()
        self._parent.setEnabled(True)  # enable back widget if error
        logger.error(exc)
        raise

    @ staticmethod
    def _execute_setting(item, task_return, function_name, display, role, section):
        if task_return == 2:
            # warning raises
            item.setData(0, role, 2)
        else:
            # run successfully
            item.setData(0, role, 1)

        # log
        logger.info('[{}] -- Run {} "{}" successfully'.format(section, function_name, display))


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
        self.task_name.setText('')
        self.task_display.setText('')
        self.widget_task_creation.filter.setText('')
        self.setFocus()

    def _get_select_task(self):
        name = self.task_name.text()
        display = self.task_display.text()
        task = self.widget_task_creation.listView.currentIndex().data()

        if name and task:
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

        if task:
            self.SIGNAL_TASK_SWITCH.emit(task)

        self.close()


# SUB FUNCTION
def set_item_data(item, **kwargs):
    """
    set TaskItem's data

    Args:
        item(TaskItem): task item object

    Keyword Args:
        display(str): display name
        attr_name(str): attr name will be used in the builder
        task_path(str): task's full path
        task(object): task
        task_kwargs(dict): task ui kwargs
        section(str): register to specific section, normally for in-class method
        inheritance(bool): if the task is inherited from parent class
    """
    display = kwargs.get('display', None)
    attr_name = kwargs.get('attr_name', None)
    task_path = kwargs.get('task_path', None)
    task = kwargs.get('task', None)
    task_kwargs = kwargs.get('task_kwargs', None)
    section = kwargs.get('section', None)
    inheritance = kwargs.get('inheritance', None)

    if display is not None:
        item.setText(0, display)

    if attr_name is not None:
        item.setData(0, ROLE_TASK_NAME, attr_name)

    if task_path is not None:
        item.setData(0, ROLE_TASK_PATH, task_path)

    if section is not None:
        item.setData(0, ROLE_TASK_SECTION, section)

    if inheritance is not None:
        item.setData(0, ROLE_TASK_INHERITANCE, inheritance)

    if task is not None:
        item.setData(0, ROLE_TASK_FUNC, task)
        if inspect.ismethod(task):
            item.setData(0, ROLE_TASK_TYPE, 'method')
        elif inspect.isfunction(task):
            item.setData(0, ROLE_TASK_TYPE, 'callback')
        else:
            item.setData(0, ROLE_TASK_TYPE, task_path)  # normally user will given task_path and task together
        task_type = item.data(0, ROLE_TASK_TYPE)
        if task_type not in ICONS_TASK:
            task_type = 'task'  # in case no specific icon
        if inheritance is None:
            inheritance = 0
        item.setIcon(0, QIcon(ICONS_TASK[task_type][inheritance]))

    if task_kwargs is not None:
        item.setData(0, ROLE_TASK_KWARGS, task_kwargs)
        item.setData(0, ROLE_TASK_KWARGS_KEY, task_kwargs.keys())


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