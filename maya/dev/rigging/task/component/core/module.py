# IMPORT PACKAGES

# import os
import os

# import inspect
import inspect

# import utils
import utils.common.logUtils as logUtils
import utils.common.modules as modules
import utils.common.files as files
import utils.common.naming as naming
import utils.common.assets as assets

# import pack
import pack

# config
import dev.rigging.task.component.config as config

# ICON
import dev.rigging.builder.ui.widgets.icons as icons

# CONSTANT
import dev.rigging.task.config.PROPERTY_ITEMS as PROPERTY_ITEMS
PROPERTY_ITEMS = PROPERTY_ITEMS.PROPERTY_ITEMS

logger = logUtils.logger

MODULE_INFO_FORMAT = '.moduleInfo'

text_path = os.path.join(os.path.dirname(config.__file__), 'MODULE_TEMPLATE.txt')
infile = open(text_path, 'r')
MODULE_TEMPLATE = infile.read()
infile.close()


# CLASS
class Module(pack.Pack):
    """
    base class for module
    """
    def __init__(self, **kwargs):
        # get module info file before anything, because we need the info to register kwargs
        # module info file locate the same place with the py file
        class_file_path = inspect.getfile(self.__class__)
        module_path = os.path.dirname(class_file_path)
        module_info_path = os.path.join(module_path, self.__class__.__name__ + MODULE_INFO_FORMAT)
        if os.path.exists(module_info_path):
            self._module_info = files.read_json_file(module_info_path)
        else:
            self._module_info = {}

        super(Module, self).__init__(**kwargs)

        self._task = 'dev.rigging.task.component.core.module'
        self._task_type = 'module'
        self._save = self._module_info.get('save', False)  # set this attr to True if we want to save module data

        # icon
        self._icon_new = icons.module_new
        self._icon_lock = icons.module_lock
        self._icon_warn = icons.module_warn

    def register_kwargs(self):
        """
        we need to override this function, because module doesn't need that many attributes as normal component
        """
        # register the basic info

        self.register_attribute('mirror', False, attr_name='mirror', attr_type='bool', hint="mirror component")

        self.register_attribute('side', naming.Side.Key.m, attr_name='side', short_name='s', attr_type='enum',
                                enum=naming.Side.Key.all, hint="component's side")

        self.register_attribute('description', '', attr_name='description', short_name='des', attr_type='str',
                                hint="component's description", skippable=False)

        self.register_attribute('input connection', '', attr_name='input_connect', attr_type='str', select=False,
                                hint=("component's input connection,\nshould be a component's joint's output matrix,\n"
                                      "or an existing maya node's matrix attribute"))

        # load kwargs from module info file
        self.register_kwargs_from_module_info()

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

    def pre_build(self):
        super(Module, self).pre_build()
        self.create_hierarchy()
        self.create_sub_task_from_module_info()
        self.connect_module_attrs_to_sub_task()
        # run each task's pre build
        for task_obj in self._sub_components_objs:
            task_obj.pre_build()

    def build(self):
        super(Module, self).build()
        # run each task's build
        for task_obj in self._sub_components_objs:
            task_obj.build()

    def post_build(self):
        super(Module, self).post_build()
        # run each task's post build
        for task_obj in self._sub_components_objs:
            task_obj.post_build()

    def pack_override_kwargs_registration(self):
        """
        empty this function, let user decide which component should be connect with the main input,
        module should allow sub components to mirror
        """
        pass

    def create_sub_task_from_module_info(self):
        """
        create tasks base on module info
        """
        # get all tasks info
        tasks_info = self._module_info.get('sub_tasks', [])

        # create task objects
        for task_info in tasks_info:
            task_name = task_info.keys[0]
            task_path = task_info[task_name]['task_path']
            task_kwargs = task_info[task_name]['task_kwargs']

            # import task
            task_import, task_function = modules.import_module(task_path)
            task_func = getattr(task_import, task_function)

            task_obj = task_func(name=task_name, parent=self._parent)
            # set task data name to module name
            task_obj.task_data_name = self._name
            # attach to module
            setattr(self, task_name, task_obj)
            # register input attrs
            task_obj.kwargs_input = task_kwargs
            # add to task object list
            self._sub_components_objs.append(task_obj)

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


