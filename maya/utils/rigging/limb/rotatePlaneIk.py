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
import fkChain


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
            blueprint_controls(list): ik control blueprint, [root, pole_vector, ik, ground] ground control is optional
            single_chain_iks(int): will create single chain ik per segment after rotate plane ik, minimum is 0,
                                   maximum is 2, blueprint joints number need to be at least greater than 3
            blueprint_reverse_controls(list): reverse set up's controls blueprints, normally for foot or hand
                                              structure like [heelRoll, toeRoll, sideInn, sideOut, ballRoll, toeTap]
            ik_handle_offset(bool): add a control to offset ik handle
    """
    def __init__(self, **kwargs):
        super(RotatePlaneIk, self).__init__(**kwargs)
        self._bp_ctrls = variables.kwargs('blueprint_controls', [], kwargs, short_name='bpCtrl')
        self._jnt_suffix = variables.kwargs('joint_suffix', 'Ik', kwargs, short_name='jntSfx')
        self._ctrl_shape = variables.kwargs('control_shape', ['sphere', 'diamond', 'cube', 'cube'], kwargs,
                                            short_name='shape')
        self._sc_iks = variables.kwargs('single_chain_iks', 0, kwargs, short_name='scIks')
        self._bp_rvs = variables.kwargs('blueprint_reverse_controls', [], kwargs, short_name='bpRvs')
        self._ik_offset = variables.kwargs('ik_handle_offset', False, kwargs, short_name='ikOffset')

        self.iks = []
        self.rvs_ctrls = []

    def create(self):
        super(RotatePlaneIk, self).create()

        if isinstance(self._ctrl_shape, basestring):
            self._ctrl_shape = [self._ctrl_shape] * 4

        # create controls
        ctrl_objs = []
        for bp_ctrl, ctrl_shape in zip(self._bp_ctrls, self._ctrl_shape):
            namer = naming.Namer(bp_ctrl)
            ctrl = controls.create(namer.description, side=namer.side, index=namer.index, offsets=self._ctrl_offsets,
                                   parent=self._controls_grp, pos=bp_ctrl, lock_hide=attributes.Attr.scale,
                                   shape=ctrl_shape, size=self._ctrl_size, color=self._ctrl_color, sub=self._sub)
            self.ctrls.append(ctrl.name)
            ctrl_objs.append(ctrl)

        # lock rotate for root and pole vector control
        ctrl_objs[0].lock_hide_attrs(attributes.Attr.rotate+attributes.Attr.rotateOrder)
        ctrl_objs[1].lock_hide_attrs(attributes.Attr.rotate+attributes.Attr.rotateOrder)

        # check single chain ik
        jnts_num = len(self.jnts)
        if jnts_num > 3 and self._sc_iks:
            jnts_extra = jnts_num - 3
            if self._sc_iks > jnts_extra:
                self._sc_iks = jnts_extra
            rp_jnts = self.jnts[0:jnts_num-self._sc_iks]
            sc_jnts = self.jnts[jnts_num-self._sc_iks:]
        else:
            rp_jnts = self.jnts
            sc_jnts = []

        # get ik and ground ctrl
        ik_ctrl_obj = ctrl_objs[2]
        if len(self._bp_ctrls) > 3:
            ground_ctrl_obj = ctrl_objs[3]
            cmds.parent(ik_ctrl_obj.zero, ground_ctrl_obj.output)
        else:
            ground_ctrl_obj = None

        # set up ik handle
        ik_handle = naming.Namer(type=naming.Type.ikHandle, side=self._side,
                                 description=self._des+self._jnt_suffix+'Rp', index=self._index).name
        cmds.ikHandle(startJoint=rp_jnts[0], endEffector=rp_jnts[-1], solver='ikRPsolver', name=ik_handle)

        self.iks.append(ik_handle)

        # add transform to drive ik
        if ground_ctrl_obj:
            ground_transform = naming.Namer(type=naming.Type.transform, side=ground_ctrl_obj.side,
                                            description=ground_ctrl_obj.description, index=ground_ctrl_obj.index).name
            ground_transform = transforms.create(ground_transform, pos=ground_ctrl_obj.name,
                                                 lock_hide=attributes.Attr.all, vis=False, parent=self._nodes_hide_grp)
            constraints.matrix_connect(ground_ctrl_obj.world_matrix_attr, ground_transform, force=True)
            ik_transform_parent = ground_transform
        else:
            ground_transform = None
            ik_transform_parent = self._nodes_hide_grp

        ik_transform = naming.Namer(type=naming.Type.transform, side=ik_ctrl_obj.side,
                                    description=ik_ctrl_obj.description, index=ik_ctrl_obj.index).name
        ik_transform = transforms.create(ik_transform, pos=ik_ctrl_obj.name, lock_hide=attributes.Attr.all, vis=False,
                                         parent=ik_transform_parent)
        constraints.matrix_connect(ik_ctrl_obj.world_matrix_attr, ik_transform, force=True)

        pv_transform = naming.Namer(type=naming.Type.transform, side=self._side,
                                    description=self._des+self._jnt_suffix+'Pv', index=self._index).name
        pv_transform = transforms.create(pv_transform, pos=ctrl_objs[1].name, lock_hide=attributes.Attr.all,
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
        constraints.matrix_pole_vector_constraint(pv_transform+'.matrix', ik_handle, rp_jnts[0],
                                                  parent_inverse_matrix=pv_inverse_matrix, force=True)

        # pole vector line
        pv_jnt_mult_matrix_attr = nodeUtils.mult_matrix([rp_jnts[1]+'.matrix', rp_jnts[0]+'.matrix'], side=self._side,
                                                        descirption=self._des+'PvJntPos', index=self._index)
        pv_jnt_decompose_node = nodeUtils.node(type=naming.Type.decomposeMatrix, side=self._side,
                                               description=self._des+'PvJntPos', index=self._index)
        cmds.connectAttr(pv_jnt_mult_matrix_attr, pv_jnt_decompose_node+'.inputMatrix')
        pv_line = naming.Namer(type=naming.Type.guideLine, side=self._side, description=self._des+'Pv',
                               index=self._index).name
        pv_line = curves.create_guide_line(pv_line, [[pv_jnt_decompose_node+'.outputTranslateX',
                                                      pv_jnt_decompose_node+'.outputTranslateY',
                                                      pv_jnt_decompose_node+'.outputTranslateZ'],
                                                     [pv_transform+'.translateX', pv_transform+'.translateY',
                                                      pv_transform+'.translateZ']],
                                           parent=self._nodes_show_grp)

        # connect root
        constraints.matrix_connect(ctrl_objs[0].world_matrix_attr, rp_jnts[0],
                                   skip=attributes.Attr.rotate+attributes.Attr.scale)

        # twist attr
        cmds.addAttr(ctrl_objs[2].name, longName='twist', attributeType='float', keyable=True)
        cmds.connectAttr(ctrl_objs[2].name+'.twist', ik_handle+'.twist')

        # ik handle offset control
        if self._ik_offset:
            ik_offset_ctrl_obj = controls.create(self._des+'IkOffset', side=self._side, index=self._index,
                                                 offsets=self._ctrl_offsets, parent=ik_ctrl_obj.output,
                                                 pos=ik_handle, shape='handle', size=self._ctrl_size,
                                                 lock_hide=attributes.Attr.rotateScale+attributes.Attr.rotateOrder,
                                                 color=self._ctrl_color, sub=self._sub)
            ik_ctrl_obj.add_attrs('ikOffsetControlVis', attribute_type='long', range=[0, 1], default_value=0,
                                  keyable=False, channel_box=True)
            cmds.connectAttr(ik_ctrl_obj.name+'.ikOffsetControlVis', ik_offset_ctrl_obj.zero+'.visibility')
            # control the ik handle
            constraints.matrix_connect(ik_offset_ctrl_obj.world_matrix_attr, ik_handle,
                                       skip=['rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ'])
        else:
            ik_offset_ctrl_obj = None

        # single chain iks
        if sc_jnts:
            sc_iks = []
            start_jnt = rp_jnts[-1]
            for jnt, sfx in zip(sc_jnts, ['A', 'B']):
                ik_handle = naming.Namer(type=naming.Type.ikHandle, side=self._side,
                                         description=self._des + self._jnt_suffix + 'SC' + sfx, index=self._index).name
                cmds.ikHandle(startJoint=start_jnt, endEffector=jnt, solver='ikSCsolver', name=ik_handle)
                cmds.parent(ik_handle, ik_transform)  # parent ik handle to ik control's transform
                start_jnt = jnt
                sc_iks.append(ik_handle)

            # reverse set up
            if self._bp_rvs and len(self._bp_rvs) >= 5:

                kwargs = {'side': self._side,
                          'description': self._des,
                          'index': self._index,
                          'blueprint_joints': self._bp_rvs[:5],
                          'joint_suffix': '',
                          'create_joints': True,
                          'offsets': self._ctrl_offsets,
                          'control_size': self._ctrl_size,

                          'controls_group': ik_ctrl_obj.output,
                          'joints_group': ik_transform,

                          'lock_hide': attributes.Attr.translate + attributes.Attr.scale,
                          'control_shape': ['cone', 'cone', 'cone', 'cone', 'rotate'],
                          'end_joint': True}

                fk_limb = fkChain.FkChain(**kwargs)
                fk_limb.create()

                self.rvs_ctrls = fk_limb.ctrls

                # parent ik offset ctrl
                if self._ik_offset:
                    ctrl_obj = controls.Control(self.rvs_ctrls[4])
                    cmds.parent(ik_offset_ctrl_obj.zero, ctrl_obj.output)

                # parent iks
                cmds.parent(self.iks + sc_iks, fk_limb.jnts[-1])

                # re-parent if has ground ctrl
                if ground_ctrl_obj:
                    cmds.parent(fk_limb.jnts[0], ground_transform)
                    root_ctrl_obj = controls.Control(fk_limb.ctrls[0])
                    cmds.parent(root_ctrl_obj.zero, ground_ctrl_obj.output)

                    # parent joints and ctrl under side to ik ctrl and transform
                    cmds.parent(fk_limb.jnts[4], ik_transform)
                    ctrl_obj = controls.Control(fk_limb.ctrls[4])
                    cmds.parent(ctrl_obj.zero, ik_ctrl_obj.output)

                    # parent ik control to rvs ctrl, parent ik transform to joint
                    # unlock transform first
                    attributes.unlock_attrs(ik_transform, attributes.Attr.all)
                    cmds.parent(ik_transform, fk_limb.jnts[3])
                    # lock back
                    attributes.lock_hide_attrs(ik_transform, attributes.Attr.all)
                    # parent ik control
                    ctrl_obj = controls.Control(fk_limb.ctrls[3])
                    cmds.parent(ik_ctrl_obj.zero, ctrl_obj.output)

                # check if need tap
                if len(self._bp_rvs) > 5 and self._sc_iks == 2:
                    # create fk control for tap
                    if ground_ctrl_obj:
                        ctrl_obj = ik_ctrl_obj
                        jnt_grp = ik_transform
                    else:
                        ctrl_obj = controls.Control(self.rvs_ctrls[-2])
                        jnt_grp = fk_limb.jnts[-2]
                    kwargs = {'side': self._side,
                              'description': self._des,
                              'index': self._index,
                              'blueprint_joints': [self._bp_rvs[5]],
                              'joint_suffix': '',
                              'create_joints': True,
                              'offsets': self._ctrl_offsets,
                              'control_size': self._ctrl_size,

                              'controls_group': ctrl_obj.output,
                              'joints_group': jnt_grp,

                              'lock_hide': attributes.Attr.translate + attributes.Attr.scale,
                              'control_shape': 'pin',
                              'end_joint': True}

                    fk_limb = fkChain.FkChain(**kwargs)
                    fk_limb.create()

                    self.rvs_ctrls += fk_limb.ctrls

                    # parent ik
                    cmds.parent(sc_iks[1], fk_limb.jnts[0])

            # pass info
            self.iks += sc_iks

        # pass info
        self.nodes_hide += [pv_transform, ik_transform]
        self.nodes_show.append(pv_line)
