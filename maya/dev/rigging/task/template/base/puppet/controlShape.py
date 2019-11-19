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
CTRL_SHAPE_INFO_NAME = 'control_shapes'
logger = logUtils.logger


# CLASS
class ControlShape(controlData.ControlData):
    """
    load and save control shapes

    Keyword Args:
        data(list): [data_info] list of data path,
                                template is [{'project': '', 'asset': '', 'rig_type': '', 'task': ''}]
        controls(list): [ctrls] list of controls need to be loaded, empty list will load data for all controls.
                                It support * and ? for multiple nodes, like 'ctrl_l_*_???' or 'ctrl_m_*'
        exceptions(list): [ctrls_exc] list of controls doesn't need to be loaded, will skip those controls when loading
                                      data. it support * and ? for multiple nodes, like 'ctrl_l_*_???' or 'ctrl_m_*'
        size(float): [size] scale controls shapes uniformly, default is 1
    """

    def __init__(self, **kwargs):
        self.ctrl_size = None
        super(ControlShape, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.template.base.puppet.controlShape'

    def register_kwargs(self):
        super(ControlShape, self).register_kwargs()

        self.register_attribute('size', 1.0, attr_name='ctrl_size', attr_type='float', min=0,
                                hint="scale controls shapes uniformly, default is 1")

    def load_data(self):
        super(ControlShape, self).load_data()
        ctrl_shape_info_load = {}

        # loop in each path
        for path in self.data_path:
            ctrl_shape_data_path = os.path.join(path, CTRL_SHAPE_INFO_NAME+controls.CTRL_SHAPE_INFO_FORMAT)
            if os.path.exists(ctrl_shape_data_path):
                ctrl_shape_data = files.read_json_file(ctrl_shape_data_path)
                for ctrl, shape_info in ctrl_shape_data.iteritems():
                    if ctrl not in ctrl_shape_info_load:
                        ctrl_shape_info_load.update({ctrl: shape_info})

        # add shape node
        controls.build_ctrl_shape_from_info(ctrl_shape_info_load, control_list=self.control_list,
                                            exception_list=self.exception_list, size=self.ctrl_size)

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
