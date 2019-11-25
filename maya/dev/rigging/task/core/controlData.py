# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import rigData
import rigData


# CLASS
class ControlData(rigData.RigData):
    """
    base class for loading control data

    used for tasks need load data for controllers (control shapes, spaces, lock hide, etc)

    Keyword Args:
        data(list): list of data path

        controls(list): [ctrls] list of controls need to be loaded, empty list will load data for all controls.
                                It support * and ? for multiple nodes, like 'ctrl_l_*_???' or 'ctrl_m_*'
        exceptions(list): [ctrls_exc] list of controls doesn't need to be loaded, will skip those controls when loading
                                      data. it support * and ? for multiple nodes, like 'ctrl_l_*_???' or 'ctrl_m_*'
    """
    def __init__(self, **kwargs):
        self.ctrls_list = None
        self.exc_list = None

        super(ControlData, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.core.controlData'
        self.control_list = []
        self.exception_list = []

    def register_kwargs(self):
        super(ControlData, self).register_kwargs()

        self.register_attribute('controls', [], attr_name='ctrls_list', attr_type='list', select=True,
                                hint="list of controls need to be loaded, empty list will load data for all controls."
                                     "\nIt support * and ? for multiple nodes, like 'ctrl_l_*_???' or 'ctrl_m_*'")

        self.register_attribute('exceptions', [], attr_name='exc_list', attr_type='list', select=True,
                                hint="list of controls doesn't need to be loaded, \nwill skip those controls when "
                                     "loading data. \nit support * and ? for multiple nodes, "
                                     "like 'ctrl_l_*_???' or 'ctrl_m_*'")

    def post_build(self):
        super(ControlData, self).post_build()
        self.load_data()

    def get_data(self):
        super(ControlData, self).get_data()

        # get controls list
        for ctrl in self.ctrls_list:
            ctrl_transforms = cmds.ls(ctrl, type='transform')
            if ctrl_transforms:
                self.control_list += ctrl_transforms

        # get exception list
        for ctrl in self.exc_list:
            ctrl_transforms = cmds.ls(ctrl, type='transforms')
            if ctrl_transforms:
                self.exception_list += ctrl_transforms
