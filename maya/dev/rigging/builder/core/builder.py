# IMPORT PACKAGES

# import os
import os

# import inspect
import inspect

# import utils
import utils.common.variables as variables
import utils.common.modules as modules
import utils.common.files as files


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

        # task info before load current task info, need this to compare for saving the current task info
        self._tasks_inheritance = None
        self._tasks_info_inheritance = None

    @property
    def project(self):
        return self._project

    @property
    def asset(self):
        return self._asset

    @property
    def rig_type(self):
        return self._rig_type

    def register_task(self, **kwargs):
        """
        register task to build script

        Keyword Args:
            name(str): task name
            display(str): task display name
            task(method): task function
            index(str/int): register task at specific index
                            if given string, it will register after the given task
                            the orders may get wrong with layers inheritance,
                            it's recommend to use string unless you want to set at the beginning, which is 0
            parent(str): parent task to the given task
            kwargs(dict): task kwargs
            section(str): register task in specific section (normally for in-class method)
                          'pre_build', 'build', 'post_build', default is 'post_build'
        """

        # get kwargs
        _name = variables.kwargs('name', '', kwargs, short_name='n')
        _display = variables.kwargs('display', '', kwargs, short_name='dis')
        _index = variables.kwargs('index', None, kwargs, short_name='i')
        _task = variables.kwargs('task', None, kwargs, short_name='tsk')
        _parent = variables.kwargs('parent', '', kwargs, short_name='p')
        _kwargs = variables.kwargs('kwargs', {}, kwargs)
        _section = variables.kwargs('section', 'post_build', kwargs)

        _inheritance = variables.kwargs('_inheritance', None, kwargs)  # this is not for user, use for loading task info

        if _inheritance is None:
            _inheritance = check_inheritance()  # check if the task is referenced or created in the class

        if not _display:
            _display = _name

        # get task
        if inspect.ismethod(_task):
            # in class method, get method name for ui display
            _task_path = _task.__name__
            _task_kwargs = _kwargs
        else:
            # imported task, get task object
            _task_path = _task
            task_import, task_function = modules.import_module(_task)
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
                      'index': _index}

        self._tasks_info.update({_name: _task_info})
        self._tasks.append(_name)

        # get index
        # if isinstance(_index, basestring):
        #     if _index in self._tasks:
        #         _index = self._tasks.index(_index) + 1
        #
        # self._tasks.insert(_index, _name)

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
        """
        _task_kwargs = {}
        # get kwargs
        _display = variables.kwargs('display', '', kwargs, short_name='dis')
        _task = variables.kwargs('task', None, kwargs, short_name='tsk')
        _parent = variables.kwargs('parent', '', kwargs, short_name='p')
        _kwargs = variables.kwargs('kwargs', {}, kwargs)
        _index = variables.kwargs('index', len(self._tasks), kwargs, short_name='i')

        if _display:
            self._tasks_info[name]['display'] = _display

        if _task:
            # imported task, get task object
            _task_path = _task
            task_import, task_function = modules.import_module(_task)
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

        if _kwargs:
            _kwargs_orig = self._tasks_info[name]['task_kwargs']
            # swap orig to _task_kwargs preset if task changed
            if _task_kwargs:
                for key in _kwargs_orig:
                    if key in _task_kwargs:
                        dv_orig = _kwargs_orig[key]['default']
                        dv = _task_kwargs[key]['default']
                        if type(dv_orig) == type(dv):
                            # same type of input, swap
                            _task_kwargs[key]['default'] = dv_orig
                            # check if value, if value, swap
                            if 'value' in _kwargs_orig[key]:
                                _task_kwargs[key].update({'value': _kwargs_orig[key]['value']})
                _kwargs_orig = _task_kwargs
            _kwargs_orig.update(_kwargs)
            if 'value' in _kwargs_orig and _kwargs_orig['value'] is not None:
                _kwargs_orig.update({'default': _kwargs_orig['value']})
                _kwargs_orig.pop('value')
            self._tasks_info[name]['task_kwargs'] = _kwargs_orig

        if _index:
            self._tasks_info[name]['index'] = _index

    def registration(self):
        """
        sub classes register all the tasks to the builder here, using self.register_task()
        """
        pass

    def get_task_data_paths(self):
        """
        get task data paths from both current class and parent classes
        """
        for cls in inspect.getmro(self.__class__)[:-1]:
            path_cls = inspect.getfile(cls)
            path_dirname = os.path.dirname(path_cls)
            path_task_data = os.path.join(path_dirname, 'task_data.tsk')
            if os.path.exists(path_task_data):
                self.task_data_paths.append(path_task_data)
            else:
                self.task_data_paths.append('')

    def load_task_data(self):
        for data_path in self.task_data_paths[:-1]:
            # hold the last one, will need data before load the last for saving
            if data_path:
                task_data = files.read_json_file(data_path)
                self._load_each_task_data(task_data)

        # reorder tasks
        task_order_copy = self._tasks[:]
        self._reorder_tasks(task_order_copy)

        # copy to inheritance list
        self._tasks_info_inheritance = self._tasks_info.copy()
        self._tasks_inheritance = self._tasks[:]

        # load the last file
        if self.task_data_paths[-1]:
            task_data = files.read_json_file(self.task_data_paths[-1])
            self._load_each_task_data(task_data)

            # reorder the last items
            tasks = task_data.keys()[:]
            self._reorder_tasks(tasks)

    def _load_each_task_data(self, task_data):
        for task_name, task_kwargs in task_data.iteritems():
            if task_name not in self._tasks_info:
                # new task, register it
                task_kwargs.update({'name': task_name,
                                    'inheritance': True})
                self.register_task(**task_kwargs)
            else:
                self.update_task(task_name, **task_kwargs)

    def _reorder_tasks(self, tasks):
        for task in tasks:
            if 'index' in self._tasks_info[task]:
                index = self._tasks_info[task]
                # take out task from list first
                self._tasks.remove(task)
                # get index
                if isinstance(index, basestring):
                    if index in self._tasks:
                        index = self._tasks.index(index) + 1
                        self._tasks.insert(index, task)
                else:
                    self._tasks.insert(index, task)

    def tree_hierarchy(self):
        hierarchy = []
        for task in self._tasks:
            self._add_child(hierarchy, task)
        return hierarchy

    def _add_child(self, hierarchy, task):
        task_info = self._get_task_info(task)
        parent = task_info['parent']
        task_info_add = {task: {'task': task_info['task'],
                                'task_path': task_info['task_path'],
                                'display': task_info['display'],
                                'task_kwargs': task_info['task_kwargs'],
                                'section': task_info['section'],
                                'children': [],
                                'inheritance': task_info['inheritance']}}
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
def check_inheritance():
    stack = inspect.stack()
    if len(stack) == 5:
        # 4 should be called from current class, but we have to reference one more level in ui
        inheritance = False
    else:
        # calling from parent classes
        inheritance = True
    del stack  # remove this to be safe
    return inheritance


# SUB CLASS
class ObjectView(object):
    def __init__(self, kwargs):
        self.__dict__ = kwargs
