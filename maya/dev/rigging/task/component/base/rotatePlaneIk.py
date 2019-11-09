# IMPORT PACKAGES

# import utils
import utils.rigging.limb.rotatePlaneIk as rotatePlaneIkLimb

# import task
import dev.rigging.task.component.core.component as component


# CLASS
class RotatePlaneIk(component.Component):
    """
    rotate plane ik component

    Keyword Args:
        mirror(bool): [mirror] mirror component, default is False
        side(str): [side] component's side, default is middle
        description(str): [description] component's description
        description suffix(str): [description_suffix] if the component nodes description need additional suffix,
                                                      like Ik, Fk etc, put it here, default is Ik
        blueprint joints(list): [bp_jnts] component's blueprint joints
        offsets(int): [ctrl_offsets] component's controls' offset groups number, default is 1
        control_size(float): [ctrl_size] component's controls' size, default is 1.0
        input connection(str):  [input_connect] component's input connection, should be a component's joint's output
                                                matrix, or an existing maya node's matrix attribute
        blueprint controls(list): [bp_ctrls] ik controls blueprint, [root, pole vector, ik, ground], gournd is optional
        single chain iks(int): [sc_iks] create single chain ik per segment after rotate plane ik, default is 1
        blueprint reverse controls(list): [bp_rvs] reverse set-up's controls blueprints, normally for foot or hand,
                                                   structure like:
                                                   [heelRoll, toeRoll, sideInn, sideOut, ballRoll, (toeTap)]
        ik handle offset(bool): [ik_offset] add a control to offset ik handle, default is False

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
    """
    def __init__(self, *args, **kwargs):
        self.bp_ctrls = None
        self.sc_iks = None
        self.bp_rvs = None
        self.ik_offset = None

        super(RotatePlaneIk, self).__init__(*args, **kwargs)

        self._task = 'dev.rigging.task.component.base.rotatePlaneIk'
        self._jnt_suffix = 'Ik'
        self._iks = []
        self._rvs_ctrls = []

    def register_kwargs(self):
        super(RotatePlaneIk, self).register_kwargs()
        self.register_attribute('blueprint controls', [], attr_name='bp_ctrls', attr_type='list', select=True,
                                skippable=False,
                                hint=("ik controls blueprint,\n",
                                      "[root, pole_vector, ik, ground] ground control is optional"))

        self.register_attribute('single chain iks', 1, attr_name='sc_iks', attr_type='int', min=0, max=2,
                                hint="create single chain ik per segment after rotate plane ik")

        self.register_attribute('blueprint reverse controls', [], attr_name='bp_rvs', attr_type='list', select=True,
                                hint=("reverse set-up's controls blueprints,\n normally for foot or hand,\n",
                                      "structure like [heelRoll, toeRoll, sideInn, sideOut, ballRoll, (toeTap)]"))

        self.register_attribute('ik handle offset', False, attr_name='ik_offset', attr_type='bool',
                                hint="add a control to offset ik handle")

        self.update_attribute('description suffix', default='Ik')

    def create_component(self):
        super(RotatePlaneIk, self).create_component()

        kwargs = {'side': self.side,
                  'description': self.description,
                  'blueprint_joints': self.bp_jnts,
                  'joint_suffix': self._jnt_suffix,
                  'create_joints': True,
                  'offsets': self.ctrl_offsets,
                  'control_size': self.ctrl_size,
                  'ik_handle_offset': self.ik_offset,

                  'controls_group': self._controls_grp,
                  'joints_group': self._joints_grp,
                  'nodes_hide_group': self._nodes_hide_grp,
                  'nodes_show_group': self._nodes_show_grp,
                  'nodes_world_group': self._nodes_world_grp,

                  'blueprint_controls': self.bp_ctrls,
                  'single_chain_iks': self.sc_iks,
                  'blueprint_reverse_controls': self.bp_rvs}

        ik_limb = rotatePlaneIkLimb.RotatePlaneIk(**kwargs)
        ik_limb.create()

        # pass info
        self._jnts = ik_limb.jnts
        self._ctrls = ik_limb.ctrls
        self._iks = ik_limb.iks
        self._rvs_ctrls = ik_limb.rvs_ctrls
        self._nodes_hide = ik_limb.nodes_hide
        self._nodes_show = ik_limb.nodes_show
