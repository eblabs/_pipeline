# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.logUtils as logUtils
import utils.common.naming as naming
import utils.common.modules as modules
import utils.common.transforms as transforms
import utils.common.attributes as attributes
import utils.common.hierarchy as hierarchy
import utils.common.nodeUtils as nodeUtils
import utils.common.mathUtils as mathUtils
import utils.rigging.constraints as constraints

# import task
import dev.rigging.task.core.task as task

# ICON
import dev.rigging.builder.ui.widgets.icons as icons

# CONSTANT
logger = logUtils.logger


# CLASS
class Component(task.Task):
    """
    base class for all component
    """
    def __init__(self, *args, **kwargs):
        # component variables,
        # useless, just put here so pyCharm won't keep warning me
        # kwargs registered at the end of task's initialization, so we need to put these before super
        self.mirror = None
        self.side = None
        self.description = None
        self.description_suffix = None
        self.bp_jnts = None
        self.ctrl_offsets = None
        self.ctrl_size = None
        self.input_connect = None

        super(Component, self).__init__(**kwargs)

        self._task = 'dev.rigging.task.component.core.component'
        self._task_type = 'component'

        # jnt suffix
        self._jnt_suffix = ''

        # kwargs input mirror
        self.kwargs_input_mirror = {}

        # mirrored component object,
        # in case we run the task creation outside the builder, save here gave us more flexibility
        self.component_mirror = None

        # icon
        self._icon_new = icons.component_new
        self._icon_ref = icons.component_reference

        # hierarchy
        self._component = None
        self._local_grp = None
        self._controls_grp = None
        self._joints_grp = None
        self._nodes_show_grp = None
        self._nodes_hide_grp = None
        self._world_grp = None
        self._nodes_world_grp = None

        # component information
        self._ctrls = []
        self._jnts = []
        self._nodes_show = []
        self._nodes_hide = []
        self._nodes_world = []
        self._input_matrix_attr = None
        self._offset_matrix_attr = None
        self._output_matrix_attr = None

        if args:
            self.get_component_info(args[0])

    @ property
    def component(self):
        return self._component

    @ property
    def controls(self):
        return self._ctrls

    @ property
    def joints(self):
        return self._jnts

    @ property
    def input_matrix_attr(self):
        return self._input_matrix_attr

    @ property
    def input_matrix(self):
        return cmds.getAttr(self._input_matrix_attr)

    @ property
    def offset_matrix_attr(self):
        return self._offset_matrix_attr

    @ property
    def offset_matrix(self):
        return cmds.getAttr(self._offset_matrix_attr)

    @ property
    def output_matrix_attr(self):
        # attribute registered in get_component_info
        return self._output_matrix_attr

    @ property
    def output_matrix(self):
        return self._get_attr(self._output_matrix_attr)

    def pre_build(self):
        super(Component, self).pre_build()
        self.create_hierarchy()
        if self.mirror:
            self.in_class_attributes_mirror_registration()
            self.get_mirrored_kwargs()
            self.mirror_pre_build()

    def build(self):
        super(Component, self).build()
        self.create_component()
        self.register_component_info()
        self.get_component_info(self._component)
        if self.mirror:
            self.mirror_build()

    def post_build(self):
        super(Component, self).post_build()
        self.connect_component()
        if self.mirror:
            self.mirror_post_build()

    def mirror_pre_build(self):
        """
        pre build function for mirrored component,
        1. create component object
        2. attached to builder and current component
        3. get mirrored kwargs
        4. create component in the scene
        """
        # get attr name
        attr_name_mirror = self._flip_val(self._name)
        # create component object
        component_import, component_function = modules.import_module(self._task)
        self.component_mirror = getattr(component_import, component_function)(name=attr_name_mirror,
                                                                              builder=self._builder)

        # attach to builder
        if self._builder:
            # check if build has the attr, in case it has name clash
            component_exist = self._get_obj_attr('builder.'+attr_name_mirror)
            if component_exist:
                logger.error("builder already has component '{}' exists".format(attr_name_mirror))
                raise KeyError("builder already has component '{}' exists".format(attr_name_mirror))
            else:
                setattr(self._builder, attr_name_mirror, self.component_mirror)

        # get mirrored kwargs plug into the component
        # make sure we turn mirror off, otherwise it will try to mirror again
        self.kwargs_input_mirror.update({'mirror': False})
        self.component_mirror.kwargs_input = self.kwargs_input_mirror

        # trigger mirrored component's pre build
        self.component_mirror.pre_build()

    def mirror_build(self):
        """
        build function for mirrored component
        """
        self.component_mirror.build()

    def mirror_post_build(self):
        """
        post build function for mirrored component
        """
        self.component_mirror.post_build()

    def register_inputs(self):
        self.get_override_kwargs()
        super(Component, self).register_inputs()
        self.override_joint_suffix()
        self.check_mirror()

    def override_joint_suffix(self):
        if self.description_suffix:
            self._jnt_suffix = self.description_suffix

    def register_kwargs(self):
        super(Component, self).register_kwargs()

        self.register_attribute('mirror', False, attr_name='mirror', attr_type='bool', hint="mirror component")

        self.register_attribute('side', naming.Side.Key.m, attr_name='side', short_name='s', attr_type='enum',
                                enum=naming.Side.Key.all, hint="component's side")

        self.register_attribute('description', '', attr_name='description', short_name='des', attr_type='str',
                                hint="component's description", skippable=False)

        self.register_attribute('description suffix', '', attr_name='description_suffix', short_name='desSfx',
                                attr_type='str',
                                hint="if the component's nodes description need additional suffix, \
                                      like Ik, Fk etc, put it here")

        self.register_attribute('blueprint joints', [], attr_name='bp_jnts', attr_type='list', select=True,
                                hint="component's blueprint joints")

        self.register_attribute('offsets', 1, attr_name='ctrl_offsets', attr_type='int', skippable=False, min=1,
                                hint="component's controls' offset groups number")

        self.register_attribute('control size', 1.0, attr_name='ctrl_size', attr_type='float', min=0.001,
                                hint="component's controls' size")

        self.register_attribute('input connection', '', attr_name='input_connect', attr_type='str', select=False,
                                hint="component's input connection, should be a component's joint's output matrix, or\
                                        an existing maya node's matrix attribute")

    def check_mirror(self):
        """
        we can't do mirror if attr_name's side or component's side set to middle,
        so if in that case, we need to set mirror to False no matter what the user set.
        """
        namer_attr = naming.check_name_convention(self._name)  # check if attr follow name convention
        if namer_attr:
            # check attr_name's side and component's side, if anything is middle, set mirror to False
            if (namer_attr.side == naming.Side.middle or namer_attr.side == naming.Side.Key.m) or (
                    self.side == naming.Side.middle or self.side == naming.Side.Key.m):
                self.mirror = False
        else:
            # normally create in script for debugging
            self.mirror = False

    def in_class_attributes_mirror_registration(self):
        """
        add in class attribute for mirror
        """
        pass

    def set_attribute_for_mirror(self, attr_name):
        """
        set individual in class attr to be mirrored

        Args:
            attr_name(str): attr's in class name
        """
        attr_value = self._get_obj_attr(attr_name)
        self.kwargs_input.update({attr_name: attr_value})

    def get_mirrored_kwargs(self):
        """
        get kwargs mirrored
        """
        self.kwargs_input_mirror = {}
        for key, item in self.kwargs_input.iteritems():
            # mirror everything
            item_flip = self._flip_val(item)
            self.kwargs_input_mirror.update({key: item_flip})

    def get_override_kwargs(self):
        """
        check if there is any kwarg need to be override from builder, normally because the component is under a pack
        """
        pack_kwargs_override = self._get_obj_attr('_builder.pack_kwargs_override')
        if pack_kwargs_override:
            override_kwargs = self._builder.pack_kwargs_override.get(self._name, {})
            if override_kwargs:
                # update the kwargs
                self.kwargs_input.update(override_kwargs)

    def create_hierarchy(self):
        """
        create component group hierarchy

        component
            -- localGroup
                -- controlsGroup
                -- jointsGroup
                -- nodesShowGroup
                -- nodesHideGroup
            -- worldGroup
                -- nodesWorldGroup
        """
        namer = naming.Namer(type=naming.Type.component, side=self.side,
                             description=self.description+self.description_suffix, index=1)

        # create transforms
        # component
        self._component = transforms.create(namer.name, lock_hide=attributes.Attr.all)

        # local group
        namer.type = naming.Type.localGroup
        self._local_grp = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self._component)

        # control group
        namer.type = naming.Type.controlsGroup
        self._controls_grp = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self._local_grp)

        # joints group
        namer.type = naming.Type.jointsGroup
        self._joints_grp = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self._local_grp)

        # nodes show group
        namer.type = naming.Type.nodesShowGroup
        self._nodes_show_grp = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self._local_grp)

        # nodes hide group
        namer.type = naming.Type.nodesHideGroup
        self._nodes_hide_grp = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self._local_grp)

        # world group
        namer.type = naming.Type.worldGroup
        self._world_grp = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self._component)

        # nodes world group
        namer.type = naming.Type.nodesWorldGroup
        self._nodes_world_grp = transforms.create(namer.name, lock_hide=attributes.Attr.all, parent=self._world_grp)

        # add attrs
        # -- input matrix: input connection from other component
        # -- offset matrix: offset from the input to the current component
        # -- controls: message info to get all the controllers' names
        # -- joints: message info to get all the joints' names
        # -- controlsVis: controls visibility switch
        # -- jointsVis: joints visibility switch
        # -- rigNodesVis: rig nodes visibility switch
        # -- componentType: component class type to get the node wrapped as object
        # -- inClassName: component name in builder
        # -- outputMatrix: joints' output matrices

        # input matrix, offset matrix
        attributes.add_attrs(self._component, ['inputMatrix', 'offsetMatrix'], attribute_type='matrix', lock=True)
        # controls, joints
        attributes.add_attrs(self._component, ['controls', 'joints'], attribute_type='message', multi=True)
        # controls vis, joints vis
        attributes.add_attrs(self._component, ['controlsVis', 'jointsVis', 'rigNodesVis'], attribute_type='long',
                             range=[0, 1], default_value=[1, 0, 0], keyable=False, channel_box=True)
        # component type and in-class name
        attributes.add_attrs(self._component, ['componentType', 'inClassName'], attribute_type='string',
                             default_value=[self._task, self._name], lock=True)
        # output matrix
        cmds.addAttr(self._component, longName='outputMatrix', attributeType='matrix', multi=True)

        # connect attrs
        attributes.connect_attrs(['controlsVis', 'controlsVis', 'jointsVis', 'rigNodesVis', 'rigNodesVis'],
                                 [self._controls_grp+'.visibility', self._nodes_show_grp+'.visibility',
                                  self._joints_grp + '.visibility', self._nodes_hide_grp+'.visibility',
                                  self._nodes_world_grp+'.visibility'], driver=self._component)

        # mult input and offset matrix to connect local group
        mult_matrix_attr = nodeUtils.mult_matrix([self._component+'.inputMatrix', self._component+'.offsetMatrix'],
                                                 side=self.side, description=self.description+self.description_suffix,
                                                 index=1)
        constraints.matrix_connect(mult_matrix_attr, self._local_grp, force=True)

        # parent to base node's component group and connect attr
        # check if has base node, skip if doesn't
        component_grp = self._get_obj_attr('_builder.base_node.components')
        if component_grp:
            # base node exists, parent component to component group
            hierarchy.parent_node(self._component, component_grp)
            # get master node
            master_node = self._get_obj_attr('_builder.base_node.master')
            # connect vis attrs
            attributes.connect_attrs(['controlsVis', 'jointsVis', 'rigNodesVis'],
                                     ['controlsVis', 'jointsVis', 'rigNodesVis'],
                                     driver=master_node, driven=self._component)

    def create_component(self):
        """
        this is the function where all sub classes' creation should be
        """
        pass

    def register_component_info(self):
        """
        register component information to component node
        """
        self._input_matrix_attr = self._component + '.inputMatrix'
        self._offset_matrix_attr = self._component + '.offsetMatrix'
        self._output_matrix_attr = self._component + '.outputMatrix'

        # control message
        for i, ctrl in enumerate(self._ctrls):
            cmds.connectAttr(ctrl+'.message', '{}.controls[{}]'.format(self._component, i), force=True)

        # joint message and output matrix
        for i, jnt in enumerate(self._jnts):
            cmds.connectAttr(jnt+'.message', '{}.joints[{}]'.format(self._component, i), force=True)
            cmds.connectAttr(jnt+'.worldMatrix[0]', '{}.outputMatrix[{}]'.format(self._component, i), force=True)

    def get_component_info(self, component_node):
        """
        get component information from component node
        """
        self._component = component_node
        self._ctrls = self._get_attr(self._component+'.controls')
        self._jnts = self._get_attr(self._component+'.joints')
        self._task = cmds.getAttr(self._component+'.componentType')
        self._name = cmds.getAttr(self._component+'.inClassName')

        # output matrix
        output_matrix_dict = {'_output_matrix_attr': []}
        if self._jnts:
            for i in range(len(self._jnts)):
                output_matrix_dict['_output_matrix_attr'].append(self._component+'.outputMatrix[{}]'.format(i))

        self._add_attr_from_dict(output_matrix_dict)

    def connect_component(self):
        """
        connect component with given input (input connection registered in initialization)
        """
        input_matrix_attr = None
        # check if has input connection
        if self.input_connect:
            input_matrix_attr = self._get_node_name(self.input_connect)
            # check if it's a matrix attr, could be a node name or other attr
            if '.' not in input_matrix_attr or cmds.getAttr(input_matrix_attr, type=True) != 'matrix':
                input_matrix_attr = None

        if not input_matrix_attr:
            # check if base node in the scene, connect to base node
            input_matrix_attr_obj = self._get_obj_attr('builder.base_node.world_pos_attr.matrix_attr')
            if input_matrix_attr_obj:
                input_matrix_attr = input_matrix_attr_obj

        if input_matrix_attr:
            # compute matrix if input matrix exist
            input_matrix = cmds.getAttr(input_matrix_attr)
            input_matrix_inv = mathUtils.inverse_matrix(input_matrix)
            offset_matrix = mathUtils.mult_matrix([mathUtils.MATRIX_DEFAULT, input_matrix_inv])

            # connect input matrix, set offset matrix
            attributes.connect_attrs(input_matrix_attr, self._input_matrix_attr, force=True)
            attributes.set_attrs(self._offset_matrix_attr, offset_matrix, type='matrix', force=True)

    def disconnect_component(self):
        """
        disconnect component
        """
        # check connection
        input_connect = cmds.listConnections(self._input_matrix_attr, source=True, destination=False, plugs=True)
        if input_connect:
            cmds.disconnectAttr(input_connect[0], self._input_matrix_attr)

        attributes.set_attrs([self._input_matrix_attr, self._offset_matrix_attr], mathUtils.MATRIX_DEFAULT,
                             type='matrix', force=True)

    def _flip_val(self, attr_value):
        """
        flip name for all type

        Args:
            attr_value(str/list/dict): attribute value

        Returns:
            attr_value_flip(str/list/dict)
        """
        if isinstance(attr_value, basestring):
            attr_value_flip = naming.mirror_name(attr_value, keep_orig=True)
        elif isinstance(attr_value, list):
            attr_value_flip = []
            for attr_val in attr_value:
                attr_value_flip.append(self._flip_val(attr_val))
        elif isinstance(attr_value, dict):
            attr_value_flip = {}
            for key, item in attr_value.iteritems():
                key_flip = naming.mirror_name(key, keep_orig=True)
                item_flip = self._flip_val(item)
                attr_value_flip.update({key_flip: item_flip})
        else:
            attr_value_flip = attr_value
        return attr_value_flip

    @ staticmethod
    def _get_attr(attr):
        """
        get given node's attr value
        Args:
            attr(str/list): attribute name

        Returns:
            value
        """
        driver = attr.split('.')[0]
        attr_name = attr.replace(driver+'.', '')
        if attributes.check_attr_exists(attr_name, node=driver):
            # check type
            if cmds.getAttr(attr, type=True) == 'message':
                val = cmds.listConnections(attr, source=True, destination=False, plugs=False, shapes=True)
            else:
                if isinstance(attr, list):
                    val = []
                    for attr_single in attr:
                        val_single = cmds.getAttr(attr_single)
                        val.append(val_single)
                else:
                    val = cmds.getAttr(attr)
        else:
            val = None
        return val
