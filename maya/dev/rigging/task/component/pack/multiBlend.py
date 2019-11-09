# IMPORT PACKAGES

# import os
import os

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.logUtils as logUtils
import utils.common.naming as naming
import utils.common.files as files
import utils.common.attributes as attributes
import utils.common.nodeUtils as nodeUtils
import utils.rigging.joints as joints
import utils.rigging.constraints as constraints
import utils.rigging.controls as controls

# import task
import dev.rigging.task.component.core.pack as pack

# CONSTANT
import dev.rigging.task.component.config as config
SPACE_CONFIG_PATH = os.path.join(os.path.dirname(config.__file__), 'SPACE.cfg')
SPACE_CONFIG = files.read_json_file(SPACE_CONFIG_PATH)

logger = logUtils.logger

MODE_CUSTOM = 50


# CLASS
class MultiBlend(pack.Pack):
    """
    base class for multi blend pack, it blends multiple components with mode blend attr, like ik/fk blend rig

    Keyword Args:
        mirror(bool): [mirror] mirror component, default is False
        side(str): [side] component's side, default is middle
        description(str): [description] component's description
        description suffix(str): [description_suffix] if the component nodes description need additional suffix,
                                                      like Ik, Fk etc, put it here
        blueprint joints(list): [bp_jnts] component's blueprint joints
        control_size(float): [ctrl_size] component's controls' size, default is 1.0
        input connection(str):  [input_connect] component's input connection, should be a component's joint's output
                                                matrix, or an existing maya node's matrix attribute
        modes(list): [modes] blend mode for each component, order is the same with the components parented under the
                             pack, the first two will be the defaults
        translate blend(bool) [blend_translate] blend translation, default is True
        rotate blend(bool) [blend_rotate] blend rotation, default is True
        sacle blend(bool) [blend_scale] blend scale, default is False
        localization(bool) [localization] blend transform in local space or world space, default is True

    Properties:
        name(str): task's name in builder
        task(str): task's path

        component(str): component node name
        controls(list): component's controls names
        joints(list): component's joints names
        input_matrix_attr(str): component's input matrix attribute
        input_matrix(list): component's input matrix
        offset_matrix_attr(str): component's offset matrix attribute
        offset_matrix(list): component's offset matrix
        output_matrix_attr(list): component's output matrices attributes
        output_matrix(list): component's output matrices

        sub_components_nodes(list): pack's sub components in builder names
        sub_components_objs(list): pack's sub components objects

        blend_ctrl(str): pack's blend control
        modes(list): pack's mode A&B's names
        modes_index(list): pack's mode A&B's indices
        all_modes(list): pack's all modes names as list
        all_modes_index(list): pack's all modes indices as list
        blend_value(float): pack's blend control's current blend value

    Attributes:
        self.sub_components.[mode](object): by giving the mode name, it will return the sub component object,
                                            like self.sub_components.fk
    """
    def __init__(self, *args, **kwargs):
        self.blend_modes = None
        self.blend_translate = None
        self.blend_rotate = None
        self.blend_scale = None
        self.localization = None
        super(MultiBlend, self).__init__(*args, **kwargs)
        self._task = 'dev.rigging.task.component.pack.multiBlend'
        self._jnts = []
        self._blend_ctrl = None
        self._rvs_blend_attr = None
        self._temp_curve_node = None
        self._index_custom = MODE_CUSTOM
        self._mode_index_list = []

    @ property
    def blend_ctrl(self):
        return self._blend_ctrl

    @ property
    def modes(self):
        mode_a = cmds.getAttr(self._blend_ctrl+'.modeA', asString=True)
        mode_b = cmds.getAttr(self._blend_ctrl+'.modeB', asString=True)
        return [mode_a, mode_b]

    @ property
    def modes_index(self):
        mode_a = cmds.getAttr(self._blend_ctrl + '.modeA', asString=False)
        mode_b = cmds.getAttr(self._blend_ctrl + '.modeB', asString=False)
        return [mode_a, mode_b]

    @ property
    def all_modes(self):
        return attributes.get_enum_names('modeA', node=self._blend_ctrl, as_string=True)

    @ property
    def all_modes_index(self):
        return attributes.get_enum_names('modeA', node=self._blend_ctrl, as_string=False)

    @ property
    def blend_value(self):
        blend_val = cmds.getAttr(self._blend_ctrl+'.blend')
        return blend_val

    def register_kwargs(self):
        super(MultiBlend, self).register_kwargs()
        self.register_attribute('modes', [], attr_name='blend_modes', attr_type='list', select=False, template='str',
                                hint=("blend mode for each component,\n",
                                      "order is the same with the components parented under the pack,\n",
                                      "the first two will be the defaults"))

        self.register_attribute('translate blend', True, attr_name='blend_translate', attr_type='bool',
                                hint='blend translation')

        self.register_attribute('rotate blend', True, attr_name='blend_rotate', attr_type='bool',
                                hint='blend rotation')

        self.register_attribute('scale blend', False, attr_name='blend_scale', attr_type='bool', hint='blend scale')

        self.register_attribute('localization', True, attr_name='localization', attr_type='bool',
                                hint='blend transform in local space or world space')

        self.remove_attribute('offsets')

    def pack_override_kwargs_registration(self):
        super(MultiBlend, self).pack_override_kwargs_registration()
        self.register_override_kwarg('bp_jnts', self.bp_jnts)

    def create_component(self):
        super(MultiBlend, self).create_component()
        # create joints
        self._jnts = joints.create_on_hierarchy(self.bp_jnts, naming.Type.blueprintJoint, naming.Type.joint,
                                                parent=self._joints_grp)

        # create blend control
        self._blend_ctrl = naming.Namer(type=naming.Type.control, side=self.side, description=self.description+'Blend',
                                        index=1).name
        # create temp curve
        self._temp_curve_node = cmds.curve(degree=1, point=[[0, 0, 0], [0, 0, 0]], name='TEMP_CURVE_NODE')
        # rename shape node
        curve_shape = cmds.listRelatives(self._temp_curve_node, shapes=True)[0]
        cmds.rename(curve_shape, self._blend_ctrl)
        # hide blend ctrl
        attributes.set_attrs(self._blend_ctrl+'.visibility', 0, force=True)

        # get modes
        enum_name = ''
        for m in self.blend_modes:
            if m in SPACE_CONFIG:
                mode_index = SPACE_CONFIG[m]
            else:
                mode_index = self._index_custom
                self._index_custom += 1
            self._mode_index_list.append(mode_index)
            enum_name += '{}={}:'.format(m, mode_index)

        # add attr
        attributes.add_attrs(self._blend_ctrl, ['modeA', 'modeB'], attribute_type='enum', enum_name=enum_name[:-1],
                             default_value=self._mode_index_list[:2], keyable=True, channel_box=True)
        cmds.addAttr(self._blend_ctrl, longName='blend', attributeType='float', min=0, max=1, keyable=True)
        attributes.add_attrs(self._blend_ctrl, 'allCtrls', attribute_type='bool', default_value=False, keyable=False,
                             channel_box=True)

        # connect sub component joint vis with pack's rig node vis
        for sub_component_obj in self._sub_components_objs:
            # connect attr
            attributes.connect_attrs(self._component+'.rigNodesVis', sub_component_obj.component+'.jointsVis',
                                     force=True)

        # pass info
        self._ctrls.append(self._blend_ctrl)

    def connect_component(self):
        super(MultiBlend, self).connect_component()
        # rvs blend
        self._rvs_blend_attr = nodeUtils.equation('~{}.blend'.format(self._blend_ctrl), side=self.side,
                                                  description=self.description, index=1)

        # control vis
        condition_attr = nodeUtils.condition(self._blend_ctrl+'.blend', 0.5, self._blend_ctrl+'.modeA',
                                             self._blend_ctrl+'.modeB', side=self.side,
                                             description=self.description+'CtrlVis', index=1, operation='<')

        for sub_component_node, mode, mode_index in zip(self._sub_components_objs, self.blend_modes,
                                                        self._mode_index_list):

            if len(mode) > 1:
                suffix = mode[0].upper() + mode[1:]
            else:
                suffix = mode.title()

            condition_attr_sub = nodeUtils.condition(condition_attr[0], mode_index, 1, self._blend_ctrl+'.allCtrls',
                                                     side=self.side,
                                                     description='{}{}CtrlVis'.format(self.description, suffix),
                                                     index=1)

            nodeUtils.equation('{}.controlsVis * {}'.format(self._component, condition_attr_sub[0]),
                               side=self.side, description='{}{}CtrlVis'.format(self.description, suffix),
                               index=1, attrs=sub_component_node.component+'.controlsVis')

            # add blend ctrl to controls in component
            for ctrl in sub_component_node.controls:
                if cmds.objectType(ctrl) == 'transform':
                    # in case it has shape control
                    controls.add_ctrls_shape(self._blend_ctrl, transform=ctrl)

        # delete temp curve
        cmds.delete(self._temp_curve_node)

        # blend joints
        for i, jnt in enumerate(self._jnts):
            # get joint namer
            namer = naming.Namer(jnt)
            # create choice node
            choice_nodes = []
            for mode in 'AB':
                choice = nodeUtils.node(type=naming.Type.choice, side=namer.side,
                                        description='{}Mode{}'.format(namer.description, mode), index=namer.index)
                cmds.connectAttr('{}.mode{}'.format(self._blend_ctrl, mode), choice+'.selector')
                choice_nodes.append(choice)

            # loop in each components joint
            for sub_component_node, mode_index in zip(self._sub_components_objs, self._mode_index_list):
                if self.localization:
                    namer_joint = naming.Namer(sub_component_node.joints[i])
                    # compose matrix with joint's translate, rotate, scale (skip joint orient)
                    driver = nodeUtils.compose_matrix([sub_component_node.joints[i]+'.translateX',
                                                       sub_component_node.joints[i]+'.translateY',
                                                       sub_component_node.joints[i]+'.translateZ'],
                                                      [sub_component_node.joints[i]+'.rotateX',
                                                       sub_component_node.joints[i]+'.rotateY',
                                                       sub_component_node.joints[i]+'.rotateZ'],
                                                      scale=[sub_component_node.joints[i]+'.scaleX',
                                                             sub_component_node.joints[i]+'.scaleY',
                                                             sub_component_node.joints[i]+'.scaleZ'],
                                                      side=namer_joint.side,
                                                      description=namer_joint.description+'Local',
                                                      index=namer_joint.index)
                else:
                    driver = sub_component_node.output_matrix_attr[i]
                attributes.connect_attrs(driver, ['{}.input[{}]'.format(choice_nodes[0], mode_index),
                                                  '{}.input[{}]'.format(choice_nodes[1], mode_index)], force=True)

            constraints.matrix_blend_constraint([choice_nodes[0]+'.output', choice_nodes[1]+'.output'], jnt,
                                                weights=[self._rvs_blend_attr, self._blend_ctrl+'.blend'],
                                                translate=self.blend_translate, rotate=self.blend_rotate,
                                                scale=self.blend_scale, localization=self.localization)

    def register_component_info(self):
        """
        register component information to component node
        """
        super(MultiBlend, self).register_component_info()

    def get_component_info(self, component_node):
        """
        get component information from component node
        """
        super(MultiBlend, self).get_component_info(component_node)
        self._blend_ctrl = self._ctrls[0]

        # get enum attrs
        enum_list = attributes.get_enum_names('modeA', node=self._blend_ctrl, as_string=True)

        sub_components_dict = {}
        for mode, obj in zip(enum_list, self._sub_components_objs):
            sub_components_dict.update({mode: obj})

        # attach to component as attributes
        self._add_obj_attr('sub_components', sub_components_dict)
