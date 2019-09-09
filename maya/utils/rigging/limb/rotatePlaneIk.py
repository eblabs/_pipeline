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
import utils.modeling.curves as curves

# import limb
import limb


# CLASS
class RotatePlaneIk(limb.Limb):
    """
    rotate plane ik rig limb

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
        @ rotatePlaneIk
            blueprint_controls(list): ik control blueprint, [root, pole_vector, ik]
    """
    def __init__(self, **kwargs):
        super(RotatePlaneIk, self).__init__(**kwargs)
        self._bp_ctrls = variables.kwargs('blueprint_controls', [], kwargs, short_name='bpCtrl')
        self._jnt_suffix = variables.kwargs('joint_suffix', 'Ik', kwargs, short_name='jntSfx')
        self._ctrl_shape = variables.kwargs('control_shape', ['sphere', 'diamond', 'cube'], kwargs, short_name='shape')

        self.iks = []

    def create(self):
        super(RotatePlaneIk, self).create()

        if isinstance(self._ctrl_shape, basestring):
            self._ctrl_shape = [self._ctrl_shape] * 3

        # create controls
        ctrl_objs = []
        for bp_ctrl, ctrl_shape in zip(self._bp_ctrls, self._ctrl_shape):
            namer = naming.Namer(bp_ctrl)
            ctrl = controls.create(namer.description, side=namer.side, index=namer.index, offsets=self._ctrl_offsets,
                                   parent=self._controls_grp, pos=bp_ctrl,
                                   lock_hide=attributes.Attr.rotate+attributes.Attr.scale+attributes.Attr.rotateOrder,
                                   shape=ctrl_shape, size=self._ctrl_size, color=self._ctrl_color, sub=self._sub)
            self.ctrls.append(ctrl.name)
            ctrl_objs.append(ctrl)

        # unlock rotate for ik control
        ctrl_objs[-1].unlock_attrs(attributes.Attr.rotate)
        ctrl_objs[-1].unlock_attrs(attributes.Attr.rotateOrder, keyable=False, channel_box=True)

        # set up ik handle
        ik_handle = naming.Namer(type=naming.Type.ikHandle, side=self._side, description=self._des+self._jnt_suffix,
                                 index=self._index).name
        cmds.ikHandle(startJoint=self.jnts[0], endEffector=self.jnts[-1], solver='ikRPsolver', name=ik_handle)

        # add transform to drive ik
        ik_transform = naming.Namer(type=naming.Type.transform, side=self._side, description=self._des+self._jnt_suffix,
                                    index=self._index).name
        ik_transform = transforms.create(ik_transform, pos=ctrl_objs[-1].name, lock_hide=attributes.Attr.all, vis=False,
                                         parent=self._nodes_hide_grp)
        constraints.matrix_connect(ctrl_objs[-1].world_matrix_attr, ik_transform, force=True)

        pv_transform = naming.Namer(type=naming.Type.transform, side=self._side,
                                    description=self._des+self._jnt_suffix+'Pv', index=self._index).name
        pv_transform = pv_transform.create(pv_transform, pos=ctrl_objs[1].name, lock_hide=attributes.Attr.all,
                                           vis=False, parent=self._nodes_hide_grp)
        constraints.matrix_connect(ctrl_objs[1].world_matrix_attr, pv_transform, force=True)

        # parent ik to transform
        cmds.parent(ik_handle, ik_transform)

        # connect pole vector
        # get ik handle local parent inverse matrix
        pv_parent_matrix_attr = nodeUtils.mult_matrix([ik_handle+'.parentMatrix[0]',
                                                       ik_transform+'.worldInverseMatrix[0]'], side=self._side,
                                                      description=self._des+'PvParentMatrix', index=self._index)
        pv_inverse_matrix = nodeUtils.inverse_matrix(pv_parent_matrix_attr, side=self._side,
                                                     description=self._des+'PvInverseMatrix', index=self._index)
        # pole vector constraint
        constraints.matrix_pole_vector_constraint(pv_transform+'.matrix', ik_handle, self.jnts[0],
                                                  parent_inverse_matrix=pv_inverse_matrix, force=True)

        # pole vector line
        pv_line = naming.Namer(type=naming.Type.guideLine, side=self._side, description=self._des+'Pv',
                               index=self._index).name
        pv_line = curves.create_guide_line(pv_line, [[self.jnts[0]+'.tx', self.jnts[0]+'.ty', self.jnts[0]+'.tz'],
                                                     [pv_transform+'.tx', pv_transform+'.ty', pv_transform+'.tz']],
                                           parent=self._nodes_show_grp)

        # connect root
        constraints.matrix_connect(ctrl_objs[0].world_matrix_attr, self.jnts[0],
                                   skip=attributes.Attr.rotate+attributes.Attr.scale)

        # twist attr
        cmds.addAttr(ctrl_objs[-1].name, longName='twist', attributeType='float', keyable=True)
        cmds.connectAttr(ctrl_objs[-1].name+'.twist', ik_handle+'.twist')

        # pass info
        self.nodes_hide += [pv_transform, ik_transform]
        self.nodes_show.append(pv_line)
        self.iks.append(ik_handle)
