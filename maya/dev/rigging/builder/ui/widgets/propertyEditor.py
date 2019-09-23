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

ROLE_ITEM_KWARGS = Qt.UserRole + 1
ROLE_TASK_KWARGS = Qt.UserRole + 4
ROLE_TASK_KWARGS_KEY = Qt.UserRole + 5


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

        # get item's ui kwargs
        data_property = item.data(0, ROLE_TASK_KWARGS)
        # get ui kwargs's key, because dictionary doesn't have order
        data_property_keys = item.data(0, ROLE_TASK_KWARGS_KEY)

        for key in data_property_keys:
            # loop in each key, get parameters for each key
            data = data_property[key]
            # add row item
            row, template_child, key_edit, keys_order = self._add_row_item(key, item_kwargs=data, key_edit=False)

            # add row
            self._model.appendRow(row)

            # loop downstream
            # get value, user edit will be saved in value, use default if no value
            if 'value' in data and data['value'] is not None:
                val = data['value']
            else:
                val = data['default']
            self._add_child(row[0], val, template=template_child, key_edit=key_edit, keys_order=keys_order)

    def refresh(self):
        self.setEnabled(True)
        self._model.clear()
        self._model = QStandardItemModel(0, 2)
        self._model.setHeaderData(0, Qt.Horizontal, 'Properties')
        self._model.setHeaderData(1, Qt.Horizontal, '')
        self.setModel(self._model)

    def _add_child(self, item, data, template=None, key_edit=False, keys_order=None):
        """
        add child items to the given item, only for list or dictionary data

        Args:
            item(QStandardItem)
            data: item's value

        Keyword Args:
            template(dict): item's template info, used for add item for list/dict item
            key_edit(bool): if key is editable, only used for dict item
            keys_order(list): if dictionary's keys need to be showed in order
        """

        if isinstance(data, list):
            template_type = check_item_type(template)  # get template's type
            # loop in each item in list
            for i, val in enumerate(data):
                # add row for each item in list
                row, template_child, key_edit, keys_order = self._add_row_item(str(i), val=val,
                                                                               item_kwargs={'type': template_type})

                # add row
                item.appendRow(row)

                # loop downstream
                self._add_child(row[0], val, template=template_child, keys_order=keys_order)

        elif isinstance(data, dict):
            if not keys_order:
                # key order will be dictionary's default key order
                keys_order = data.keys()
            for key in keys_order:
                val = data[key]
                attr_type = None  # check template's attribute type
                if template:
                    if not isinstance(template, dict):
                        # all keys have same attribute type
                        attr_type = template
                    elif isinstance(template, dict) and key in template:
                        # key has specific attribute type
                        attr_type = template[key]

                row, template_child, \
                    key_edit_child, keys_order_child = self._add_row_item(key, val=val, item_kwargs={'type': attr_type},
                                                                          key_edit=key_edit)

                # add row
                item.appendRow(row)

                # loop downstream
                self._add_child(row[0], val, template=template_child, key_edit=key_edit_child,
                                keys_order=keys_order_child)

    def _update_parent(self, item):
        # get item parent
        parent = item.parent()
        if parent:
            # get index
            index_parent = parent.index()

            # get value index
            index_value = self._model.index(parent.row(), 1, parent=index_parent.parent())

            # get value
            value = convert_data(self._model.data(index_value))

            # get children row count
            row_children = parent.rowCount()

            # create empty container for update val
            if isinstance(value, list):
                value_collect = []
            else:
                value_collect = {}

            # loop in each row
            for i in range(row_children):
                index_attr = self._model.index(i, 0, parent=index_parent)
                index_val = self._model.index(i, 1, parent=index_parent)
                attr = convert_data_to_str(self._model.data(index_attr))  # get key
                val = convert_data(self._model.data(index_val))  # get value
                if isinstance(value, list):
                    value_collect.append(val)
                else:
                    value_collect.update({attr: val})

            # assign data
            if value != value_collect:
                self._model.setData(index_value, convert_data_to_str(value_collect))

            # loop to upper level
            self._update_parent(self._model.itemFromIndex(index_parent))
        else:
            # no parent item need to update, save the data value to the item
            index_key = self._model.index(item.row(), 0, parent=item.index().parent())  # current item's key index
            index_value = self._model.index(item.row(), 1, parent=item.index().parent())  # current item's value index
            item_data = self._model.itemFromIndex(index_value)  # current item
            key = self._model.data(index_key)  # key name
            val = convert_data(item_data.text())  # data value

            item_kwargs = item_data.data(role=ROLE_ITEM_KWARGS)  # get ui kwargs for current item
            item_kwargs.update({'value': val})  # override ui kwargs's value to the current value
            item_data.setData(item_kwargs, ROLE_ITEM_KWARGS)  # save ui kwargs

            task_kwargs = self._item.data(0, ROLE_TASK_KWARGS)  # get task kwargs
            task_kwargs[key]['value'] = val
            self._item.setData(0, ROLE_TASK_KWARGS, task_kwargs)  # set back to task item

    def _rebuild_child(self, item):
        index_value = item.index()
        index_attr = self._model.index(item.row(), 0, parent=index_value.parent())

        # get value
        value = convert_data(self._model.data(index_value))
        if isinstance(value, list) or isinstance(value, dict):
            item_attr = self._model.itemFromIndex(index_attr)

            # clear out the children
            rows = item_attr.rowCount()
            item_attr.removeRows(0, rows)

            # get template
            item_kwargs = item.data(role=ROLE_ITEM_KWARGS)
            if item_kwargs and 'template' in item_kwargs:
                template = item_kwargs['template']
            else:
                template = None

            # get key_edit value
            key_edit = False
            if item_kwargs and 'key_edit' in item_kwargs:
                key_edit = item_kwargs['key_edit']

            # get keys_order value
            keys_order = None
            if item_kwargs and 'keys_order' in item_kwargs:
                keys_order = item_kwargs['keys_order']

            # rebuild
            self._add_child(item_attr, value, template=template, key_edit=key_edit, keys_order=keys_order)

    def _add_row_item(self, key, val=None, item_kwargs=None, key_edit=False):
        if item_kwargs is None:
            item_kwargs = {}

        # column 1: property name
        column_property = QStandardItem(key)

        # key edit value
        if key_edit:
            column_property.setEditable(True)
        else:
            column_property.setEditable(False)

        column_property.setData(self._size, role=Qt.SizeHintRole)

        # update kwargs
        if 'type' in item_kwargs and item_kwargs['type'] is not None:
            item_type = item_kwargs['type']
            if not isinstance(item_type, basestring) or item_type not in PROPERTY_ITEMS:
                # item type need to be checked
                item_type = check_item_type(item_type)
            kwargs_add = PROPERTY_ITEMS[item_type].copy()  # make a copy so the config won't be changed
            kwargs_add.update(item_kwargs)
            item_kwargs = kwargs_add

        # column 2: value
        if val is not None:
            item_kwargs.update({'value': val})

        column_val = PropertyItem(data_info=item_kwargs)

        if 'height' in item_kwargs:
            size = QSize(self._size.width(), item_kwargs['height'])

            column_property.setData(size, role=Qt.SizeHintRole)

        # get template
        if 'template' in item_kwargs:
            template = item_kwargs['template']
        else:
            template = None

        # get key_edit val
        key_edit = False
        if 'key_edit' in item_kwargs:
            key_edit = item_kwargs['key_edit']

        # get keys_order val
        keys_order = None
        if 'keys_order' in item_kwargs:
            keys_order = item_kwargs['keys_order']

        return [column_property, column_val], template, key_edit, keys_order

    def _show_menu(self, pos):
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)
        column = item.column()
        if column > 0:
            # only show menu if mouse on value column
            pos = self.viewport().mapToGlobal(pos)
            self.menu.move(pos)

            data_info = item.data(role=ROLE_ITEM_KWARGS)

            if 'select' in data_info and data_info['select']:
                self.action_set_select.setEnabled(True)
                if 'template' in data_info and data_info['template'] is not None:
                    self.action_add_select.setEnabled(True)
                else:
                    self.action_add_select.setEnabled(False)
            else:
                self.action_set_select.setEnabled(False)
                self.action_add_select.setEnabled(False)

            if 'template' in data_info and data_info['template'] is not None:
                self.action_add_element.setEnabled(True)
            else:
                self.action_add_element.setEnabled(False)

            parent = item.parent()
            if parent:
                # get index
                index_parent = parent.index()

                # get value index
                index_value = self._model.index(parent.row(), 1, parent=index_parent.parent())

                # parent value item
                item_attr = self._model.itemFromIndex(index_value)

                data_info = item_attr.data(role=ROLE_ITEM_KWARGS)
                if 'template' in data_info and data_info['template'] is not None:
                    self.action_del_element.setEnabled(True)
                    self.action_dup_element.setEnabled(True)
                else:
                    self.action_del_element.setEnabled(False)
                    self.action_dup_element.setEnabled(False)
            else:
                self.action_del_element.setEnabled(False)
                self.action_dup_element.setEnabled(False)

            self.menu.show()

    def _reset_value(self):
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)
        data_info = item.data(role=ROLE_ITEM_KWARGS)
        value = data_info['default']
        item.setText(convert_data_to_str(value))
        self._rebuild_child(item)
        self._update_parent(item)

    def _set_selection(self):
        """
        set selected nodes as attr
        """
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)

        sel = cmds.ls(selection=True)

        if sel:
            data_info = item.data(role=ROLE_ITEM_KWARGS)
            if 'template' in data_info and data_info['template'] is not None:
                # item is list
                item.setText(convert_data_to_str(sel))
                self._rebuild_child(item)
            else:
                item.setText(convert_data_to_str(sel[0]))

            self._update_parent(item)

    def _add_selection(self):
        """
        add selected nodes to attr
        """
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
            self._rebuild_child(item)
            self._update_parent(item)

    def _add_element(self):
        """
        add element to list or dict
        """
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)

        val = item.text()
        # convert value
        val = convert_data(val)

        # get template
        kwargs = item.data(role=ROLE_ITEM_KWARGS)

        if isinstance(val, list):
            append_val = ''
            if 'template' in kwargs and kwargs['template']:
                template_info = kwargs['template']
                if template_info is not None:
                    if not isinstance(template_info, basestring):
                        append_val = template_info
                    elif template_info not in PROPERTY_ITEMS:
                        append_val = template_info
                    else:
                        append_val = PROPERTY_ITEMS[template_info]['default']

            # list attr
            val.append(append_val)
        else:
            # dict attr
            # check if has key
            if val.keys():
                key = val.keys()[-1] + '_copy'
                append_val = val[val.keys()[-1]]
            else:
                key = 'key'
                append_val = ''
            val.update({key: append_val})

        item.setText(convert_data_to_str(val))

        self._rebuild_child(item)
        self._update_parent(item)

    def _dup_element(self):
        """
        duplicate current item
        """
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)

        val = convert_data(item.text())

        # get parent val
        parent = item.parent()
        index_parent = parent.index()

        # get value index
        index_value = self._model.index(parent.row(), 1, parent=index_parent.parent())

        # get parent value item
        item_parent = self._model.itemFromIndex(index_value)

        # get value
        val_parent = convert_data(self._model.data(index_value))

        if isinstance(val_parent, list):
            val_parent.append(val)
        else:
            # get key
            index_parent = self._model.index(item.row(), 0, parent=index_parent)
            key = convert_data(self._model.data(index_parent))
            val_parent.update({key + '_copy': val})

        item_parent.setText(convert_data_to_str(val_parent))

        self._rebuild_child(item_parent)
        self._update_parent(item_parent)
        self.setCurrentIndex(index)

    def _del_element(self):
        """
        delete current item
        """
        index = self.currentIndex()
        item = self._model.itemFromIndex(index)

        val = convert_data(item.text())

        # get parent val
        parent = item.parent()
        index_parent = parent.index()

        # get value index
        index_value = self._model.index(parent.row(), 1, parent=index_parent.parent())

        # get parent value item
        item_parent = self._model.itemFromIndex(index_value)

        # get value
        val_parent = convert_data(self._model.data(index_value))

        if isinstance(val_parent, list):
            val_parent.remove(val)
        else:
            # get key
            index_parent = self._model.index(item.row(), 0, parent=index_parent)
            key = convert_data(self._model.data(index_parent))
            val_parent.pop(key)
        item_parent.setText(convert_data_to_str(val_parent))
        self._rebuild_child(item_parent)
        self._update_parent(item_parent)
        self.setCurrentIndex(QModelIndex())


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

        data_info = item.data(role=ROLE_ITEM_KWARGS)

        value = index.data()

        if data_info:
            widget = data_info['widget'](parent)
        else:
            widget = QLineEdit(parent)

        # extra setting
        if isinstance(widget, QComboBox):
            # set enum
            widget.addItems(data_info['enum'])
            enum_index = widget.findText(value, Qt.MatchFixedString)
            widget.setCurrentIndex(enum_index)

        elif isinstance(widget, QDoubleSpinBox) or isinstance(widget, QSpinBox):
            # set range
            if 'min' in data_info and data_info['min'] is not None:
                widget.setMinimum(data_info['min'])
            if 'max' in data_info and data_info['max'] is not None:
                widget.setMaximum(data_info['max'])
            if isinstance(widget, QSpinBox) and data_info['skippable']:
                widget.setSpecialValueText('None')

        elif isinstance(widget, QLineEdit):
            widget.setFrame(False)

        return widget

    def setModelData(self, editor, model, index):
        item = index.model().itemFromIndex(index)
        # get previous value
        value = item.text()

        # get data info
        data_info = item.data(role=ROLE_ITEM_KWARGS)

        # set data
        super(PropertyDelegate, self).setModelData(editor, model, index)

        if not data_info:
            # shoot rebuild signal
            self.SIGNAL_UPDATE_PARENT.emit(item)
            return

        # if it's string/list/dict
        if isinstance(editor, QLineEdit):
            # get default value
            value_default = data_info['default']
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
        if 'value' in self._data_info and self._data_info['value'] is not None:
            val = self._data_info['value']
        else:
            val = self._data_info['default']

        val = convert_data_to_str(val)

        self.setText(val)

        self.setData(self._data_info, role=ROLE_ITEM_KWARGS)

        if 'hint' in self._data_info and self._data_info['hint']:
            self.setData(self._data_info['hint'], Qt.ToolTipRole)


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
