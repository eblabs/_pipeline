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
import dev.rigging.task.core.rigData as rigData

# CONSTANT
CTRL_SHAPE_INFO_NAME = 'control_shapes'
logger = logUtils.logger


# CLASS
class ControlShape(rigData.RigData):
    """
    load and save control shapes

    Keyword Args:
        data(list): [data_info] list of data path,
                                template is [{'project': '', 'asset': '', 'rig_type': '', 'task': ''}]
        controls(list): [ctrls] list of controls need to be loaded, empty list will load all control shapes from data
                                it support * and ? for multiple nodes, like 'ctrl_l_*_???' or 'ctrl_m_*'
        exceptions(list): [ctrls_exc] list of controls doesn't need to be loaded, will skip those controls when loading
                                      data. it support * and ? for multiple nodes, like 'ctrl_l_*_???' or 'ctrl_m_*'
        size(float): [size] scale controls shapes uniformly, default is 1

    Properties:
        name(str): task's name in builder
        task(str): task's path
    """

    def __init__(self, **kwargs):
        self.ctrls_list = None
        self.exc_list = None
        self.ctrl_size = None
        super(ControlShape, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.template.base.puppet.controlShape'
        self.control_list = []
        self.exception_list = []

    def register_kwargs(self):
        super(ControlShape, self).register_kwargs()

        self.register_attribute('controls', [], attr_name='ctrls_list', attr_type='list', select=True,
                                hint="list of controls need to be loaded, empty list will load all control shapes from "
                                     "data.\n it support * and ? for multiple nodes, like 'ctrl_l_*_???' or 'ctrl_m_*'")

        self.register_attribute('exceptions', [], attr_name='exc_list', attr_type='list', select=True,
                                hint="list of controls doesn't need to be loaded, \nwill skip those controls when "
                                     "loading data. \nit support * and ? for multiple nodes, "
                                     "like 'ctrl_l_*_???' or 'ctrl_m_*'")

        self.register_attribute('size', 1.0, attr_name='ctrl_size', attr_type='float', min=0,
                                hint="scale controls shapes uniformly, default is 1")

    def get_data(self):
        super(ControlShape, self).get_data()

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

    def load_data(self):
        super(ControlShape, self).load_data()
        # loop in each control shape info file
        for path in self.data_path:
            controls.load_ctrl_shape_info(path, control_list=self.control_list, exception_list=self.exception_list,
                                          size=self.ctrl_size)

    def save_data(self):
        super(ControlShape, self).save_data()
        # list all controls
        sel = cmds.ls('{}_*'.format(naming.Type.control), type='transform')
        if sel:
            # save control shape info
            controls.export_ctrl_shape(sel, self.save_data_path, name=CTRL_SHAPE_INFO_NAME)

    def update_data(self):
        super(ControlShape, self).update_data()
        ctrl_shape_info = {}

        # get data
        ctrl_shape_path = os.path.join(self.save_data_path, CTRL_SHAPE_INFO_NAME + controls.CTRL_SHAPE_INFO_FORMAT)
        if os.path.exists(ctrl_shape_path):
            ctrl_shape_info = files.read_json_file(ctrl_shape_path)

        # list selection
        sel = cmds.ls(selection=True)
        if sel:
            for s in sel:
                ctrl_info = controls.get_ctrl_shape_info(s)
                if ctrl_info:
                    ctrl_shape_info.update(ctrl_info)
            # save file
            if ctrl_shape_info:
                files.write_json_file(ctrl_shape_path, ctrl_shape_info)
                logger.info("update {} to path {} successfully".format(
                    CTRL_SHAPE_INFO_NAME + controls.CTRL_SHAPE_INFO_FORMAT,
                    ctrl_shape_path))
            else:
                logger.warn("no control node selected, skipped")
        else:
            logger.warning("nothing selected, skipped")
