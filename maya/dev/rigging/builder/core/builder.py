# IMPORT PACKAGES

# import os
import os

# import inspect
import inspect

# import utils
import utils.common.variables as variables
import utils.common.modules as modules
import utils.common.files as files
import utils.common.logUtils as logUtils

# CONSTANT
logger = logUtils.logger


# CLASS
class Builder(object):
    """
    base template for all the build script
    """
    def __init__(self):
        super(Builder, self).__init__()
        self._project = None
        self._asset = None
        self._rig_type = None
        self.task_data_paths = []
        self._tasks = []
        self._tasks_info = {}

        self.tasks_level_list = []
        # task info before load current task info, need this to compare for saving the current task info
        self._tasks_compare = None
        self._tasks_info_compare = None

    @property
    def project(self):
        return self._project

    @property
    def asset(self):
        return self._asset

    @property
    def rig_type(self):
        return self._rig_type

    def get_task_data_paths(self):
        """
        get task data paths from both current class and parent classes, also generate a level list
        """
        cls_list = inspect.getmro(self.__class__)[:-1]
        # create a level list for register tasks later, each level loops in register task first, then task info file
        self.tasks_level_list = [[] for _ in range(len(cls_list))]

        # get task info file
        for cls in cls_list:
            path_cls = inspect.getfile(cls)
            path_dirname = os.path.dirname(path_cls)
            path_task_data = os.path.join(path_dirname, 'tasks.tsk')
            if os.path.exists(path_task_data):
                self.task_data_paths.append(path_task_data)
            else:
                self.task_data_paths.append('')

        self.task_data_paths.reverse()

    def register_task(self, **kwargs):
        """
        register task to build script

        Keyword Args:
            name(str): task name
            display(str): task display name
            task_path(method): task function
            index(str/int): register task at specific index
                            if given string, it will register after the given task
            parent(str): parent task to the given task
            kwargs(dict): task kwargs
            section(str): register task in specific section (normally for in-class method)
                          'pre_build', 'build', 'post_build', default is 'post_build'
            background_color(list): task background color, None will use the default,
                                    use str 'default' to set back to default
            text_color(list): task text color, None will use the default
                              use str 'default' to set back to default
        """

        # get kwargs
        _name = variables.kwargs('name', '', kwargs, short_name='n')
        _display = variables.kwargs('display', '', kwargs, short_name='dis')
        _index = variables.kwargs('index', None, kwargs, short_name='i')
        _task_path = variables.kwargs('task_path', None, kwargs, short_name='tsk')
        _parent = variables.kwargs('parent', '', kwargs, short_name='p')
        _kwargs = variables.kwargs('kwargs', {}, kwargs)
        _section = variables.kwargs('section', 'post_build', kwargs)
        _background_color = variables.kwargs('background_color', None, kwargs)
        _text_color = variables.kwargs('text_color', None, kwargs)

        # kwargs for loading task info only, not for user
        _inheritance = variables.kwargs('inheritance', None, kwargs)
        _check = variables.kwargs('check', 1, kwargs)

        if _inheritance is None:
            _level = check_level()  # check if the task is referenced or created in the class

            if _level > 0:
                _inheritance = True
            else:
                _inheritance = False
        else:
            _level = None  # load from task info file, no need to put in level list

        if not _display:
            _display = _name

        # get task
        if inspect.ismethod(_task_path):
            # in class method, get method name for ui display
            _task = _task_path
            _task_path = _task_path.__name__
            _task_kwargs = _kwargs
        else:
            # imported task, get task object
            task_import, task_function = modules.import_module(_task_path)
            _task = getattr(task_import, task_function)
            if inspect.isfunction(_task):
                # function, normally is callback
                _task_kwargs = task_import.kwargs_ui
            else:
                # task class
                task_obj = _task()
                _task_kwargs = task_obj.kwargs_ui
                # add attr
                setattr(self, _name, task_obj)
            # if value in _kwargs, set value as default
            if 'value' in _kwargs and _kwargs['value'] is not None:
                _kwargs.update({'default': _kwargs['value']})
                _kwargs.pop('value')
            _task_kwargs.update(_kwargs)

        # add task info to class as attribute
        _task_info = {'task': _task,
                      'task_path': _task_path,
                      'display': _display,
                      'task_kwargs': _task_kwargs,
                      'parent': _parent,
                      'section': _section,
                      'inheritance': _inheritance,
                      'index': _index,
                      'check': _check,
                      'background_color': _background_color,
                      'text_color': _text_color}

        self._tasks_info.update({_name: _task_info})

        if _level is not None:
            self.tasks_level_list[-1-_level].append(_name)

    def update_task(self, name, **kwargs):
        """
        update registered task's info, used only for load task info from file

        Args:
            name(str): task name

        Keyword Args:
            task(method): task function
            display(str): task display name
            index(str/int): register task at specific index
                            if given string, it will register after the given task
            parent(str): parent task to the given task
            kwargs(dict): task kwargs
            check(int): task check state
            background_color(list): task background color, None will use the default,
                                    use str 'default' to set back to default
            text_color(list): task text color, None will use the default
                              use str 'default' to set back to default
        """
        _task_kwargs = {}
        # get kwargs
        _display = variables.kwargs('display', '', kwargs, short_name='dis')
        _task_path = variables.kwargs('task_path', None, kwargs, short_name='tsk')
        _parent = variables.kwargs('parent', '', kwargs, short_name='p')
        _kwargs = variables.kwargs('kwargs', {}, kwargs)
        _index = variables.kwargs('index', None, kwargs, short_name='i')
        _check = variables.kwargs('check', 1, kwargs)
        _background_color = variables.kwargs('background_color', None, kwargs)
        _text_color = variables.kwargs('text_color', None, kwargs)

        if _display:
            self._tasks_info[name]['display'] = _display

        if _task_path:
            # imported task, get task object
            task_import, task_function = modules.import_module(_task_path)
            _task = getattr(task_import, task_function)
            if not inspect.isfunction(_task):
                # task class
                task_obj = _task()
                # add attr
                setattr(self, name, task_obj)
                # get task kwargs
                _task_kwargs = task_obj.kwargs_ui
            else:
                _task_kwargs = task_import.kwargs_ui
            self._tasks_info[name]['task'] = _task
            self._tasks_info[name]['task_path'] = _task_path

        if _parent:
            self._tasks_info[name]['parent'] = _parent

        if _task_kwargs:
            _kwargs_orig = self._tasks_info[name]['task_kwargs']
            for key, data in _task_kwargs.iteritems():
                if key in _kwargs:
                    _task_kwargs[key]['default'] = _kwargs[key]['default']
                elif key in _kwargs_orig:
                    default_value = _task_kwargs[key]['default']
                    orig_value = _kwargs_orig[key]['default']
                    if type(default_value) == type(orig_value) and default_value != orig_value:
                        _task_kwargs[key]['default'] = orig_value

            self._tasks_info[name]['task_kwargs'] = _task_kwargs

        if _index is not None:
            self._tasks_info[name]['index'] = _index

        if _check != self._tasks_info[name]['check']:
            self._tasks_info[name]['check'] = _check

        if _background_color is not None:
            if _background_color == 'default':
                _background_color = None
            self._tasks_info[name]['background_color'] = _background_color

        if _text_color is not None:
            if _text_color == 'default':
                _text_color = None
            self._tasks_info[name]['text_color'] = _text_color

    def load_task_data(self):
        for i, tasks_level in enumerate(self.tasks_level_list[:-1]):
            # hold the last one for now, will need data before load to compare for saving task info
            # check task level list to register tasks at level
            for task in tasks_level:
                index = self._tasks_info[task]['index']
                self._order_task(task, index, update=False)

            # load task info file
            if self.task_data_paths[i]:
                tasks_data = files.read_json_file(self.task_data_paths[i])
                self._load_each_task_data(tasks_data, inheritance=True)

        # order the final level tasks, those are from the asset's class methods
        for task in self.tasks_level_list[-1]:
            index = self._tasks_info[task]['index']
            self._order_task(task, index, update=False)

        # copy to inheritance list
        self._tasks_info_compare = self._tasks_info.copy()
        self._tasks_compare = self._tasks[:]

        # load the last file
        if self.task_data_paths[-1]:
            tasks_data = files.read_json_file(self.task_data_paths[-1])
            self._load_each_task_data(tasks_data, inheritance=False)

    def tasks_registration(self):
        """
        sub classes register all the tasks to the builder here, using self.register_task()
        """
        pass

    def registration(self):
        """
        register and order all tasks, both in-class registration and loading task info files
        """
        self.get_task_data_paths()
        self.tasks_registration()
        self.load_task_data()

    def tree_hierarchy(self):
        hierarchy = []
        for task in self._tasks:
            self._add_child(hierarchy, task)
        return hierarchy

    def export_tasks_info(self, tasks_info):
        """
        compare the given tasks info with existing one in class, save the differences to the builder's folder

        Args:
            tasks_info(list): tasks info from ui
        """
        tasks_info_export = []  # final export tasks info list
        index_previous = 0
        for i, task_info in enumerate(tasks_info):
            task = task_info.keys()[0]
            task_data = task_info[task]
            # reduce task_kwargs
            if 'task_kwargs' in task_data:
                task_kwargs_export = {}
                for key, data in task_data['task_kwargs'].iteritems():
                    task_kwargs_key = {}
                    if 'value' in data:
                        task_kwargs_key.update({'value': data['value']})
                    elif 'default' in data:
                        task_kwargs_key.update({'default': data['default']})
                    if task_kwargs_key:
                        task_kwargs_export.update({key: task_kwargs_key})
                task_data['task_kwargs'] = task_kwargs_export

            # check if exist
            if task not in self._tasks_info_compare:
                # new task added in ui, save all data
                task_data.update({'index': index_previous})
                tasks_info_export.append({task: task_data})
            else:
                # task was in class, check differences
                task_data_update = {}
                for key in ['display', 'task_path', 'parent', 'check', 'text_color', 'background_color']:
                    if key in task_data and key not in self._tasks_info_compare[task]:
                        # update key
                        task_data_update.update({key: task_data[key]})
                    elif key in task_data and task_data[key] != self._tasks_info_compare[task][key]:
                        # key value is different, add to save dictionary
                        task_data_update.update({key: task_data[key]})
                # ui kwargs
                task_kwargs_update = {}
                for key, data in task_data['task_kwargs'].iteritems():
                    if 'value' in data:
                        value = data['value']
                    else:
                        value = data['default']

                    data_compare = self._tasks_info_compare[task]['task_kwargs']
                    if key in data_compare and value != data_compare[key]['default']:
                        task_kwargs_update.update({key: {'default': value}})
                    elif key not in data_compare:
                        task_kwargs_update.update({key: {'default': value}})
                if task_kwargs_update:
                    task_data_update.update({'task_kwargs': task_kwargs_update})

                # check order
                index_orig = self._tasks_compare.index(task)  # get original task position
                if index_orig > 0:
                    task_previous_orig = self._tasks_compare[index_orig - 1]
                else:
                    task_previous_orig = 0

                if index_previous != task_previous_orig:
                    task_data_update.update({'index': index_previous})

                if task_data_update:
                    tasks_info_export.append({task: task_data_update})
            index_previous = task

        # export file
        if tasks_info_export:
            cls_path = inspect.getfile(self.__class__)
            cls_dirname = os.path.dirname(cls_path)
            task_export_path = os.path.join(cls_dirname, 'tasks.tsk')
            files.write_json_file(task_export_path, tasks_info_export)
            logger.info('save builder successfully at {}'.format(task_export_path))

    def _order_task(self, task, index, update=False):
        tasks_num = len(self._tasks)
        index_pop = None
        if isinstance(index, basestring):
            if index in self._tasks:
                index = self._tasks.index(index) + 1
            else:
                index = tasks_num
        elif index is None:
            index = tasks_num

        if update:
            index_pop = self._tasks.index(task)
        self._tasks.insert(index, task)
        if index_pop is not None:
            if index_pop > index:
                index_pop += 1  # because we insert the new item before index_pop, should shift back one
            self._tasks.pop(index_pop)

    def _load_each_task_data(self, tasks_data, inheritance=True):
        for task_info in tasks_data:
            task = task_info.keys()[0]
            task_kwargs = task_info[task]
            if task not in self._tasks_info:
                # new task, register it
                task_kwargs.update({'name': task,
                                    'inheritance': inheritance})
                self.register_task(**task_kwargs)
                # order it
                index = task_kwargs['index']
                self._order_task(task, index, update=False)
            else:
                self.update_task(task, **task_kwargs)
                if 'index' in task_kwargs:
                    index = task_kwargs['index']
                    self._order_task(task, index, update=True)

    def _add_child(self, hierarchy, task):
        task_info = self._get_task_info(task)
        parent = task_info['parent']
        task_info_add = {task: {'task': task_info['task'],
                                'task_path': task_info['task_path'],
                                'display': task_info['display'],
                                'task_kwargs': task_info['task_kwargs'],
                                'section': task_info['section'],
                                'children': [],
                                'inheritance': task_info['inheritance'],
                                'check': task_info['check'],
                                'background_color': task_info['background_color'],
                                'text_color': task_info['text_color']}}
        if parent:
            for hie_info in hierarchy:
                key = hie_info.keys()[0]
                if parent == key:
                    hie_info[parent]['children'].append(task_info_add)
                else:
                    self._add_child(hie_info[key]['children'], task)
        else:
            hierarchy.append(task_info_add)

    def _get_task_info(self, task):
        task_info = self._tasks_info[task]
        return task_info

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


# SUB FUNCTION
def check_level():
    stack = inspect.stack()
    # this is the initial levels went through, if inherited from other builder, it will add more in between
    # 1. button shelf reload signal emit
    # 2. tree widget check save signal emit
    # 3. rig info get builder signal emit
    # 4. tree widget reload builder
    # 5. core builder registration
    # 6. builder tasks registration
    # --- inherit builders tasks registration
    # 7. core builder register task
    # 8. check level
    level = len(stack) - 8
    del stack  # remove this to be safe
    return level


# SUB CLASS
class ObjectView(object):
    def __init__(self, kwargs):
        self.__dict__ = kwargs
