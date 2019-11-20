# IMPORT PACKAGES

# import os
import os

# import maya cmds
import maya.cmds as cmds

# import OrderedDict
from collections import OrderedDict 

# import utils
import utils.common.variables as variables
import utils.common.logUtils as logUtils
import utils.common.modules as modules
import utils.common.attributes as attributes
import utils.rigging.buildUtils as buildUtils

# ICON
import dev.rigging.builder.ui.widgets.icons as icons

# CONSTANT
import dev.rigging.task.config.PROPERTY_ITEMS as PROPERTY_ITEMS
PROPERTY_ITEMS = PROPERTY_ITEMS.PROPERTY_ITEMS

logger = logUtils.logger


# CLASS
class Task(object):
    """
    base class for Task
    """
    def __init__(self, **kwargs):
        super(Task, self).__init__()
        # get name and builder
        name = variables.kwargs('name', None, kwargs, short_name='n')
        builder = variables.kwargs('builder', None, kwargs)
        if not name:
            name = self.__class__.__name__
        self._name = name
        self._task = 'dev.rigging.task.core.task'
        self._task_type = 'task'
        self._builder = builder  # plug builder in to get builder's variables
        self.project = None
        self.asset = None
        self.rig_type = None
        if self._builder:
            self.project = self._builder.project
            self.asset = self._builder.asset
            self.rig_type = self._builder.rig_type
        self._save = False  # attr to check if has save function
        self.save_data_path = None  # store saving path for further use

        # this attr is specific for module, task need to read data from its own folder, will need to get the task name
        # the default is the task's own name, but it's bundled to a module, it won't have its own data folder, we need
        # to get data from module's data folder instead
        self.task_data_name = self._name

        # icon
        self._icon_new = icons.task_new
        self._icon_lock = icons.task_lock
        self._icon_warn = icons.task_warn

        self.kwargs_task = {}  # store each kwarg's long name, short name and default value
        self.kwargs_ui = OrderedDict()  # store ui info with order
        self.kwargs_input = {}  # use kwargs input to plug in user final inputs value, to register to class

        self.signal = 1  # 1 is success, 2 is warning, error will be caught by ui
        self.message = ''  # if want to show any specific message to log window when click on status icon

        self.register_kwargs()  # register kwargs to ui and class for further use

    @ property
    def name(self):
        return self._name

    @ property
    def task(self):
        return self._task

    @ property
    def task_type(self):
        return self._task_type

    @ property
    def builder(self):
        return self._builder

    @ property
    def save(self):
        return self._save

    @ property
    def icons(self):
        return [self._icon_new, self._icon_lock, self._icon_warn]

    @ name.setter
    def name(self, task_name):
        self._name = task_name

    @ builder.setter
    def builder(self, builder_obj):
        self._builder = builder_obj
        if self._builder:
            self.project = self._builder.project
            self.asset = self._builder.asset
            self.rig_type = self._builder.rig_type

    @ save.setter
    def save(self, save_check):
        self._save = save_check

    def pre_build(self):
        self.signal = 1  # preset the signal to avoid overwrite
        self.message = ''

        self.register_inputs()  # register inputs to class

    def build(self):
        self.signal = 1  # preset the signal to avoid overwrite
        self.message = ''

    def post_build(self):
        self.signal = 1  # preset the signal to avoid overwrite
        self.message = ''

    def register_kwargs(self):
        """
        all sub classes should register custom kwargs here,
        using self.register_attribute(name, value, attr_name=None, short_name=None, attr_type=None, **kwargs)
        it will automatically update the kwargs information to self.kwargs_task and self.kwargs_ui
        """
        pass

    def register_inputs(self):
        for key, val in self.kwargs_task.iteritems():
            attr_val = variables.kwargs(val[0], val[1], self.kwargs_input, short_name=val[2])
            self.__setattr__(val[0], attr_val)

    def register_attribute(self, name, value, attr_name=None, short_name=None, attr_type=None, **kwargs):
        """
        register attribute to the task, and ui will pick up the information

        Args:
            name(str): attribute name in kwargs
            value: attribute default value (function read type by the value, don't use None)

        Keyword Args:
            attr_name(str): attribute name in class
            short_name(str): attribute short name
            attr_type(str): if it has more complicate ui info need from PROPERTY_ITEMS
            min(float/int): min value
            max(float/int): max value
            skippable(bool): define if the kwarg can be skip or not, it will turn red if no value for unskippable attr.
                             default is True
            select(bool): if right click can add/set selection
            enum(list): enum options
            template: list/dict children template
            key_edit(bool): if double click can edit dict key name
            keys_order(list): if the dictionary's keys need to show by order
            hint(str): attribute's hint
            custom(bool): if set to custom, the kwarg will be QLineEdit, and user can add/remove/duplicate all the time,
                          it will be the user's responsibility to keep the kwarg consistent with component,
                          normally used for kwargs need to be override
        """
        hint = kwargs.get('hint', '')

        # check attr type to save in hint
        attr_type_str = self._check_value_type(value)

        if not attr_type:
            # if not specific attribute type, use attr_type_str, it will get all ui info from PROPERTY_ITEMS
            attr_type = attr_type_str

        if not attr_name:
            attr_name = name

        kwargs_ui = PROPERTY_ITEMS[attr_type].copy()  # get kwargs from PROPERTY_ITEMS, make a copy
        kwargs_ui.update(kwargs)
        kwargs_ui.update({'attr_name': attr_name})

        if attr_type in ['float', 'int']:
            range_value = [kwargs_ui['min'], kwargs_ui['max']]
            if range_value[0] is not None and range_value[1] is not None:
                # sort min and max value, make sure the max is greater than the min
                range_value.sort()
                kwargs_ui['min'] = range_value[0]
                kwargs_ui['max'] = range_value[1]

            if range_value[0] is not None and range_value[0] > value:
                value = range_value[0]  # set value to min if min value greater than the given value
            if range_value[1] is not None and range_value[1] < value:
                value = range_value[1]  # set value to max if max value is lesser than the given value

        kwargs_ui['default'] = value

        # add attr name to hint
        hint = self._add_attr_name_to_hint(hint, attr_name, value, attr_type=attr_type_str)
        # override hint
        kwargs_ui.update({'hint': hint})

        self._register_attr_to_task([name, attr_name, value, short_name], kwargs_ui)

    def update_attribute(self, name, **kwargs):
        """
        update task's attribute information
        Args:
            name(str): attribute name in kwargs

        Keyword Args:
            default: default value
            min(float/int): min value
            max(float/int): max value
            skippable(bool): define if the kwarg can be skip or not, it will turn red if no value for unskippable attr.
                             default is True
            select(bool): if right click can add/set selection
            enum(list): enum options
            template: list/dict children template
            key_edit(bool): if double click can edit dict key name
            keys_order(list): if the dictionary's keys need to show by order
            hint(str): attribute's hint
            custom(bool): if set to custom, the kwarg will be QLineEdit, and user can add/remove/duplicate all the time,
                          it will be the user's responsibility to keep the kwarg consistent with component,
                          normally used for kwargs need to be override
        """
        if name in self.kwargs_ui:
            # override hint with attr name added on
            hint = kwargs.get('hint', None)
            if hint:
                attr_name = self.kwargs_ui[name]['attr_name']
                default = kwargs.get('default', None)
                if default is None:
                    default = self.kwargs_ui[name]['default']
                hint = self._add_attr_name_to_hint(hint, attr_name, default)
                kwargs.update({'hint': hint})
            self.kwargs_ui[name].update(kwargs)

    def remove_attribute(self, name):
        """
        remove the task attribute

        Args:
            name(str): attribute name in kwargs
        """

        self.kwargs_task.pop(name, None)
        self.kwargs_ui.pop(name, None)

    def save_data(self):
        """
        function to save data, all tasks with saving data function should sub class here for saving
        """
        # get saving path
        self.save_data_path = buildUtils.get_data_path(self.task_data_name, self.rig_type, self.asset, self.project,
                                                       warning=False, check_exist=False)
        # create folder if not exist
        if not os.path.exists(self.save_data_path):
            os.mkdir(self.save_data_path)

    def update_data(self):
        """
        function to update selection data to the saving file,
        it will be a normal saving selection function if no data file saved previously
        all tasks with updating data function should sub class here for saving
        """
        # get saving path
        self.save_data_path = buildUtils.get_data_path(self._name, self.rig_type, self.asset, self.project,
                                                       warning=False, check_exist=False)
        # create folder if not exist
        if not os.path.exists(self.save_data_path):
            os.mkdir(self.save_data_path)

    def _register_attr_to_task(self, kwargs_task, kwargs_ui):
        """
        add custom attribute to task
        """

        self.kwargs_task.update({kwargs_task[0]: [kwargs_task[1], kwargs_task[2], kwargs_task[3]]})

        self.kwargs_ui.update({kwargs_task[0]: kwargs_ui})

    def _add_attr_from_dict(self, attr_dict):
        """
        add class attributes from given dictionary
        """
        for key, val in attr_dict.iteritems():
            setattr(self, key, val)

    def _add_obj_attr(self, attr, attr_dict):
        attr_split = attr.split('.')
        attr_parent = self
        if len(attr_split) > 1:
            for a in attr_split[:-1]:
                attr_parent = getattr(attr_parent, a)
        setattr(attr_parent, attr_split[-1], ObjectView(attr_dict))

    def _get_obj_attr(self, attr):
        attr_value = modules.get_obj_attr(self, attr)
        return attr_value

    def _get_node_name(self, node_name):
        """
        get the given name as the name in the scene.
        given name could be builder's attribute, maya node's attribute or maya node

        Args:
            node_name(str): builder's attribute, maya node's attribute or maya node

        Returns:
            node_name_return(str): maya node name or maya node's attribute
        """
        # check if the node name is an component attribute
        builder_attr = self._get_obj_attr('builder.' + node_name)
        if builder_attr:
            node_name_return = builder_attr
        else:
            # check if it's a node in scene
            attr_split = node_name.split('.')  # split if it's an attribute
            if cmds.objExists(attr_split[0]):
                if len(attr_split) > 1:
                    # given name is an attr, check if attr exist
                    if attributes.check_attr_exists(node_name.replace(attr_split[0]+'.', ''), node=attr_split[0]):
                        node_name_return = node_name
                    else:
                        node_name_return = None
                else:
                    # given name is a node name
                    node_name_return = node_name
            else:
                # node doesn't exist
                node_name_return = None

        return node_name_return

    def _add_attr_name_to_hint(self, hint, attr_name, value, attr_type=None):
        """
        add attr name and attr type to hint
        """
        if not attr_type:
            attr_type = self._check_value_type(value)

        hint_attr_name = attr_name
        if attr_type:
            hint_attr_name += '({})'.format(attr_type)
        hint = '{}: {}'.format(hint_attr_name, hint)

        return hint

    def _get_attr_from_base_node(self, attr_name):
        """
        get attr from builder's base node
        Args:
            attr_name(str): base node's attribute name

        Returns:
            attr_val: attribute's value, None if attribute doesn't exist
        """
        attr_val = modules.get_obj_attr(self.builder, 'base_node.'+attr_name)
        return attr_val

    @ staticmethod
    def _check_value_type(value):
        if value in [True, False]:
            attr_type = 'bool'
        elif isinstance(value, float):
            attr_type = 'float'
        elif isinstance(value, int):
            attr_type = 'int'
        elif isinstance(value, list):
            attr_type = 'list'
        elif isinstance(value, dict):
            attr_type = 'dict'
        elif isinstance(value, basestring):
            attr_type = 'str'
        else:
            attr_type = None
        return attr_type


#  SUB CLASS
class ObjectView(object):
    def __init__(self, kwargs):
        self.__dict__ = kwargs