# functions
def get_module_info(project, module_name):
    """
    get module information from given project and module name, will return None if not exist

    Args:
        project(str)
        module_name(str)

    Returns:
        module_info(dict)
    """
    # get task folder
    task_folder_path = assets.get_project_task_path(project, warning=False)

    if task_folder_path:
        # get module task info file path
        module_info_path = os.path.join(task_folder_path, module_name+MODULE_INFO_FORMAT)
        # check if exist
        if os.path.exists(module_info_path):
            module_info = files.read_json_file(module_info_path)
        else:
            module_info = None
    else:
        module_info = None

    return module_info


def get_all_module_in_folder(folder):
    """
    get all module from folders

    Args:
        folder(str): module folder path

    Returns:
        module_names(list)
    """
    module_names = []
    # list all module info files
    module_info_files = files.get_files_from_path(folder, extension=MODULE_INFO_FORMAT, full_paths=False)
    if module_info_files:
        for module_info in module_info_files:
            name = module_info.replace(MODULE_INFO_FORMAT, '')
            module_names.append(name)
        module_names.sort()

    return module_names


def generate_module_script_file(project, module_name):
    # get script file path
    task_folder_path = assets.get_project_task_path(project, warning=False)
    if task_folder_path:
        module_script_path = os.path.join(task_folder_path, module_name+'.py')
        if os.path.exists(module_script_path):
            # module script already exist, return
            return None
        else:
            # remove template docstring
            template = MODULE_TEMPLATE[5:]
            template = template[:-4]

            # get args in docstring
            module_path = "'{}.scripts.task.{}'".format(project, module_name)
            module_class_name = module_name[0].upper() + module_name[1:]

            # replace keywords with args
            module_script = template
            for input_arg, temp_keyword in zip([module_path, module_class_name],
                                               ['TEMP_MODULE_PATH', 'TEMP_CLASS_NAME']):
                module_script = module_script.replace(temp_keyword, input_arg)

            # write file
            outfile = open(module_script_path, 'w')
            outfile.write(module_script)
            outfile.close()

            logger.info('create module script successfully at {}'.format(module_script_path))
            return module_script_path
    else:
        return None


def export_module_info(project, module_name, module_attrs_info, sub_tasks_info):
    """
    export module info

    Args:
        project(str)
        module_name(str)
        module_attrs_info(dict)
        sub_tasks_info(dict)

    Returns:
        module_info_path(str)
    """
    # compose module info
    module_info = {}
    # kwargs keys
    module_info.update({'kwargs_keys': module_attrs_info.keys()})
    # kwargs
    module_info.update({'kwargs': dict(module_attrs_info)})
    # sub tasks info
    module_info.update({'sub_tasks': sub_tasks_info})
    # get connect info
    connect_info = {}
    for kwarg_info in module_attrs_info.values():
        attr_name = kwarg_info['attr_name']
        connect = kwarg_info.get('output', [])
        connect_info_attr = {}
        for output_attr in connect:
            output_attr_split = output_attr.split('.')  # split to task and task attr
            sub_task = output_attr_split[0]
            task_attr = output_attr_split[1]
            if sub_task not in connect_info_attr:
                connect_info_attr.update({sub_task: [task_attr]})
            else:
                connect_info_attr[sub_task].append(task_attr)
        connect_info.update({attr_name: connect_info_attr})
    module_info.update({'connect_info': connect_info})

    # get task folder
    task_folder_path = assets.get_project_task_path(project, warning=False)

    # generate module python script
    generate_module_script_file(project, module_name)
    print module_info
    # save module info
    if task_folder_path:
        module_info_path = os.path.join(task_folder_path, module_name+MODULE_INFO_FORMAT)
        files.write_json_file(module_info_path, module_info)
        logger.info("save module info for module '{}' at {} successfully".format(module_name, module_info_path))
        return module_info_path
    else:
        logger.warning("no task folder found for module '{}' at '{}', skipped".format(module_name, project))
        return None
