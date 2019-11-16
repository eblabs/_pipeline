# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.naming as naming
import utils.common.variables as variables
import utils.common.attributes as attributes
import utils.common.nodeUtils as nodeUtils
import utils.common.transforms as transforms
import utils.rigging.controls as controls
import utils.rigging.constraints as constraints

# import limb
import limb


# CLASS
class SingleChainIk(limb.Limb):
    """
    single chain ik rig limb

    Keyword Args:
        @ limb
            side(str)
            description(str)
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
        @ singleChainIk
            ik_type(str): ik/aim
    """
    def __init__(self, **kwargs):
        super(SingleChainIk, self).__init__(**kwargs)
        self._ik_type = variables.kwargs('ik_type', 'ik', kwargs)
        self._jnt_suffix = variables.kwargs('joint_suffix', self._ik_type.title(), kwargs, short_name='jntSfx')
        self._ctrl_shape = variables.kwargs('control_shape', ['sphere', 'handle'], kwargs, short_name='shape')
        self.iks = []

    def create(self):
        super(SingleChainIk, self).create()

        if isinstance(self._ctrl_shape, basestring):
            self._ctrl_shape = [self._ctrl_shape] * 2

        # create controls
        ctrl_objs = []
        for jnt, ctrl_shape, suffix in zip([self.jnts[0], self.jnts[-1]], self._ctrl_shape, ['Root', 'Target']):
            namer = naming.Namer(jnt)
            ctrl = controls.create(namer.description+suffix, side=namer.side, index=namer.index,
                                   offsets=self._ctrl_offsets, parent=self._controls_grp, pos=jnt,
                                   lock_hide=attributes.Attr.scale, shape=ctrl_shape, size=self._ctrl_size,
                                   color=self._ctrl_color, sub=self._sub)
            self.ctrls.append(ctrl.name)
            ctrl_objs.append(ctrl)

        # lock hide target control's rotation and rotate order
        ctrl_objs[1].lock_hide_attrs(attributes.Attr.rotate+attributes.Attr.rotateOrder)
        # parent target control to root control
        cmds.parent(ctrl_objs[1].zero, ctrl_objs[0].output)

        # connect root control translate with root joint
        constraints.matrix_connect(ctrl_objs[0].world_matrix_attr, self.jnts[0],
                                   skip=attributes.Attr.rotate+attributes.Attr.scale)

        # get target matrix
        target_matrix = nodeUtils.mult_matrix([ctrl_objs[1].world_matrix_attr, ctrl_objs[0].world_matrix_attr],
                                              side=self._side, description=self._des+'TargetPos', index=1)

        # rig ik
        if self._ik_type == 'ik':
            # create ik handle
            ik_handle = naming.Namer(type=naming.Type.ikHandle, side=self._side, description=self._des+self._jnt_suffix,
                                     index=1).name
            cmds.ikHandle(startJoint=self.jnts[0], endEffector=self.jnts[-1], solver='ikSCsolver', name=ik_handle)

            # add transform to drive ik handle
            ik_transform = naming.Namer(type=naming.Type.transform, side=self._side,
                                        description=self._des+self._jnt_suffix, index=1).name
            ik_transform = transforms.create(ik_transform, pos=ctrl_objs[-1].name, lock_hide=attributes.Attr.all,
                                             vis=False, parent=self._nodes_hide_grp)
            constraints.matrix_connect(target_matrix, ik_transform, force=True)

            cmds.parent(ik_handle, ik_transform)

            # pass info
            self.nodes_hide.append(ik_transform)
            self.iks.append(ik_handle)
        else:
            # get aim axis and up axis, because right side may be -1
            # get second joint's tx
            tx = cmds.getAttr(self.jnts[1]+'.translateX')
            if tx >= 0:
                aim_vec = [1, 0, 0]
                up_vec = [0, 1, 0]
            else:
                aim_vec = [-1, 0, 0]
                up_vec = [0, -1, 0]
            # aim constraint
            constraints.matrix_aim_constraint(target_matrix, self.jnts[0], world_up_type='objectrotation',
                                              world_up_matrix=ctrl_objs[0].world_matrix_attr, aim_vector=aim_vec,
                                              up_vector=up_vec, local=True, lock=True, force=True)
