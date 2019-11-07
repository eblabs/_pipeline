# IMPORT PACKAGES

# import utils
import utils.rigging.limb.singleChainIk as singleChainIkLimb

# import task
import dev.rigging.task.component.core.component as component


# CLASS
class SingleChainIk(component.Component):
    """
    single chain ik component
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
