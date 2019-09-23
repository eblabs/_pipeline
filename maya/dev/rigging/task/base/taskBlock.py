# IMPORT PACKAGES

# import task
import dev.rigging.task.core.task as task


# CLASS
class TaskBlock(task.Task):
    """task block, empty task to separate other tasks"""
    def __init__(self, **kwargs):
        super(TaskBlock, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.base.taskBlock'
