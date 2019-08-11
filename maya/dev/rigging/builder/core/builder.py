# IMPORT PACKAGES

# import os
import os

# import inspect
import inspect

# import utils
import utils.common.variables as variables
import utils.common.modules as modules


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
            task(method): task function
            index(str/int): register task at specific index
                            if given string, it will register after the given task
            parent(str): parent task to the given task
            kwargs(dict): task kwargs
            section(str): register task in specific section (normally for in-class method)
                          'pre_build', 'build', 'post_build', default is 'post_build'
        """

        # get kwargs
        _name = variables.kwargs('name', '', kwargs, short_name='n')
        _display = variables.kwargs('display', '', kwargs, short_name='dis')
        _task = variables.kwargs('task', None, kwargs, short_name='tsk')
        _index = variables.kwargs('index', len(self._tasks), kwargs, short_name='i')
        _parent = variables.kwargs('parent', '', kwargs, short_name='p')
        _kwargs = variables.kwargs('kwargs', {}, kwargs)
        _section = variables.kwargs('section', 'post_build', kwargs)

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
            for key, item in _kwargs.iteritems():
                _task_kwargs.update({key: item})

        # add task info to class as attribute
        _task_info = {'task': _task,
                      'task_path': _task_path,
                      'display': _display,
                      'task_kwargs': _task_kwargs,
                      'parent': _parent,
                      'section': _section,
                      'inheritance': _inheritance}

        self._tasks_info.update({_name: _task_info})

        # get index
        if isinstance(_index, basestring):
            if _index in self._tasks:
                _index = self._tasks.index(_index) + 1

        self._tasks.insert(_index, _name)

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
            path_task_data = os.path.join(path_dirname, 'task_data.taskinfo')
            if os.path.exists(path_task_data):
                self.task_data_paths.append(path_task_data)
            else:
                self.task_data_paths.append('')
        self.task_data_paths.reverse()

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
