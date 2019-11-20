# IMPORT PACKAGES

# import os
import os

# import utils
import utils.common.logUtils as logUtils
import utils.common.modules as modules
import utils.common.files as files

# import task
import task

# ICON
import dev.rigging.builder.ui.widgets.icons as icons

# CONSTANT
import dev.rigging.task.config.PROPERTY_ITEMS as PROPERTY_ITEMS
PROPERTY_ITEMS = PROPERTY_ITEMS.PROPERTY_ITEMS

logger = logUtils.logger

MODULE_INFO_FORMAT = '.moduleInfo'


# CLASS
class Module(task.Task):
    """
    base class for Task
    """
    def __init__(self, **kwargs):
        # get module info file before anything, because we need the info to register kwargs
        # module info file locate the same place with the py file
        module_path = os.path.dirname(self.__file__)
        module_info_path = os.path.join(module_path, self.__class__.__name__ + MODULE_INFO_FORMAT)
        if os.path.exists(module_info_path):
            self._module_info = files.read_json_file(module_info_path)
        else:
            self._module_info = {}

        super(Module, self).__init__(**kwargs)

        self._task = 'dev.rigging.task.core.module'
        self._task_type = 'module'
        self._save = self._module_info.get('save', False)  # set this attr to True if we want to save module data

        # icon
        self._icon_new = icons.module_new
        self._icon_lock = icons.module_lock
        self._icon_warn = icons.module_warn

        # task objects
        self._task_objs = []  # store all task objects here for further use

    def register_kwargs(self):
        super(Module, self).register_kwargs()
        self.register_kwargs_from_module_info()

    def pre_build(self):
        super(Module, self).pre_build()
        self.create_hierarchy()
        self.create_sub_task_from_module_info()
        self.connect_module_attrs_to_sub_task()
        # run each task's pre build
        for task_obj in self._task_objs:
            task_obj.pre_build()

    def build(self):
        super(Module, self).build()
        # run each task's build
        for task_obj in self._task_objs:
            task_obj.build()

    def post_build(self):
        super(Module, self).post_build()
        # run each task's post build
        for task_obj in self._task_objs:
            task_obj.post_build()

    def register_kwargs_from_module_info(self):
        """
        register attributes from module info
        """
        # get all kwargs
        kwargs = self._module_info.get('kwargs', {})
        kwargs_keys = self._module_info.get('kwargs_keys', [])

        # loop in each kwarg and register
        for attr in kwargs_keys:
            if attr in kwargs:
                attr_info = kwargs[attr]
                value = attr_info.get('default', None)
                self.register_attribute(attr, value, **attr_info)

    def create_sub_task_from_module_info(self):
        """
        create tasks base on module info
        """
        # get all tasks info
        tasks_info = self._module_info.get('tasks', [])

        # create task objects
        for task_info in tasks_info:
            task_name = task_info.keys[0]
            task_path = task_info[task_name]['path']
            task_kwargs = task_info[task_name]['task_kwargs']

            # import task
            task_import, task_function = modules.import_module(task_path)
            task_func = getattr(task_import, task_function)

            task_obj = task_func(name=task_name, builder=self._builder)
            # set task data name to module name
            task_obj.task_data_name = self._name
            # attach to module
            setattr(self, task_name, task_obj)
            # register input attrs
            task_obj.kwargs_input = task_kwargs
            # add to task object list
            self._task_objs.append(task_obj)

    def connect_module_attrs_to_sub_task(self):
        """
        feed in module's attributes to tasks base on module info
        """
        # get connection info
        connect_info = self._module_info.get('connect_info', {})

        for attr, attr_info in connect_info.iteritems():
            # get module's attr value
            val = getattr(self, attr)
            # feed in to each object
            for task_name, attrs_connect in attr_info.iteritems():
                kwargs_update = {}
                for attr_update in attrs_connect:
                    kwargs_update.update({attr_update: val})
                task_obj = getattr(self, task_name)
                task_obj.kwargs_input.update(kwargs_update)

    def create_hierarchy(self):
        """
        create module hierarchy
        """
        pass
