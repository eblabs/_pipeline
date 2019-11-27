# IMPORT PACKAGES

# import os
import os

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.files as files
import utils.common.logUtils as logUtils
import utils.common.modules as modules
import utils.common.naming as naming
import utils.common.attributes as attributes
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
        control space(dict): [ctrl_space] add spaces for controls after loading space data
                                          template is {control_name: {space_name: {'input_matrix_attr': matrix_attr,
                                                                                   'space_type': []}}}
                                          control name can be control's transform node in maya,
                                          or current component control attr
                                          input matrix attr can be component's matrix attribute, or maya matrix attr
                                          space type has 'parent', 'point', 'orient', 'scale'
                                          point/orient won't be added if control already had parent space,
                                          same for the opposite way, all depends on which one will be added first
                                          there are check boxes for control and space,
                                          user can turn it off if don't want to add it
    """

    def __init__(self, **kwargs):
        self.ctrl_space = None
        super(Space, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.template.base.puppet.space'

    def register_kwargs(self):
        super(Space, self).register_kwargs()

        self.register_attribute('control space', {}, attr_name='ctrl_space', attr_type='dict', key_edit=True,
                                template='space_list', checkable=True, val_edit=False,
                                hint="add spaces for controls after loading space data\n"
                                     "template is {control_name: {space_name: {'input_matrix_attr': matrix_attr,\n"
                                     "                                         'space_type': []}}}\n"
                                     "control name can be transform node name in maya, or component's control attr\n"
                                     "space types has 'parent', 'point', 'orient', 'scale'\n"
                                     "point/orient won't be added if control already had parent space\n"
                                     "same for the opposite way, depends on which on added first")

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
                        # loop in each space type
                        for space_type, space_type_info in ctrl_space_info.iteritems():
                            if space_type not in space_info_load[ctrl]:
                                space_info_load[ctrl].update({space_type: space_type_info})
                            else:
                                # loop in each space
                                for key, input_attr in space_type_info['space'].iteritems():
                                    if key not in space_info_load[ctrl][space_type]['space']:
                                        space_info_load[ctrl][space_type]['space'].update({key: input_attr})

        # get space info from ctrl_space attr
        if self.ctrl_space:
            for ctrl, ctrl_space_info in self.ctrl_space.iteritems():
                # get ctrl name fist
                # check if ctrl is an object attr first
                ctrl_name = modules.get_obj_attr(self._parent, ctrl)
                if not ctrl_name:
                    # check if it's a maya node in scene
                    if cmds.objExists(ctrl):
                        ctrl_name = ctrl

                if ctrl_name:
                    # skip if not, means there is no such ctrl in the scene
                    if ctrl_name not in space_info_load:
                        # add ctrl to space_info_load
                        space_info_load.update({ctrl_name: {}})

                        for ctrl_space_data in ctrl_space_info:
                            space_name = ctrl_space_data.keys()[0]
                            input_attr = ctrl_space_data[space_name]['input_matrix_attr']
                            # check input attr
                            input_attr_name = modules.get_obj_attr(self._parent, input_attr)
                            if not input_attr_name and attributes.check_attr_exists(input_attr):
                                # check if it's a maya attribute
                                input_attr_name = input_attr

                            if input_attr_name:
                                space_info_add = {space_name: input_attr_name}
                                # otherwise skip the current space because no input exist
                                for ctrl_space_type in ctrl_space_data[space_name]['space_type']:
                                    if ctrl_space_type in space_info_load[ctrl_name]:
                                        # update directly
                                        space_info_load[ctrl_name][ctrl_space_type]['space'].update(space_info_add)
                                    elif (ctrl_space_type in ['point', 'orient'] and
                                            'parent' in space_info_load[ctrl_name]):
                                        pass
                                    elif ctrl_space_type == 'parent' and ('point' in space_info_load[ctrl_name] or
                                                                          'orient' in space_info_load[ctrl_name]):
                                        pass
                                    else:
                                        # update space
                                        space_info_add = {ctrl_space_type: space_info_add}
                                        space_info_load[ctrl_name][ctrl_space_type].update(space_info_add)

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
