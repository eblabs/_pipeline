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

        super(RotatePlaneIk, self).__init__(*args, **kwargs)

        self._task = 'dev.rigging.task.component.base.rotatePlaneIk'
        self._jnt_suffix = 'Ik'
        self._iks = []

    def register_kwargs(self):
        super(RotatePlaneIk, self).register_kwargs()
        self.register_attribute('blueprint controls', [], attr_name='bp_ctrls', attr_type='list',
                                hint="ik control blueprint, [root, pole_vector, ik]")

    def create_component(self):
        super(RotatePlaneIk, self).create_component()

        kwargs = {'side': self.side,
                  'description': self.description,
                  'index': self.index,
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

                  'blueprint_controls': self.bp_ctrls}

        ik_limb = rotatePlaneIkLimb.RotatePlaneIk(**kwargs)
        ik_limb.create()

        # pass info
        self._jnts = ik_limb.jnts
        self._ctrls = ik_limb.ctrls
        self._iks = ik_limb.iks
        self._nodes_hide = ik_limb.nodes_hide
        self._nodes_show = ik_limb.nodes_show
