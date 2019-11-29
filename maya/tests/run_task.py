def _run_task(self, items=None, collect=True, section=None, ignore_check=False, skip_build=False):
    """
    run task

    Keyword Args:
        items(QItem): None will be the root, default is None
        collect(bool): loop downstream tasks, default is True
        section(list): run for specific section, None will run for all, default is None
                       ['pre_build', 'build', 'post_build']
        ignore_check(bool): ignore the item's check state if True, default is False
        skip_build(bool): skip task section already built if True, or will re-run the section, default is False
    """
    if section is None:
        section = ['pre_build', 'build', 'post_build']

    running_role = {'pre_build': ROLE_TASK_PRE,
                    'build': ROLE_TASK_RUN,
                    'post_build': ROLE_TASK_POST}

    # collect items
    if isinstance(items, list):
        items_run = []
        for item in items:
            if collect and item not in set(items_run):
                items_run += self._collect_items(item)
                ignore_check = False
            else:
                items_run = items
                ignore_check = True
    else:
        # because the function can be only triggered by ui,
        # it can only happens at None with collect set to True, or single item with/without collect
        if collect:
            items_run = self._collect_items(item=items)
            ignore_check = False
        else:
            items_run = [items]
            ignore_check = True

    progress_max = len(items_run) * len(section)

    clear_maya_progress_bar_cache(self.maya_progress_bar, progress_max)  # clear out the cache

    # shoot signal to progress bar
    self.SIGNAL_PROGRESS_INIT.emit(len(items_run) * len(section))

    # loop in each task
    item_count = float(len(items_run))
    break_checker = False  # escape the loop if maya progress bar end by user (ESC pressed)
    for i, sec in enumerate(section):
        if break_checker:
            break
        role = running_role[sec]
        for j, item in enumerate(items_run):
            # get task info to run task
            task_info = item.data(0, ROLE_TASK_INFO)
            # get check state
            check_state = item.checkState(0)
            # convert to bool
            if check_state == Qt.Checked or ignore_check:
                check_state = True
            else:
                check_state = False
            # get task kwargs reduced
            task_info['task_kwargs'] = self._reduce_task_kwargs(task_info['task_kwargs'])
            # get task running state, skipped if already run
            item_running_state = item.data(0, role)
            if item_running_state == 0 or not skip_build:
                # either the item haven't run or we do not skip task already built
                # check progress bar in case user want to stop
                if cmds.progressBar(self.maya_progress_bar, query=True, isCancelled=True):
                    # escape from loop
                    self.SIGNAL_ERROR.emit()
                    logger.warning('Task process is stopped by user')
                    break_checker = True
                    break

                # run task
                # get children item
                # get child count
                child_count = item.childCount()
                # children tasks attr name
                sub_tasks = []
                # loop downstream
                for index_child in range(child_count):
                    # get item
                    child_item = item.child(index_child)
                    # get child task info
                    child_task_info = child_item.data(0, ROLE_TASK_INFO)
                    # get check state
                    child_check_state = child_item.checkState(0)
                    # add to pack if checked
                    if child_check_state == Qt.Checked:
                        sub_tasks.append(child_task_info['attr_name'])
                    task_result = self.builder.run_task(task_info, section=sec, check=check_state, sub_tasks=sub_tasks)
                    self._execute_setting(item, task_result)





            # get task info
            task_info = item.data(0, ROLE_TASK_INFO)
            task_type = item.data(0, ROLE_TASK_TYPE)
            task_display = item.text(0)
            check_state = item.checkState(0)
            # reduce task kwargs, because original one contains lots of ui info we don't need
            task_kwargs = self._reduce_task_kwargs(task_info['task_kwargs'])

            # check if the item is unchecked
            if check_state == Qt.Checked or ignore_check:
                # get task running state, skipped if already run
                item_running_state = item.data(0, role)
                if item_running_state == 0 or not skip_build:
                    # item haven't run, or need re-run, start running task
                    # check progress bar
                    if cmds.progressBar(self.maya_progress_bar, query=True, isCancelled=True):
                        # escape from loop
                        self.SIGNAL_ERROR.emit()
                        logger.warning('Task process is stopped by the user')
                        break_checker = True
                        break

                    # check item type
                    if task_type == 'method':
                        # get section registered
                        section_init = task_info['section']

                        if sec != section_init:
                            # skip
                            item.setData(0, role, 1)
                        else:
                            # try to run in class method
                            try:
                                task_func = task_info['task']
                                task_return = task_func(**task_kwargs)
                                message = ''
                                task_return_state = 1  # success
                                if isinstance(task_return, basestring):
                                    message = task_return  # override message to store in icon
                                self._execute_setting(item, task_return_state, 'method', task_display, role, sec,
                                                      message)
                            except Exception:
                                traceback_str = traceback.format_exc()
                                self._error_setting(item, traceback_str, role)

                    # check if registered function is a function (mainly for callback)
                    elif task_type == 'callback':
                        # try to run function
                        try:
                            if task_kwargs[sec]:
                                # if section has callback code
                                task_func = task_info['task']
                                task_func(task_kwargs[sec])
                            self._execute_setting(item, 1, 'function', task_display, role, sec, '')
                        except Exception:
                            traceback_str = traceback.format_exc()
                            self._error_setting(item, traceback_str, role)
                    else:
                        # Task is an imported task
                        # try to run task
                        try:
                            # get task name
                            task_name = task_info['attr_name']
                            task_obj = getattr(self.builder, task_name)

                            if sec == 'pre_build':
                                # register input data
                                task_obj.kwargs_input = task_kwargs
                                # check if task is duplicate
                                if task_type == 'copy':
                                    # check target task is a pack or not
                                    attr_name_target = task_kwargs.get('duplicate_component', None)
                                    if attr_name_target:
                                        task_target = modules.get_obj_attr(self.builder, attr_name_target)
                                        if task_target:
                                            # check if the target is pack, override the parameter if so
                                            task_type = task_target.task_type

                                # check if task is pack
                                if task_type == 'pack':
                                    # get child count
                                    child_count = item.childCount()
                                    # loop downstream
                                    for index_child in range(child_count):
                                        # get item
                                        child_item = item.child(index_child)
                                        # get child task info
                                        child_task_info = child_item.data(0, ROLE_TASK_INFO)
                                        # get check state
                                        child_check_state = child_item.checkState(0)
                                        # add to pack if checked
                                        if child_check_state == Qt.Checked:
                                            task_obj.sub_components_attrs.append(child_task_info['attr_name'])
                            # run task
                            func = getattr(task_obj, sec)
                            func()
                            return_signal = task_obj.signal
                            message = task_obj.message

                            self._execute_setting(item, return_signal, 'task', task_display, role, sec, message)

                        except Exception:
                            traceback_str = traceback.format_exc()
                            self._error_setting(item, traceback_str, role)

            # progress bar grow
            cmds.progressBar(self.maya_progress_bar, edit=True, step=1)

            # emit signal
            self.SIGNAL_PROGRESS.emit(item_count * i + j + 1)

    # end progress bar
    cmds.progressBar(self.maya_progress_bar, edit=True, endProgress=True)

    # emit reset signal
    self.SIGNAL_RESET.emit()