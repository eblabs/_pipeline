# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.naming as naming
import utils.common.transforms as transforms
import utils.common.attributes as attributes
import utils.rigging.controls as controls

# import task
import dev.rigging.task.core.task as task


# CLASS
class ImportModel(task.Task):
    """
    import model for current asset
    """

    def __init__(self, **kwargs):
        super(ImportModel, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.base.baseNode'
        self.model_path = []

    def register_kwargs(self):
        super(ImportModel, self).register_kwargs()

        self.register_attribute('model', [{'model_type': '', 'resolution': []}], attr_name='model_path', select=False,
                                template='model_data', hint='load model from following paths')

    def pre_build(self):
        super(ImportModel, self).pre_build()


