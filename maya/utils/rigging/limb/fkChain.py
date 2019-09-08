# IMPORT PACKAGES

# import utils
import utils.common.naming as naming
import utils.common.variables as variables
import utils.common.attributes as attributes
import utils.rigging.controls as controls
import utils.rigging.constraints as constraints

# import limb
import limb


# CLASS
class FkChain(limb.Limb):
    """
    fk chain rig limb

    Keyword Args:
        @ limb
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
        @ fkChain
            lock_hide(list): lock and hide controls channels
            end_joint(bool)[True]: add control for the end joint
    """
    def __init__(self, **kwargs):
        super(FkChain, self).__init__(**kwargs)
        self._lock_hide = variables.kwargs('lock_hide', attributes.Attr.scale, kwargs, short_name='lh')
        self._jnt_suffix = variables.kwargs('joint_suffix', 'Fk', kwargs, short_name='jntSfx')
        self._ctrl_shape = variables.kwargs('control_shape', 'circle', kwargs, short_name='shape')
        self._end_jnt = variables.kwargs('end_joint', True, kwargs, short_name='end')

    def create(self):
        super(FkChain, self).create()
        if isinstance(self._ctrl_shape, basestring):
            self._ctrl_shape = [self._ctrl_shape] * len(self.jnts)

        # create controls
        parent = self._controls_grp
        jnts = self.jnts
        if not self._end_jnt:
            jnts = self.jnts[:-1]

        for jnt, shape in zip(jnts, self._ctrl_shape):
            # loop in each blueprint joint and control shape
            namer = naming.Namer(jnt)
            ctrl = controls.create(namer.description, side=namer.side, index=namer.index, offsets=self._ctrl_offsets,
                                   parent=parent, pos=jnt, lock_hide=self._lock_hide, shape=shape,
                                   size=self._ctrl_size, color=self._ctrl_color, sub=self._sub)

            # connect ctrl to joint
            constraints.matrix_connect(ctrl.local_matrix_attr, jnt, skip=attributes.Attr.translate)
            constraints.matrix_connect(ctrl.world_matrix_attr, jnt, skip=attributes.Attr.rotate+attributes.Attr.scale)

            self.ctrls.append(ctrl.name)
            parent = ctrl.output
