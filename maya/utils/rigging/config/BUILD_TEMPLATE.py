'''
# IMPORT PACKAGES

# import utils
import utils.common.modules as modules
import utils.common.naming as naming
import utils.common.attributes as attributes
import utils.common.hierarchy as hierarchy
import utils.common.transforms as transforms
import utils.rigging.controls as controls
import utils.rigging.joints as joints

# LOGGER
import utils.common.logUtils as logUtils
logger = logUtils.get_logger(name='builder', level='info')

# INHERIT CLASS
BUILDER_INHERIT_PATH = TEMP_BUILDER_PATH
cls, function = modules.import_module(BUILDER_INHERIT_PATH)
CLASS_INHERIT = getattr(cls, function)

# ASSET INFO
PROJECT = TEMP_PROJECT_NAME
ASSET = TEMP_ASSET_NAME
RIG_TYPE = TEMP_RIG_TYPE_NAME

# CLASS
class Builder(CLASS_INHERIT):
    """
    build script for TEMP_PROJECT_NAME - TEMP_ASSET_NAME - TEMP_RIG_TYPE_NAME
    """
    def __init__(self):
        super(Builder, self).__init__()
        self._project = PROJECT
        self._asset = ASSET
        self._rig_type = RIG_TYPE

    def tasks_registration(self):
        """
        register all the tasks to the builder here, using self.register_task()

        template:
            self.register_task(name=task_name,
                               task=task_path,
                               display=display_name,
                               index=index,
                               parent=parent_task,
                               kwargs=kwargs,
                               section=section)

        self.register_task Keyword Args:
            name(str): task name
            task(method): task function
            index(str/int): register task at specific index
                            if given string, it will register after the given task
            parent(str): parent task to the given task
            kwargs(dict): task kwargs
            section(str): register task in specific section (normally for in-class method)
                          'pre_build', 'build', 'post_build', default is 'post_build'
        """
        super(Builder, self).tasks_registration()
'''