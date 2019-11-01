# IMPORT PACKAGES

# import utils
import utils.rigging.limb.rotatePlaneIk as rotatePlaneIkLimb

# import task
import dev.rigging.task.component.core.component as component


# CLASS
class RotatePlaneIk(component.Component):
    """
    single chain ik component
    """
    def __init__(self, *args, **kwargs):
        self.bp_ctrls = None
        self.sc_iks = None
        self.bp_rvs = None

        super(RotatePlaneIk, self).__init__(*args, **kwargs)

        self._task = 'dev.rigging.task.component.base.rotatePlaneIk'
        self._jnt_suffix = 'Ik'
        self._iks = []
        self._rvs_ctrls = []

    def register_kwargs(self):
        super(RotatePlaneIk, self).register_kwargs()
        self.register_attribute('blueprint controls', [], attr_name='bp_ctrls', attr_type='list', select=True,
                                hint="ik control blueprint, [root, pole_vector, ik, ground] ground control is optional")

        self.register_attribute('single chain iks', 0, attr_name='sc_iks', attr_type='int', min=0, max=2,
                                skippable=False, hint="create single chain ik per segment after rotate plane ik")

        self.register_attribute('blueprint reverse controls', [], attr_name='bp_rvs', attr_type='list', select=True,
                                hint="reverse set-up's controls blueprints, normally for foot or hand\
                                            structure like [heelRoll, toeRoll, sideInn, sideOut, ballRoll, (toeTap)]")

        self.register_attribute('ik_handle_offset', False, attr_type='bool', hint="add a control to offset ik handle")

    def mirror_kwargs(self):
        super(RotatePlaneIk, self).mirror_kwargs()
        self.bp_ctrls = self._flip_list(self.bp_ctrls)
        self.bp_rvs = self._flip_list(self.bp_rvs)

    def create_component(self):
        super(RotatePlaneIk, self).create_component()

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
