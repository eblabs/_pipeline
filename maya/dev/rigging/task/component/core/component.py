# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.variables as variables
import utils.common.logUtils as logUtils
import utils.common.naming as naming
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
        super(Component, self).__init__(**kwargs)
        self._task = 'dev.rigging.task.component.core.component'
        self._task_type = 'component'

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
        self._input_matrix_attr = None
        self._offset_matrix_attr = None

        if args:
            self.get_component_info(args[0])

    @property
    def component(self):
        return self._component

    @property
    def controls(self):
        return self._ctrls

    @property
    def joints(self):
        return self._jnts

    @property
    def input_matrix_attr(self):
        return self._input_matrix_attr

    @property
    def input_matrix(self):
        return cmds.getAttr(self._input_matrix_attr)

    @property
    def offset_matrix_attr(self):
        return self._offset_matrix_attr

    @property
    def offset_matrix(self):
        return cmds.getAttr(self._offset_matrix_attr)

    @property
    def output_matrix_attr(self):
        # attribute registered in get_component_info
        return self._output_matrix_attr

    @property
    def output_matrix(self):
        return self._get_attr(self._output_matrix_attr)

    def pre_build(self):
        super(Component, self).pre_build()
        self.create_hierarchy()

    def build(self):
        super(Component, self).build()
        self.create_component()
        self.register_component_info()
        self.get_component_info(self._component)

    def post_build(self):
        super(Component, self).post_build()
        self.connect_component()

    def register_kwargs(self):
        super(Component, self).register_kwargs()

        self.register_attribute('side', naming.Side.middle, attr_name='side', short_name='s', attr_type='enum',
                                enum=naming.Side.all, hint="component's side")

        self.register_attribute('description', '', attr_name='description', short_name='des', attr_type='str',
                                hint="component's description")

        self.register_attribute('index', -1, attr_name='index', short_name='i', attr_type='int', skippable=True,
                                hint="component's index")

        self.register_attribute('blueprint joints', [], attr_name='bp_jnts', attr_type='list', select=True,
                                hint="component's blueprint joints")

        self.register_attribute('offsets', 1, attr_name='ctrl_offsets', attr_type='int', skippable=False, min=1,
                                hint="component's controls' offset groups number")

        self.register_attribute('control size', 1.0, attr_name='ctrl_size', attr_type='float', min=0.001,
                                hint="component's controls' size")

        self.register_attribute('input connection', '', attr_name='input_connect', attr_type='str', select=False,
                                hint="component's input connection, should be a component's joint's output matrix, or\
                                        an existing maya node's matrix attribute")

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
        namer = naming.Namer(type=naming.Type.component, side=self.side, description=self.description, index=self.index)

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
        # -- outputMatrix: joints' output matrices

        # input matrix, offset matrix
        attributes.add_attrs(self._component, ['inputMatrix', 'offsetMatrix'], attribute_type='matrix', lock=True)
        # controls, joints
        attributes.add_attrs(self._component, ['controls', 'joints'], attribute_type='message', multi=True)
        # controls vis, joints vis
        attributes.add_attrs(self._component, ['controlsVis', 'jointsVis', 'rigNodesVis'], attribute_type='long',
                             range=[0, 1], default_value=[1, 0, 0], keyable=False, channel_box=True)
        # component type
        attributes.add_attrs(self._component, 'componentType', attribute_type='string', default_value=self._task,
                             lock=True)
        # output matrix
        cmds.addAttr(self._component, longName='outputMatrix', attributeType='matrix', multi=True)

        # connect attrs
        attributes.connect_attrs(['controlsVis', 'jointsVis', 'rigNodesVis', 'rigNodesVis'],
                                 [self._controls_grp+'.visibility', self._joints_grp + '.visibility',
                                  self._nodes_hide_grp+'.visibility', self._nodes_world_grp+'.visibility'],
                                 driver=self._component)

        # mult input and offset matrix to connect local group
        mult_matrix_attr = nodeUtils.mult_matrix([self._component+'.inputMatrix', self._component+'.offsetMatrix'],
                                                 side=self.side, description=self.description, index=self.index)
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

        # control message
        for i, ctrl in enumerate(self._ctrls):
            cmds.connectAttr(ctrl+'.message', '{}.controls[{}]'.format(self._component, i), force=True)

        # joint message and output matrix
        for i, jnt in enumerate(self._jnts):
            cmds.connectAttr(jnt+'.message', '{}.joints[{}]'.format(self._component, i), force=True)
            cmds.connectAttr(jnt+'.worldMatrix[0]', '{}.outputMatrix[{}]'.format(self._component, i), force=True)

    def get_component_info(self, component):
        """
        get component information from component node
        """
        self._component = component
        self._ctrls = self._get_attr(self._component+'.controls')
        self._jnts = self._get_attr(self._component+'.joints')

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
            # check if input connection is an component attribute
            input_matrix_attr = self._get_obj_attr('builder.'+self.input_connect)
            if input_matrix_attr and cmds.getAttr(input_matrix_attr, type=True) != 'matrix':
                # set back input_matrix_attr
                input_matrix_attr = None
        else:
            # check if it's a node in scene
            attr_split = self.input_connect.split('.')
            if len(attr_split) > 1 and cmds.objExists(attr_split[0]):
                # it's a node attribute and node is in the scene
                if attributes.check_attr_exists(attr_split[1:], node=attr_split[0]):
                    # check if it's matrix
                    if cmds.getAttr(self.input_connect, type=True) == 'matrix':
                        input_matrix_attr = self.input_connect

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
                val = cmds.listConnections(attr, source=True, destination=False, plugs=False)
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


