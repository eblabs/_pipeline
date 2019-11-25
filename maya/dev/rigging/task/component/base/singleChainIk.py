# IMPORT PACKAGES

# import utils
import utils.rigging.limb.singleChainIk as singleChainIkLimb

# import task
import dev.rigging.task.component.core.component as component


# CLASS
class SingleChainIk(component.Component):
    """
    single chain ik component

    Keyword Args:
        mirror(bool): [mirror] mirror component, default is False
        side(str): [side] component's side, default is middle
        description(str): [description] component's description
        description suffix(str): [description_suffix] if the component nodes description need additional suffix,
                                                      like Ik, Fk etc, put it here, default is Ik
        blueprint joints(list): [bp_jnts] component's blueprint joints
        control space(dict): [ctrl_space] add spaces for controls after loading space data
                                          template is {control_name: [{space_name: {'input_matrix_attr': matrix_attr,
                                                                                    'space_type': []}}}]
                                          control name can be transform node name in maya, or component's control attr
                                          input matrix attr can be maya node's attribute name, or component's attr
                                          space types has 'parent', 'point', 'orient', 'scale'
                                          parent and point/orient can't be added on top if the other exist already
        offsets(int): [ctrl_offsets] component's controls' offset groups number, default is 1
        control_size(float): [ctrl_size] component's controls' size, default is 1.0
        input connection(str):  [input_connect] component's input connection, should be a component's joint's output
                                                matrix, or an existing maya node's matrix attribute
        ik type(str): [ik_type] ik type for this component, single chain ik or aim constraint, ik/aim, default is ik

    Properties:
        name(str): task's name in builder
        task(str): task's path

        component(str): component node name
        controls(list): component's controls names
        control_objects(list): component's control objects
        joints(list): component's joints names
        input_matrix_attr(str): component's input matrix attribute
        input_matrix(list): component's input matrix
        offset_matrix_attr(str): component's offset matrix attribute
        offset_matrix(list): component's offset matrix
        output_matrix_attr(list): component's output matrices attributes
        output_matrix(list): component's output matrices
    """
    def __init__(self, *args, **kwargs):
        self.ik_type = None
        self._jnt_suffix = ''

        super(SingleChainIk, self).__init__(*args, **kwargs)

        self._task = 'dev.rigging.task.component.base.singleChainIk'
        self._iks = []

    def register_kwargs(self):
        super(SingleChainIk, self).register_kwargs()
        self.register_attribute('ik type', 'ik', attr_name='ik_type', attr_type='enum', enum=['ik', 'aim'],
                                hint="ik type for this component, single chain ik or aim constraint")

        self.update_attribute('description suffix', default='Ik')

    def override_joint_suffix(self):
        if self.description_suffix:
            self._jnt_suffix = self.description_suffix
        else:
            self._jnt_suffix = self.ik_type.title()

    def create_component(self):
        super(SingleChainIk, self).create_component()

        kwargs = {'side': self.side,
                  'description': self.description,
                  'blueprint_joints': self.bp_jnts,
                  'joint_suffix': self._jnt_suffix,
                  'create_joints': True,
                  'offsets': self.ctrl_offsets,
                  'control_size': self.ctrl_size,

                  'controls_group': self._controls_grp,
                  'joints_group': self._joints_grp,
                  'nodes_hide_group': self._nodes_hide_grp,
                  'nodes_show_group': self._nodes_show_grp,
                  'nodes_world_group': self._nodes_world_grp,

                  'ik_type': self.ik_type}

        ik_limb = singleChainIkLimb.SingleChainIk(**kwargs)
        ik_limb.create()

        # pass info
        self._jnts = ik_limb.jnts
        self._ctrls = ik_limb.ctrls
        self._iks = ik_limb.iks
        self._nodes_hide = ik_limb.nodes_hide
