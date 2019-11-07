# IMPORT PACKAGES

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

# import json
import json

# import ast
import ast

# import OrderedDict
from collections import OrderedDict

# import maya
import maya.cmds as cmds

# CONSTANT
import dev.rigging.task.config.PROPERTY_ITEMS as PROPERTY_ITEMS

PROPERTY_ITEMS = PROPERTY_ITEMS.PROPERTY_ITEMS

ROLE_TASK_INFO = Qt.UserRole + 1

ROLE_ITEM_KWARGS = Qt.UserRole + 2  # this role hold each property's ui kwargs

COLOR_WARN = QColor(255, 0, 0)


#  CLASS
class PropertyEditor(QTreeView):
    """base class for PropertyEditor"""

    def __init__(self):
        super(PropertyEditor, self).__init__()
        self._property = []
        self._size = QSize(20, 20)
        self._item = None  # store property item for further use

        self.setFocusPolicy(Qt.NoFocus)
        # different color each row
        self.setAlternatingRowColors(True)
        # show header so user can adjust the first column width
        self.setHeaderHidden(False)
        # last section stretch
        self.header().setStretchLastSection(True)

        # QStandardItemModel
        self._model = QStandardItemModel(0, 2)
        self._model.setHeaderData(0, Qt.Horizontal, 'Properties')
        self._model.setHeaderData(1, Qt.Horizontal, '')
        self.setModel(self._model)

        # delegate
        delegate = PropertyDelegate(self)
        delegate.SIGNAL_UPDATE_PARENT.connect(self._update_parent)
        delegate.SIGNAL_REBUILD_CHILD.connect(self._rebuild_child)

        self.setItemDelegate(delegate)

        # right click menu
        self.menu = QMenu()
        self.action_reset = self.menu.addAction('Reset Value')
        self.menu.addSeparator()
        self.action_set_select = self.menu.addAction('Set Selection')
        self.action_add_select = self.menu.addAction('Add Selection')
        self.menu.addSeparator()
        self.action_add_element = self.menu.addAction('Add Element')
        self.action_del_element = self.menu.addAction('Remove Element')
        self.action_dup_element = self.menu.addAction('Duplicate Element')

        for action in [self.action_set_select, self.action_add_select, self.action_add_element, self.action_del_element,
                       self.action_dup_element]:
            action.setEnabled(False)

        # connect function
        self.action_reset.triggered.connect(self._reset_value)
        self.action_set_select.triggered.connect(self._set_selection)
        self.action_add_select.triggered.connect(self._add_selection)
        self.action_add_element.triggered.connect(self._add_element)
        self.action_del_element.triggered.connect(self._del_element)
        self.action_dup_element.triggered.connect(self._dup_element)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

    def keyPressEvent(self, event):
        pass

    def init_property(self, item):
        """
        initialize property

        Args:
            item(QTreeWidgetItem): given task item
        """

        self._item = item  # store the given task item
        self.refresh()  # refresh the widget

        # get task info
        task_info = item.data(0, ROLE_TASK_INFO)
        # get kwargs and keys
        task_kwargs = task_info['task_kwargs']
        task_kwargs_keys = task_info['task_kwargs_keys']

        # loop in each key, get value and ui info
        for key in task_kwargs_keys:
            kwarg_data = task_kwargs[key]

            # add row item
            row_items = self._add_row_item(key, item_kwargs=kwarg_data, key_edit=False)
            # add row item function
            self._model.appendRow(row_items)

            # loop downstream
            # add child
            self._add_child(row_items)

    def refresh(self):
        self.setEnabled(True)
        self._model.clear()
        self._model = QStandardItemModel(0, 2)
        self._model.setHeaderData(0, Qt.Horizontal, 'Properties')
        self._model.setHeaderData(1, Qt.Horizontal, '')
        self.setModel(self._model)

    def _add_row_item(self, key, val=None, item_kwargs=None, key_edit=False):
        """
        add row for property
        Args:
            key(str): property name
        Keyword Args:
            val: property default value
            item_kwargs(dict): property item's ui kwargs
            key_edit(bool): if the key name can be changed by user, normally used for sth like adding space
        Returns:
            row_items(list): key_item, value_item
        """
        if item_kwargs is None:
            item_kwargs = {}

        # get custom, if custom set to True, enable key edit
        custom = item_kwargs.get('custom', False)
        if custom:
            key_edit = True

        # column 1: property name
        column_key = QStandardItem(key)

        # set editable if key_edit
        if key_edit:
            column_key.setEditable(True)
        else:
            column_key.setEditable(False)

        column_key.setData(self._size, role=Qt.SizeHintRole)  # set column size

        # add ui kwargs info from template in case sth missing
        # check property type
        if 'type' in item_kwargs and item_kwargs['type'] is not None:
            item_type = item_kwargs['type']
            # check item type if not in template list
            if not isinstance(item_type, basestring) or item_type not in PROPERTY_ITEMS:
                item_type = check_item_type(item_type)
            item_kwargs_template = PROPERTY_ITEMS[item_type].copy()  # make a copy so the config won't be changed
            item_kwargs_template.update(item_kwargs)  # override the keys from the item
            item_kwargs = item_kwargs_template

        # column 2: value
        if val is not None:
            item_kwargs.update({'value': val})  # override the value

        column_val = PropertyItem(data_info=item_kwargs)  # create property item with given item kwargs info

        # set height, normally for call back
        if 'height' in item_kwargs:
            size = QSize(self._size.width(), item_kwargs['height'])  # get size with given height
            column_key.setData(size, role=Qt.SizeHintRole)

        return [column_key, column_val]

    def _add_child(self, items):
        """
        add child items to the given item, only for list or dictionary data

        Args:
            items(list): a list contain key column item and value column item
        """
        # get value item data
        val_item = items[1]
        val_data = val_item.data(ROLE_ITEM_KWARGS)

        # get value
        # user's value change will be saved in value, use default if no value set
        val = val_data.get('value', None)
        if val is None:
            val = val_data['default']

        # get template
        template = val_data.get('template', None)

        # get custom
        custom = val_data.get('custom', False)

        # check value's type
        if isinstance(val, list):
            # loop in each item in list
            for i, v in enumerate(val):
                # try to get value's type from template
                attr_type = None
                if template:
                    if isinstance(template, list) and template:
                        # each value has specific attr type
                        attr_type = check_item_type(template[i])
                    elif not isinstance(template, list) or not template:
                        # all values has the same type
                        attr_type = check_item_type(template)

                # get attr_kwargs from attr_type
                if attr_type:
                    attr_kwargs = PROPERTY_ITEMS[attr_type].copy()
                else:
                    attr_kwargs = {}

                # override custom
                if custom:
                    attr_kwargs.update({'custom': True})

                # create row items
                items_add = self._add_row_item(str(i), val=v, item_kwargs=attr_kwargs)

                # add row attached to key column item
                items[0].appendRow(items_add)

                # loop downstream
                self._add_child(items_add)

        elif isinstance(val, dict):
            # get key order
            keys_order = val_data.get('keys_order', [])
            if not keys_order:
                keys_order = val.keys()

            # get key edit
            key_edit = val_data.get('key_edit', False)

            # loop in each key
            for k in keys_order:
                v = val[k]  # get key's value
                # try to get value's type from template
                attr_type = None
                if template:
                    if isinstance(template, dict) and k in template:
                        # key's value has a specific attr type
                        attr_type = check_item_type(template[k])
                    elif not isinstance(template, dict) or not template:
                        # all keys have some attr type
                        attr_type = check_item_type(template)
                # get attr kwargs from attr type
                if attr_type:
                    attr_kwargs = PROPERTY_ITEMS[attr_type].copy()
                else:
                    attr_kwargs = {}

                # override custom
                if custom:
                    attr_kwargs.update({'custom': True})

                # create row items
                items_add = self._add_row_item(k, val=v, item_kwargs=attr_kwargs, key_edit=key_edit)

                # add row attached to key column item
                items[0].appendRow(items_add)

                # loop downstream
                self._add_child(items_add)

    def _update_parent(self, item):
        """
        update parent item's value until reach the root level,
        then save the value back to the task item in task tree

        Args:
            item: property item
        """
        # get parent column key item
        parent = item.parent()
        if parent:
            # get parent column key item's index
            index_parent = parent.index()

            # get parent column value item's index
            index_value = self._model.index(parent.row(), 1, parent=index_parent.parent())

            # get value converted from string
            value = convert_data(self._model.data(index_value))

            # get children row count
            row_children = parent.rowCount()

            # create empty container for update val, can only be list or dict, others won't have child row
            if isinstance(value, list):
                value_collect = []
            else:
                value_collect = {}

            # loop in each row
            for i in range(row_children):
                index_attr = self._model.index(i, 0, parent=index_parent)
                index_val = self._model.index(i, 1, parent=index_parent)
                key = convert_data_to_str(self._model.data(index_attr))  # get key
                val = convert_data(self._model.data(index_val))  # get value
                if isinstance(value, list):
                    value_collect.append(val)
                else:
                    value_collect.update({key: val})

            # assign data
            if value != value_collect:
                # only assign data if the value changed
                self._model.setData(index_value, convert_data_to_str(value_collect))

            # loop to upper level
            self._update_parent(self._model.itemFromIndex(index_parent))
        else:
            # no parent item need to update, this is the root level
            # we need to get the value and save out the data to the task item in task tree
            index_key = self._model.index(item.row(), 0, parent=item.index().parent())  # current item's key index
            index_value = self._model.index(item.row(), 1, parent=item.index().parent())  # current item's value index
            item_data = self._model.itemFromIndex(index_value)  # current item
            key = self._model.data(index_key)  # key name
            val = convert_data(item_data.text())  # data value

            item_kwargs = item_data.data(role=ROLE_ITEM_KWARGS)  # get ui kwargs for current item
            item_kwargs.update({'value': val})  # override ui kwargs's value to the current value
            item_data.setData(item_kwargs, ROLE_ITEM_KWARGS)  # save ui kwargs

            task_info = self._item.data(0, ROLE_TASK_INFO)  # get task info
            task_info['task_kwargs'][key]['value'] = val  # override task value
            self._item.setData(0, ROLE_TASK_INFO, task_info)  # set back to task item

    def _rebuild_child(self, item):
        """
        rebuild children items

        Args:
            item: property item
        """
        index_value = item.index()  # get column value item's index
        index_key = self._model.index(item.row(), 0, parent=index_value.parent())  # get column key item's index

        # get value
        value = convert_data(self._model.data(index_value))  # convert data from string

        if isinstance(value, list) or isinstance(value, dict):
            # only list and value has child
            key_item = self._model.itemFromIndex(index_key)  # get key item from key index

            # clear out the children, we need to rebuild them
            rows = key_item.rowCount()
            key_item.removeRows(0, rows)

            # rebuild children
            self._add_child([key_item, item])

    def _show_menu(self, pos):
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)
        column = item.column()  # get item's column
        if column > 0:
            # only show menu if mouse on value column, key column is 0, values is 1

            # get mouse position map to global, and move menu there
            pos = self.viewport().mapToGlobal(pos)
            self.menu.move(pos)

            item_kwargs = item.data(role=ROLE_ITEM_KWARGS)  # get item kwargs

            # check if it has select set True
            select = item_kwargs.get('select', False)

            # get default value, list can add selection
            val_default = item_kwargs.get('default', None)
            if isinstance(val_default, list):
                add_select = True
            else:
                add_select = False

            self.action_set_select.setEnabled(select)
            self.action_add_select.setEnabled(select*add_select)

            # get template, set add element to True if has template in it
            template = item_kwargs.get('template', None)
            if template is not None:
                self.action_add_element.setEnabled(True)
            else:
                self.action_add_element.setEnabled(False)

            # check if item has parent item (if it's part of list/dict)
            parent = item.parent()
            if parent:
                # get column key item's index
                index_parent = parent.index()

                # get column value item's index
                index_value = self._model.index(parent.row(), 1, parent=index_parent.parent())

                # get parent column value item
                item_value = self._model.itemFromIndex(index_value)

                parent_item_kwargs = item_value.data(role=ROLE_ITEM_KWARGS)
                parent_template = parent_item_kwargs.get('template', None)
                if parent_template is not None:
                    # parent item has template, means the children items are editable, can be remove or duplicate
                    self.action_del_element.setEnabled(True)
                    self.action_dup_element.setEnabled(True)
                else:
                    self.action_del_element.setEnabled(False)
                    self.action_dup_element.setEnabled(False)
            else:
                self.action_del_element.setEnabled(False)
                self.action_dup_element.setEnabled(False)

            # get custom, set add/dup/del element to True if set to custom
            custom = item_kwargs.get('custom', False)
            if custom:
                self.action_add_element.setEnabled(True)
                self.action_dup_element.setEnabled(True)
                self.action_del_element.setEnabled(True)

            self.menu.show()

    def _reset_value(self):
        """
        reset value to default (default is the value from last time saved the build script)
        """
        # the index can only be column value item's index, otherwise reset value menu won't show up
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)  # get column value item
        item_kwargs = item.data(role=ROLE_ITEM_KWARGS)
        value = item_kwargs['default']
        item.setText(convert_data_to_str(value))

        # we need to update parent first, because it will save the value back to item
        # rebuild child will need the value from item, not from the text,
        # this way we can keep the value type more consistent
        self._update_parent(item)
        self._rebuild_child(item)

    def _set_selection(self):
        """
        set selected nodes as attr
        """
        # the index can only be column value item's index, otherwise set selection menu won't show up
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)  # get column value item

        sel = cmds.ls(selection=True)  # get selection

        item_kwargs = item.data(role=ROLE_ITEM_KWARGS)  # get item kwargs
        # check if it is a list or string
        if isinstance(item_kwargs['default'], basestring):
            # item is string, set to the first select node, or empty string
            if sel:
                val = sel[0]
            else:
                val = ''
            item.setText(convert_data_to_str(val))
            # update parent item and save back to task item
            self._update_parent(item)
        else:
            # item is list
            item.setText(convert_data_to_str(sel))

            # we need to update parent first, because it will save the value back to item
            # rebuild child will need the value from item, not from the text,
            # this way we can keep the value type more consistent

            # update parent item and save back to task item
            self._update_parent(item)
            # update child
            self._rebuild_child(item)

    def _add_selection(self):
        """
        add selected nodes to attr
        """
        # the index can only be column value item's index, otherwise add selection menu won't show up
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)

        val = item.text()
        # convert value
        val = convert_data(val)
        # get selection
        sel = cmds.ls(selection=True)
        # add selection
        if sel:
            val += sel
            val = list(OrderedDict.fromkeys(val))
            item.setText(convert_data_to_str(val))
            # we need to update parent first, because it will save the value back to item
            # rebuild child will need the value from item, not from the text,
            # this way we can keep the value type more consistent
            self._update_parent(item)
            self._rebuild_child(item)

    def _add_element(self):
        """
        add element to list or dict
        """
        # the index can only be column value item's index, otherwise add element menu won't show up
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)

        val = item.text()
        # convert value
        val = convert_data(val)

        # get template
        item_kwargs = item.data(role=ROLE_ITEM_KWARGS)

        if isinstance(val, list):
            append_val = ''
            # get template
            template = item_kwargs.get('template', None)
            if template is not None:
                if isinstance(template, basestring) and template in PROPERTY_ITEMS:
                    # get value from PROPERTY_ITEMS
                    append_val = PROPERTY_ITEMS[template]['default']
                else:
                    # check template type and get info from PROPERTY_ITEMS
                    template_type = check_item_type(template)
                    append_val = PROPERTY_ITEMS[template_type]['default']

            # append to list
            val.append(append_val)
        else:
            # dict attr
            # check if has key
            if val.keys():
                # get the latest key, make a copy
                key = val.keys()[-1] + '_copy'
                append_val = val[val.keys()[-1]]
            else:
                append_val = ''
                # get template
                template = item_kwargs.get('template', None)
                if template is not None:
                    if isinstance(template, basestring) and template in PROPERTY_ITEMS:
                        # get value from PROPERTY_ITEMS
                        append_val = PROPERTY_ITEMS[template]['default']
                    else:
                        # check template type and get info from PROPERTY_ITEMS
                        template_type = check_item_type(template)
                        append_val = PROPERTY_ITEMS[template_type]['default']
                key = 'key'

            val.update({key: append_val})

        item.setText(convert_data_to_str(val))

        # we need to update parent first, because it will save the value back to item
        # rebuild child will need the value from item, not from the text,
        # this way we can keep the value type more consistent
        self._update_parent(item)
        self._rebuild_child(item)

    def _dup_element(self):
        """
        duplicate current item
        """
        # the index can only be column value item's index, otherwise duplicate element menu won't show up
        # get current item and current value
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)
        val = convert_data(item.text())

        # get parent info
        parent_info = self._get_parent_item_info_from_current_index()
        parent_val_item = parent_info[0]
        parent_val = parent_info[1]
        parent_key_index = parent_info[2]

        if isinstance(parent_val, list):
            parent_val.append(val)
        else:
            # parent value is dict
            # get key
            key_index = self._model.index(item.row(), 0, parent=parent_key_index)  # get key index
            key = convert_data(self._model.data(key_index))  # get key name
            parent_val.update({key + '_copy': val})

        # set the update value to parent item, let update parent/rebuild child do the rest work
        parent_val_item.setText(convert_data_to_str(parent_val))

        # we need to update parent first, because it will save the value back to item
        # rebuild child will need the value from item, not from the text,
        # this way we can keep the value type more consistent
        self._update_parent(parent_val_item)
        self._rebuild_child(parent_val_item)

        self.setCurrentIndex(index)  # set back selection

    def _del_element(self):
        """
        delete current item
        """
        # the index can only be column value item's index, otherwise remove element menu won't show up
        # get current item and current value
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)
        val = convert_data(item.text())

        # get parent info
        parent_info = self._get_parent_item_info_from_current_index()
        parent_val_item = parent_info[0]
        parent_val = parent_info[1]
        parent_key_index = parent_info[2]

        if isinstance(parent_val, list):
            parent_val.remove(val)
        else:
            # get key
            key_index = self._model.index(item.row(), 0, parent=parent_key_index)  # get key index
            key = convert_data(self._model.data(key_index))
            parent_val.pop(key)  # remove key

        # set the update value to parent item, let update parent/rebuild child do the rest work
        parent_val_item.setText(convert_data_to_str(parent_val))

        # we need to update parent first, because it will save the value back to item
        # rebuild child will need the value from item, not from the text,
        # this way we can keep the value type more consistent
        self._update_parent(parent_val_item)
        self._rebuild_child(parent_val_item)

        self.setCurrentIndex(QModelIndex())  # clear current selection

    def _get_parent_item_info_from_current_index(self):
        """
        Returns:
            parent_item, parent_val, parent_key_index, parent_val_index
        """
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)

        # get parent val
        parent = item.parent()
        parent_key_index = parent.index()  # parent column key item's index

        # parent column value item's index
        parent_val_index = self._model.index(parent.row(), 1, parent=parent_key_index.parent())

        # get parent value item
        parent_val_item = self._model.itemFromIndex(parent_val_index)

        # get value
        parent_val = convert_data(parent_val_item.text())

        return [parent_val_item, parent_val, parent_key_index, parent_val_index]


