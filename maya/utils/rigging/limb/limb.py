# IMPORT PACKAGES

# import utils
import utils.common.naming as naming
import utils.common.variables as variables
import utils.rigging.joints as joints


# CLASS
class Limb(object):
    """
    base limb

    Keyword Args:
        side(str)
        description(str)
        index(int)
        blueprint_joints(list)
        joint_suffix(str)
        create_joints(bool): False will use blueprint joints as joints directly
        offsets(int): controls' offset groups
        control_size(float)
        control_color(str/int): None will follow the side's preset
        control_shape(str/list): controls shape
        sub_control(bool)[True]
        controls_group(str): transform node to parent controls
        joints_group(str): transform node to parent joints
        nodes_hide_group(str): transform node to parent hidden nodes
        nodes_show_group(str): transform node to parent visible nodes
        nodes_world_group(str): transform node to parent world rig nodes
    """
    def __init__(self, **kwargs):
        self._side = variables.kwargs('side', 'middle', kwargs, short_name='s')
        self._des = variables.kwargs('description', '', kwargs, short_name='des')
        self._index = variables.kwargs('index', None, kwargs, short_name='i')
        self._bp_jnts = variables.kwargs('blueprint_joints', [], kwargs, short_name=naming.Type.blueprintJoints)
        self._jnt_suffix = variables.kwargs('joint_suffix', '', kwargs, short_name='jntSfx')
        self._create_jnts = variables.kwargs('create_joints', True, kwargs)

        self._ctrl_offsets = variables.kwargs('offsets', 1, kwargs, short_name=naming.Type.offset)
        self._ctrl_size = variables.kwargs('control_size', 1, kwargs, short_name='size')
        self._ctrl_color = variables.kwargs('control_color', None, kwargs, short_name='color')
        self._ctrl_shape = variables.kwargs('control_shape', 'circle', kwargs, short_name='shape')
        self._sub = variables.kwargs('sub_control', True, kwargs, short_name='sub')

        self._controls_grp = variables.kwargs('controls_group', '', kwargs, short_name=naming.Type.controlsGroup)
        self._joints_grp = variables.kwargs('joints_group', '', kwargs, short_name=naming.Type.jointsGroup)
        self._nodes_hide_grp = variables.kwargs('nodes_hide_group', '', kwargs, short_name=naming.Type.nodesHideGroup)
        self._nodes_show_grp = variables.kwargs('nodes_show_group', '', kwargs, short_name=naming.Type.nodesShowGroup)
        self._nodes_world_grp = variables.kwargs('nodes_world_group', '', kwargs,
                                                 short_name=naming.Type.nodesWorldGroup)

        self.jnts = []
        self.ctrls = []
        self.nodes_world = []
        self.nodes_hide = []
        self.nodes_show = []

    def create(self):
        if self._create_jnts:
            self.jnts = joints.create_on_hierarchy(self._bp_jnts, naming.Type.blueprintJoint, naming.Type.joint,
                                                   suffix=self._jnt_suffix, parent=self._joints_grp)
        else:
            self.jnts = self._bp_jnts
