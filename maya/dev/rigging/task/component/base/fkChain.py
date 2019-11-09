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

    Keyword Args:
        mirror(bool): [mirror] mirror component, default is False
        side(str): [side] component's side, default is middle
        description(str): [description] component's description
        description suffix(str): [description_suffix] if the component nodes description need additional suffix,
                                                      like Ik, Fk etc, put it here, default is Fk
        blueprint joints(list): [bp_jnts] component's blueprint joints
        offsets(int): [ctrl_offsets] component's controls' offset groups number
        control_size(float): [ctrl_size] component's controls' size
        input connection(str):  [input_connect] component's input connection, should be a component's joint's output
                                                matrix, or an existing maya node's matrix attribute
        lock hide(list): [lock_hide] lock hide the given channels, default is [scaleX, scaleY, scaleZ]
        end joint(bool): [end_jnt] add control for the end joint, default is False

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
        self.lock_hide = None
        self.end_jnt = None

        super(FkChain, self).__init__(*args, **kwargs)

        self._task = 'dev.rigging.task.component.base.fkChain'
        self._jnt_suffix = 'Fk'

    def register_kwargs(self):
        super(FkChain, self).register_kwargs()
        self.register_attribute('lock hide', attributes.Attr.scale, attr_name='lock_hide', short_name='lh',
                                attr_type='list', hint="lock hide the given channels")

        self.register_attribute('end joint', False, attr_name='end_jnt', short_name='end', attr_type='bool',
                                hint="add control for the end joint")

        self.update_attribute('description suffix', default='Fk')

    def create_component(self):
        super(FkChain, self).create_component()

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

                  'lock_hide': self.lock_hide,
                  'end_joint': self.end_jnt}

        fk_limb = fkChainLimb.FkChain(**kwargs)
        fk_limb.create()

        # pass info
        self._jnts = fk_limb.jnts
        self._ctrls = fk_limb.ctrls