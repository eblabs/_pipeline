# IMPORT PACKAGES

# import OrderedDict
from collections import OrderedDict 

# import utils
import utils.common.variables as variables
import utils.common.logUtils as logUtils

# ICON
import dev.rigging.builder.ui.widgets.icons as icons

# CONSTANT
import dev.rigging.task.config.PROPERTY_ITEMS as PROPERTY_ITEMS
PROPERTY_ITEMS = PROPERTY_ITEMS.PROPERTY_ITEMS

logger = logUtils.logger


# CLASS
class Task(object):
    """base class for Task"""
    def __init__(self, **kwargs):
        super(Task, self).__init__()
        # get name and builder
        name = variables.kwargs('name', None, kwargs, short_name='n')
        builder = variables.kwargs('builder', None, kwargs)
        if not name:
            name = self.__class__.__name__
        self._name = name[0].lower() + name[1:]  # make sure task name starts with lowercase
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

        # icon
        self._icon_new = icons.task_new
        self._icon_ref = icons.task_reference

        self.kwargs_task = {}
        self.kwargs_ui = OrderedDict()

        self.signal = 1  # 1 is success, 2 is warning, error will be caught by ui
        self.message = ''  # if want to show any specific message to log window when click on status icon

        self.register_attrs(**kwargs)

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
        return [self._icon_new, self._icon_ref]

    @name.setter
    def name(self, task_name):
        self._name = task_name

    @builder.setter
    def builder(self, builder_obj):
        self._builder = builder_obj
        if self._builder:
            self.project = self._builder.project
            self.asset = self._builder.asset
            self.rig_type = self._builder.rig_type

    def pre_build(self):
        self.signal = 1  # preset the signal to avoid overwrite
        self.message = ''

    def build(self):
        self.signal = 1  # preset the signal to avoid overwrite
        self.message = ''

    def post_build(self):
        self.signal = 1  # preset the signal to avoid overwrite
        self.message = ''

    def register_attrs(self, **kwargs):
        self.register_kwargs()
        self.register_inputs(**kwargs)

    def register_kwargs(self):
        """
        all sub classes should register custom kwargs here,
        using self.register_attribute(name, value, attr_name=None, short_name=None, attr_type=None, **kwargs)
        it will automatically update the kwargs information to self.kwargs_task and self.kwargs_ui
        """
        pass

    def register_inputs(self, **kwargs):
        for key, val in self.kwargs_task.iteritems():
            attr_val = variables.kwargs(val[0], val[1], kwargs, short_name=val[2])
            self.__setattr__(key, attr_val)

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
            skippable(bool): if True, will show 'None' if int value is out of range
            select(bool): if right click can add/set selection
            enum(list): enum options
            template: list/dict children template
            key_edit(bool): if double click can edit dict key name
            keys_order(list): if the dictionary's keys need to show by order
            hint(str): attribute's hint
        """

        if not attr_type:
            # if not specific attribute type, define the type by value
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

        self._register_attr_to_task([name, value, attr_name, short_name], kwargs_ui)

    def update_attribute(self, name, **kwargs):
        """
        update task's attribute information
        Args:
            name(str): attribute name in kwargs

        Keyword Args:
            default: default value
            min(float/int): min value
            max(float/int): max value
            select(bool): if right click can add/set selection
            enum(list): enum options
            template: list/dict children template
            key_edit(bool): if double click can edit dict key name
            keys_order(list): if the dictionary's keys need to show by order
            hint(str): attribute's hint
        """
        if name in self.kwargs_ui:
            self.kwargs_ui[name].update(kwargs)

    def remove_attribute(self, name, attr_name=None):
        """
        remove the task attribute

        Args:
            name(str): attribute name in kwargs

        Keyword Args:
            attr_name(str): attribute name in class
        """
        if attr_name:
            key = attr_name
        else:
            key = name

        self.kwargs_task.pop(key, None)
        self.kwargs_ui.pop(name, None)

    def _register_attr_to_task(self, kwargs_task, kwargs_ui):
        """
        add custom attribute to task
        """

        self.kwargs_task.update({kwargs_task[2]: [kwargs_task[0], kwargs_task[1], kwargs_task[3]]})

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
        attr_split = attr.split('.')
        attr_parent = self
        for attr_part in attr_split:
            if hasattr(attr_parent, attr_part):
                attr_parent = getattr(attr_parent, attr_part)
            else:
                attr_parent = None
                break
        return attr_parent


#  SUB CLASS
class ObjectView(object):
    def __init__(self, kwargs):
        self.__dict__ = kwargs
