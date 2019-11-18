# IMPORT PACKAGES

# import os
import os

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.files as files
import utils.common.logUtils as logUtils
import utils.common.naming as naming
import utils.rigging.controls as controls

# import task
import dev.rigging.task.core.controlData as controlData

# CONSTANT
logger = logUtils.logger


# CLASS
class Space(controlData.ControlData):
    """
    load and save spaces for controls

    Keyword Args:
        data(list): [data_info] list of data path,
                                template is [{'project': '', 'asset': '', 'rig_type': '', 'task': ''}]
        controls(list): [ctrls] list of controls need to be loaded, empty list will load data for all controls.
                                It support * and ? for multiple nodes, like 'ctrl_l_*_???' or 'ctrl_m_*'
        exceptions(list): [ctrls_exc] list of controls doesn't need to be loaded, will skip those controls when loading
                                      data. it support * and ? for multiple nodes, like 'ctrl_l_*_???' or 'ctrl_m_*'
    """

    def __init__(self, **kwargs):
        super(Space, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.template.base.puppet.space'
