# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import task
import dev.rigging.task.core.task as task


# CLASS
class NewScene(task.Task):
    """create new scene"""
    def __init__(self, **kwargs):
        super(NewScene, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.base.newScene'

    def pre_build(self):
        super(NewScene, self).pre_build()
        cmds.file(f=True, new=True)
