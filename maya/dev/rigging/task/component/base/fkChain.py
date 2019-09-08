# IMPORT PACKAGES

# import utils
import utils.common.attributes as attributes
import utils.rigging.limb.fkChain as fkChainLimb

# import task
import dev.rigging.task.component.core.component as component


# CLASS
class FkChain(component.Component):
    """
    fk chain component
    """
    def __init__(self, *args, **kwargs):
        self.lock_hide = None
        self.end_jnt = None

        super(FkChain, self).__init__(*args, **kwargs)

        self._task = 'dev.rigging.task.component.base.fkChain'
        self._jnt_suffix = 'Fk'

    def register_kwargs(self):
        super(FkChain, self).register_kwargs()
        self.register_attribute('lock hide', attributes.Attr.scale, attr_name='lock_hide', short_name='lh',
                                attr_type='list', hint="lock hide the given channels")

        self.register_attribute('end joint', True, attr_name='end_jnt', short_name='end', attr_type='bool',
                                hint="add control for the end joint")

    def create_component(self):
        super(FkChain, self).create_component()

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

                  'lock_hide': self.lock_hide,
                  'end_joint': self.end_jnt}

        fk_limb = fkChainLimb.FkChain(**kwargs)
        fk_limb.create()

        # pass info
        self._jnts = fk_limb.jnts
        self._ctrls = fk_limb.ctrls