class PropertyDelegate(QItemDelegate):
    """
    base class for PropertyDelegate
    PropertyDelegate will create the correct widget base on property type
    """
    SIGNAL_UPDATE_PARENT = Signal(QStandardItem)
    SIGNAL_REBUILD_CHILD = Signal(QStandardItem)

    def __init__(self, parent=None):
        super(PropertyDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        item = index.model().itemFromIndex(index)

        item_kwargs = item.data(role=ROLE_ITEM_KWARGS)

        value = index.data()

        if item_kwargs:
            custom = item_kwargs.get('custom', False)
            if not custom:
                widget = item_kwargs['widget'](parent)  # get widget from kwargs
            else:
                widget = QLineEdit(parent)  # use QLineEdit
        else:
            widget = QLineEdit(parent)  # use QLineEdit as general widget

        # extra setting
        if isinstance(widget, QComboBox):
            # set enum
            widget.addItems(item_kwargs['enum'])  # add enum options
            enum_index = widget.findText(value, Qt.MatchFixedString)  # get default index
            widget.setCurrentIndex(enum_index)  # set default

        elif isinstance(widget, QDoubleSpinBox) or isinstance(widget, QSpinBox):
            # set range
            if 'min' in item_kwargs and item_kwargs['min'] is not None:
                widget.setMinimum(item_kwargs['min'])
            if 'max' in item_kwargs and item_kwargs['max'] is not None:
                widget.setMaximum(item_kwargs['max'])

        elif isinstance(widget, QLineEdit):
            widget.setFrame(False)

        return widget

    def setModelData(self, editor, model, index):
        item = index.model().itemFromIndex(index)
        # get previous value
        value = item.text()

        # get data info
        item_kwargs = item.data(role=ROLE_ITEM_KWARGS)

        # get custom
        custom = item_kwargs.get('custom', False)

        # set data
        super(PropertyDelegate, self).setModelData(editor, model, index)

        # I think this is for dictionary's key if the key is editable,
        # key column doesn't contain item kwargs, we can just go back update the parents
        # if not item_kwargs:
        #     # shoot rebuild signal
        #     self.SIGNAL_UPDATE_PARENT.emit(item)
        #     return
        column = item.column()  # get item's column
        if column == 0:
            # this is the key name change for dictionary, no need to compare input type
            # shoot rebuild signal and update the parents
            self.SIGNAL_UPDATE_PARENT.emit(item)
            return

        # if it's string/list/dict, compare with the previous value
        # because we need to stick with the value type, and these three are all converted from string
        # if we don't do the compare, user may change the string to list by typing mistake
        # will skip check if it's set to custom, user will need to keep the kwargs consistent
        if isinstance(editor, QLineEdit) and not custom:
            # get default value
            value_default = item_kwargs['default']
            # get changed value
            value_change = item.text()
            # convert value
            value_change = convert_data(value_change)

            # if string and changed value is not
            if isinstance(value_default, basestring) and not isinstance(value_change, basestring):
                # change back to previous
                item.setText(value)
            # if list
            elif isinstance(value_default, list):
                if isinstance(value_change, list):
                    # shoot signal
                    self.SIGNAL_REBUILD_CHILD.emit(item)
                else:
                    # change back to previous
                    item.setText(value)

            # if dict
            elif isinstance(value_default, dict):
                if isinstance(value_change, dict):
                    # shoot signal
                    self.SIGNAL_REBUILD_CHILD.emit(item)
                else:
                    # change back to previous
                    item.setText(value)

        # check if the value is unskippable, set background color if no value with skippable set to False
        skippable = item_kwargs.get('skippable', True)

        if not skippable:
            value = convert_data(item.text())  # get current item value converted
            if not value:
                item.setData(COLOR_WARN, Qt.BackgroundRole)
            else:
                item.setData(None, Qt.BackgroundRole)
        else:
            item.setData(None, Qt.BackgroundRole)

        # shoot rebuild signal
        self.SIGNAL_UPDATE_PARENT.emit(item)


class PropertyItem(QStandardItem):
    """
    base class for PropertyItem
    PropertyItem register all the data info into QStandardItem
    so it can be query or recreate later
    especially for list and dictionary,
    it hold the template to add items
    """

    def __init__(self, data_info=None):
        super(PropertyItem, self).__init__()

        if data_info is None:
            data_info = {}

        self._data_info = data_info
        self._set_data()

    def _set_data(self):
        # get default value
        val = self._data_info.get('value', None)
        if val is None:
            val = self._data_info['default']

        val_str = convert_data_to_str(val)  # convert value to str to display

        self.setText(val_str)  # set default value

        # add tool tip if has in kwargs
        if 'hint' in self._data_info and self._data_info['hint']:
            self.setData(self._data_info['hint'], Qt.ToolTipRole)

        # check if value is unskippable,
        # set background to red if no value but unskip so user can be aware
        skippable = self._data_info.get('skippable', True)
        if not skippable and not val:
            self.setData(COLOR_WARN, Qt.BackgroundRole)

        # store all ui kwargs in data
        self.setData(self._data_info, role=ROLE_ITEM_KWARGS)


# FUNCTION
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


def check_item_type(item_value):
    if isinstance(item_value, basestring):
        if item_value in PROPERTY_ITEMS:
            item_type = item_value
        else:
            item_type = 'str'
    elif isinstance(item_value, float):
        item_type = 'float'
    elif isinstance(item_value, int):
        item_type = 'int'
    elif isinstance(item_value, bool):
        item_type = 'bool'
    elif isinstance(item_value, list):
        item_type = 'list'
    elif isinstance(item_value, dict):
        item_type = 'dict'
    else:
        item_type = None
    return item_type
