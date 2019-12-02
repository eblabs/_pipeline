# IMPORT PACKAGES

# import os
import os

# import inspect
import inspect

# import traceback
import traceback

# import utils
import utils.common.variables as variables
import utils.common.modules as modules
import utils.common.files as files
import utils.common.logUtils as logUtils
import utils.common.naming as naming

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

        # pack kwargs override
        # because the pack shares some of the kwargs with its sub components,
        # and we don't want the user to set each separately and keep those the same by themselves
        # the problem is because the pack object register before its sub components,
        # especially when we do mirror, there won't be sub components when we do pack's pre build
        # so we register those override kwargs back to the builder as a dict, with sub components attr name as key,
        # and in each component, we will search the dict to see if anything need to be override before set kwargs
        self.pack_kwargs_override = {}

        # base node task will override this parameter, so components will get base node use it
        self.base_node = None

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
            task_path(method/str): task function, or module path
            index(str/int): register task at specific index
                            if given string, it will register after the given task
            parent(str): parent task to the given task
            task_kwargs(dict): task kwargs
            section(str): register task in specific section (only for in-class method)
                          'pre_build', 'build', 'post_build', default is 'post_build'
            background_color(list): task background color, None will use the default
        """

        # get kwargs
        _name = variables.kwargs('name', '', kwargs, short_name='n')
        _display = variables.kwargs('display', '', kwargs, short_name='dis')
        _task_path = variables.kwargs('task_path', None, kwargs, short_name='tsk')
        _index = variables.kwargs('index', None, kwargs, short_name='i')
        _parent = variables.kwargs('parent', '', kwargs, short_name='p')
        _kwargs = variables.kwargs('task_kwargs', {}, kwargs)
        _section = variables.kwargs('section', 'post_build', kwargs)
        _background_color = variables.kwargs('background_color', None, kwargs)

        # kwargs for loading task info only, not for user
        _lock = variables.kwargs('lock', True, kwargs)  # if the task is inherit or in class method
        _check = variables.kwargs('check', 1, kwargs)  # check state in ui
        _in_class = variables.kwargs('in_class', True, kwargs)  # either load from build script or task info file

        # task info to pass to other widget for further use
        _task_info = {}

        if _in_class:
            _level = check_level()  # check if the task is referenced or created in the class
        else:
            _level = None  # load from task info file, no need to put in level list

        if not _display:
            _display = _name  # use the attr name as display name

        _save_data = False

        # get task
        if inspect.ismethod(_task_path):
            # in class method, get method name for ui display
            _task = _task_path
            _task_path = _task_path.__name__
            _task_kwargs = _kwargs
            _task_info.update({'section': _section})  # only in class method has section
            _task_type = 'method'
        else:
            # imported task, get task object
            task_import, task_function = modules.import_module(_task_path)
            _task = getattr(task_import, task_function)
            if inspect.isfunction(_task):
                # function, normally is callback
                _task_kwargs = task_import.kwargs_ui
                _task_type = 'callback'
            else:
                # task class
                task_obj = _task(name=_name, parent=self)
                _task_kwargs = task_obj.kwargs_ui
                _save_data = task_obj.save
                _task_type = task_obj.task_type

                # add attr
                setattr(self, _name, task_obj)  # initialize task object to builder
            # if value in _kwargs, set value as default
            if 'value' in _kwargs and _kwargs['value'] is not None:
                _kwargs.update({'default': _kwargs['value']})
                _kwargs.pop('value')
            # loop in each kwarg in _kwargs and update in _task_kwargs
            for key, item in _kwargs.iteritems():
                if key in _task_kwargs:
                    _task_kwargs[key].update(item)

        # add task info to class as attribute
        _task_info.update({'task': _task,  # task function or task object
                           'task_path': _task_path,
                           'task_type': _task_type,
                           'display': _display,
                           'task_kwargs': _task_kwargs,
                           'parent': _parent,
                           'lock': _lock,
                           'index': _index,
                           'check': _check,
                           'background_color': _background_color,
                           'save_data': _save_data})

        self._tasks_info.update({_name: _task_info})

        if _level is not None:
            self.tasks_level_list[-1 - _level].append(_name)

    def update_task(self, name, **kwargs):
        """
        update registered task's info, used only for load task info from file

        Args:
            name(str): task name

        Keyword Args:
            display(str): task display name
            task_path(method/str): task function or module path
            index(str/int): register task at specific index
                            if given string, it will register after the given task
            parent(str): parent task to the given task
            task_kwargs(dict): task kwargs
            check(int): task check state
            background_color(list): task background color, None will use the inherit color,
                                    use str 'default' to set back to default
        """
        # task kwargs to add back to task info, it will store the task kwargs here temperately if we change task path
        _task_kwargs = {}
        # get kwargs
        _display = variables.kwargs('display', '', kwargs, short_name='dis')
        _task_path = variables.kwargs('task_path', None, kwargs, short_name='tsk')
        _index = variables.kwargs('index', None, kwargs, short_name='i')
        _parent = variables.kwargs('parent', '', kwargs, short_name='p')
        _kwargs = variables.kwargs('task_kwargs', {}, kwargs)
        _check = variables.kwargs('check', 1, kwargs)
        _background_color = variables.kwargs('background_color', None, kwargs)

        if _display:
            self._tasks_info[name]['display'] = _display

        if _task_path:
            # imported task, get task object
            task_import, task_function = modules.import_module(_task_path)
            _task = getattr(task_import, task_function)
            if not inspect.isfunction(_task):
                # task class
                task_obj = _task()
                # override class object to builder
                setattr(self, name, task_obj)
                # get task kwargs
                _task_kwargs = task_obj.kwargs_ui  # get all kwargs from the new task object
            else:
                # callback, it is a function
                _task_kwargs = task_import.kwargs_ui  # get all kwargs from the new task function
            self._tasks_info[name]['task'] = _task
            self._tasks_info[name]['task_path'] = _task_path

        if _parent:
            self._tasks_info[name]['parent'] = _parent

        # override kwargs if has any
        # get original kwargs to compare
        _kwargs_orig = self._tasks_info[name]['task_kwargs'].copy()

        for key, data in _kwargs.iteritems():
            if key in _kwargs_orig:
                # update with the kwargs values given by the input
                _kwargs_orig[key]['default'] = data['default']
            elif key in _kwargs_orig:
                # get kwargs values from the original task info,
                # that way we can keep the changes even if we switch the task
                default_value = _task_kwargs[key]['default']
                orig_value = _kwargs_orig[key]['default']
                if type(default_value) == type(orig_value) and default_value != orig_value:
                    _task_kwargs[key]['default'] = orig_value

        if _task_kwargs:
            # means we change the task path, it's now a different task,
            # we need to see if anything from original can be swapped.
            # get original kwargs to compare
            _kwargs_orig = self._tasks_info[name]['task_kwargs']

            for key, data in _task_kwargs.iteritems():
                if key in _kwargs_orig:
                    # get kwargs values from the original task info,
                    # that way we can keep the changes even if we switch the task
                    default_value = _task_kwargs[key]['default']
                    orig_value = _kwargs_orig[key]['default']
                    if type(default_value) == type(orig_value) and default_value != orig_value:
                        _task_kwargs[key]['default'] = orig_value
        else:
            _task_kwargs = self._tasks_info[name]['task_kwargs']

        if _kwargs:
            # check to see if any kwargs need to be updated
            for key, data in _kwargs.iteritems():
                if key in _task_kwargs:
                    _task_kwargs[key]['default'] = data['default']

        self._tasks_info[name]['task_kwargs'] = _task_kwargs  # override task kwargs info

        if _index is not None:
            self._tasks_info[name]['index'] = _index

        if _check != self._tasks_info[name]['check']:
            self._tasks_info[name]['check'] = _check  # only save the check state if changed

        if _background_color is not None:
            if _background_color == 'default':
                _background_color = None  # override the background color to default
            self._tasks_info[name]['background_color'] = _background_color

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
                self._load_each_task_data(tasks_data, lock=True, in_class=False)

        # order the final level tasks, those are from the asset's in class methods
        for task in self.tasks_level_list[-1]:
            index = self._tasks_info[task]['index']
            self._order_task(task, index, update=False)

        # copy to inheritance list, we need these info to compare to save users changes in ui
        self._tasks_info_compare = self._tasks_info.copy()
        self._tasks_compare = self._tasks[:]

        # load the last file
        if self.task_data_paths[-1]:
            tasks_data = files.read_json_file(self.task_data_paths[-1])
            self._load_each_task_data(tasks_data, lock=False, in_class=False)

    def tasks_registration(self):
        """
        sub classes register all the tasks to the builder here, using self.register_task()
        """
        self.register_task(name='task_m_rigInfo', display='Rig Info', task_path=self.rig_info, section='pre_build')

    def registration(self):
        """
        register and order all tasks, both in-class registration and loading task info files
        """
        self.get_task_data_paths()
        self.tasks_registration()
        self.load_task_data()

    def rig_info(self):
        """
        print out rig info
        """
        rig_info = 'RIG INFO\nproject: {}\nasset: {}\nrig type: {}'.format(self._project, self._asset, self._rig_type)
        logger.info(rig_info)  # print in log
        # return rig info to store in icon
        return rig_info

    def tree_hierarchy(self):
        hierarchy = []
        for task in self._tasks:
            self._add_child(hierarchy, task)
        return hierarchy

    def run_task(self, task_info, section=None, check=True, sub_tasks=None):
        """
        run the given task, both ui and code will trigger this function to each run task

        Args:
            task_info(dict): given task information

        Keyword Args:
            section(str): pre_build/build/post_build, default is pre_build
            check(bool): if the item is checked or not, will skip if it is not checked
            sub_tasks(list): tasks names parented to the given item, mainly for pack and module
        """
        # get section
        if not section:
            section = 'pre_build'
        # get sub_tasks
        if not sub_tasks:
            sub_tasks = []

        # task result template for return
        # state: 1 (success), 2 (warning), 0 (error)
        # message: any info need to show in ui
        state = 1,
        message = ''

        if check:
            task_info.update({'sub_tasks': sub_tasks})
            task_type = task_info['task_type']
            # get task running function
            # in class method
            if task_type == 'method':
                task_func = self._run_in_class_method
            elif task_type == 'callback':
                task_func = self._run_callback
            else:
                task_func = self._run_task_object

            try:
                state, message = task_func(task_info, section)
            except:
                # this exception has to be board, because we need to catch all errors here
                state = 0
                message = traceback.format_exc()
        return state, message

    def export_tasks_info(self, tasks_info, save_file=True):
        """
        compare the given tasks info with existing one in class, save the differences to the builder's folder

        Args:
            tasks_info(list): tasks info from ui
        Keyword Args:
            save_file(bool): save the tasks info as a file,
                             will only print out the info if set to False, only for debugging
        """
        tasks_info_export = []  # final export tasks info list

        for i, task_info in enumerate(tasks_info):
            task = task_info.keys()[0]  # get task name
            task_data = task_info[task].copy()  # get task info
            index_previous = task_data['index']  # get the previous task name

            # reduce task_kwargs,
            # because the task info exported from ui contains lots of unused info (min, max etc..)
            # we only care about value, and that's how we save in the compare list as well
            if 'task_kwargs' in task_data:
                task_kwargs_export = {}
                for key, data in task_data['task_kwargs'].iteritems():
                    task_kwargs_key = {}
                    if 'value' in data:
                        task_kwargs_key.update({'default': data['value']})
                    else:
                        task_kwargs_key.update({'default': data['default']})
                    if task_kwargs_key:
                        task_kwargs_export.update({key: task_kwargs_key})
                task_data['task_kwargs'] = task_kwargs_export

            # remove task obj and children from task_data, because JSON can't save object
            task_data.pop('task', None)
            task_data.pop('children', None)

            # check if exist
            if task not in self._tasks_info_compare:
                # new task added in ui, save all data
                tasks_info_export.append({task: task_data})
            else:
                # task was in class, check differences
                task_data_update = {}
                for key in ['display', 'task_path', 'parent', 'check', 'background_color']:
                    if key in task_data and key not in self._tasks_info_compare[task]:
                        # update key
                        task_data_update.update({key: task_data[key]})
                    elif key in task_data and task_data[key] != self._tasks_info_compare[task][key]:
                        # key value is different, add to save dictionary
                        task_data_update.update({key: task_data[key]})
                # ui kwargs
                task_kwargs_update = {}
                data_compare = self._tasks_info_compare[task]['task_kwargs']
                for key, data in task_data['task_kwargs'].iteritems():
                    value = data['default']

                    if key in data_compare and value != data_compare[key]['default']:
                        # save the differences
                        task_kwargs_update.update({key: {'default': value}})
                    elif key not in data_compare:
                        # it's a new kwarg, save it out
                        task_kwargs_update.update({key: {'default': value}})

                if task_kwargs_update:
                    task_data_update.update({'task_kwargs': task_kwargs_update})

                # check order
                index_orig = self._tasks_compare.index(task)  # get original task position

                if index_orig > 0:
                    # find the task name before the task
                    task_previous_orig = self._tasks_compare[index_orig - 1]
                else:
                    # given task is the first one
                    task_previous_orig = 0

                if index_previous != task_previous_orig:
                    task_data_update.update({'index': index_previous})

                if task_data_update:
                    tasks_info_export.append({task: task_data_update})

        # export file
        if save_file:
            # save out the file if anything changed
            if tasks_info_export:
                cls_path = inspect.getfile(self.__class__)
                cls_dirname = os.path.dirname(cls_path)
                # generate task info file path
                task_export_path = os.path.join(cls_dirname, 'tasks.tsk')
                # make a copy so if we destroyed the original task info file by mistake, we can still revert it back
                task_export_copy_path = os.path.join(cls_dirname, 'tasks_copy.tsk_copy')
                # export task info file
                files.write_json_file(task_export_path, tasks_info_export)
                # export copy file
                files.write_json_file(task_export_copy_path, tasks_info_export)
                logger.info('save builder successfully at {}'.format(task_export_path))
        else:
            # only print out the tasks_info_export for debugging
            logger.debug('export task info')
            logger.debug(tasks_info_export)

        return tasks_info_export

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

    def _load_each_task_data(self, tasks_data, lock=True, in_class=True):
        for task_info in tasks_data:
            task = task_info.keys()[0]
            task_kwargs = task_info[task]
            if task not in self._tasks_info:
                # new task, register it
                task_kwargs.update({'name': task,
                                    'lock': lock,
                                    'in_class': in_class})
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
        task_info.update({'children': []})  # add children list for tree build
        task_info_add = {task: task_info}

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

    def _run_task_object(self, task_info, section):
        task_name = task_info['attr_name']
        task_kwargs = task_info['task_kwargs']
        sub_tasks = task_info['sub_tasks']
        task_obj = getattr(self, task_name)

        if section == 'pre_build':
            # register input data
            task_obj.kwargs_input = task_kwargs
            # register sub tasks
            task_obj.sub_tasks = sub_tasks

        # run task
        func = getattr(task_obj, section)
        func()
        state = task_obj.signal
        message = task_obj.message
        return state, message

    @staticmethod
    def reduce_task_kwargs(task_kwargs):
        """
        because task's kwargs has too many information we don't need (like ui info), this function will reduce to
        only have value and attr name, so later on we can plug into task's kwargs_input

        Args:
            task_kwargs(dict): task's kwargs

        Returns:
            task_kwargs_reduce(dict)

        """
        task_kwargs_reduce = {}
        for key, data in task_kwargs.iteritems():
            if 'value' in data and data['value'] is not None:
                val = data['value']
            else:
                val = data['default']
            attr_name = data['attr_name']
            task_kwargs_reduce.update({attr_name: val})
        return task_kwargs_reduce

    @staticmethod
    def _run_in_class_method(task_info, section):
        task_func = task_info['task']
        task_kwargs = task_info['task_kwargs']
        section_init = task_info['section']
        state = 1
        message = ''
        if section == section_init:
            task_return = task_func(**task_kwargs)
            if isinstance(task_return, basestring):
                message = task_return
        return state, message

    @staticmethod
    def _run_callback(task_info, section):
        task_kwargs = task_info['task_kwargs']
        state = 1
        message = ''
        if task_kwargs[section]:
            # if section has callback code
            task_func = task_info['task']
            task_func(task_kwargs[section])
        return state, message


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
