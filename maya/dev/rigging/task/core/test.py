# IMPORT PACKAGES

# import os
import os

# import utils
import utils.rigging.buildUtils as buildUtils

# import task
import task

# ICON
import dev.rigging.builder.ui.widgets.icons as icons

import time


# CLASS
class Test(task.Task):
    """
    base class for loading data

    used for tasks need load data (deformers, controlShapes, models etc)

    all tasks with load data function should inherit from this class

    Keyword Args:
        data(list): list of data path
    """
    def __init__(self, **kwargs):
        super(Test, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.core.test'

    def pre_build(self):
        super(Test, self).pre_build()
        self.sleep()

    def build(self):
        super(Test, self).build()
        self.sleep()

    def post_build(self):
        super(Test, self).post_build()
        self.sleep()

    @ staticmethod
    def sleep():
        for i in range(10):
            time.sleep(1)
            print i
