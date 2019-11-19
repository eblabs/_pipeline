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
SPACE_INFO_NAME = 'spaces'
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

    def load_data(self):
        super(Space, self).load_data()

        space_info_load = {}

        # loop in each path
        for path in self.data_path:
            space_data_path = os.path.join(path, SPACE_INFO_NAME + controls.CTRL_SPACE_INFO_FORMAT)
            if os.path.exists(space_data_path):
                space_data = files.read_json_file(space_data_path)
                for ctrl, ctrl_space_info in space_data.iteritems():
                    if ctrl not in space_info_load:
                        space_info_load.update({ctrl: ctrl_space_info})
                    else:
                        # get remove list
                        remove_space_type = space_info_load[ctrl].get('remove', [])
                        # loop in each space type
                        for space_type, space_type_info in ctrl_space_info.iteritems():
                            if space_type not in remove_space_type:
                                # otherwise will skip
                                if space_type not in space_info_load[ctrl]:
                                    space_info_load[ctrl].update({space_type: space_type_info})
                                else:
                                    # get space remove list
                                    remove_space_key = space_info_load[ctrl][space_type].get('remove', [])
                                    # loop in each space
                                    for key, input_attr in space_type_info['space'].iteritems():
                                        if key not in remove_space_key and \
                                                key not in space_info_load[ctrl][space_type]['space']:
                                            space_info_load[ctrl][space_type]['space'].update({key: input_attr})
                                    # add current remove list
                                    remove_space_key_current = space_type_info.get('remove', [])
                                    remove_space_key += remove_space_key_current
                                    space_info_load[ctrl][space_type].update({'remove': remove_space_key})
                                    # check default value
                                    if not space_info_load[ctrl][space_type]['default']:
                                        # use the current one's default
                                        space_info_load[ctrl][space_type]['default'] = space_type_info['default']
                        # add current remove list
                        remove_space_type_current = ctrl_space_info.get('remove', [])
                        remove_space_type += remove_space_type_current
                        space_info_load[ctrl].update({'remove': remove_space_type})

        # build spaces
        controls.build_spaces_from_info(space_info_load, control_list=self.control_list,
                                        exception_list=self.exception_list)

    def save_data(self):
        super(Space, self).save_data()
        # this is temporary, should call a custom ui, check previous data, and automatically find the differences

        # list all controls
        sel = cmds.ls('{}_*'.format(naming.Type.control), type='transform')
        if sel:
            # save control shape info
            controls.export_space_info(sel, self.save_data_path, name=SPACE_INFO_NAME)

    def update_data(self):
        super(Space, self).update_data()
        # this should call the same ui as save data, it should have option there to either update or override
        pass
