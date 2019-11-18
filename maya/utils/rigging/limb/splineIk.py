# IMPORT PACKAGES

# import maya packages
import maya.cmds as cmds

# import utils
import utils.common.naming as naming
import utils.common.variables as variables
import utils.common.attributes as attributes
import utils.common.transforms as transforms
import utils.common.nodeUtils as nodeUtils
import utils.common.mathUtils as mathUtils
import utils.common.hierarchy as hierarchy
import utils.rigging.controls as controls
import utils.rigging.joints as joints
import utils.rigging.constraints as constraints
import utils.modeling.curves as curves

# import limb
import limb


# CLASS
class SplineIk(limb.Limb):
    """
    spline ik rig limb

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
        @ splineIk
            blueprint_curve(str): blueprint curve for spline ik setup
            blueprint_controls(list): blueprint controls
            joints_number(int): generate joints evenly along the curve if no blueprint is given
            rotation_up_vector(list): generated joints' up vector, default is [0,1,0]
            auto_twist_range(bool): auto set twist start and end base on controls position
            twist_start(float): twist start position on the curve, value from 0 to 1
            twist_end(float): twist end position on the curve, value from 0 to 1
            twist_interpolation(str): twist ramp interpolation, linear/smooth/spline
            segment_twist(bool): add twist attribute to control each segment twist
            segment_twist_interpolation(str): segment twist ramp interpolation, linear/smooth/spline
            curve_skin(dict): curve's skin cluster data
            curve_name(str): ik curve's name when creation
                            (because in component level, we need curve name to save skin data without running the
                             function, by passing the name to override, I don't need to hardcoded the curve name
                             everywhere)
    """
    def __init__(self, **kwargs):
        super(SplineIk, self).__init__(**kwargs)
        self._bp_crv = variables.kwargs('blueprint_curve', '', kwargs, short_name=naming.Type.blueprintCurve)
        self._bp_ctrl = variables.kwargs('blueprint_controls', [], kwargs, short_name='bpCtrls')
        self._jnt_num = variables.kwargs('joints_number', 5, kwargs, short_name='jntNum')
        self._rot_up_vector = variables.kwargs('rotation_up_vector', [0, 1, 0], kwargs, short_name='rotUpVec')
        self._auto_twist_range = variables.kwargs('auto_twist_range', True, kwargs, short_name='autoRange')
        self._twist_start = variables.kwargs('twist_start', 0, kwargs)
        self._twist_end = variables.kwargs('twist_end', 1, kwargs)
        self._twist_interp = variables.kwargs('twist_interpolation', 'linear', kwargs, short_name='interp')
        self._segment_twist = variables.kwargs('segment_twist', True, kwargs, short_name='segmentTwist')
        self._segment_twist_interp = variables.kwargs('segment_twist_interpolation', 'linear', kwargs,
                                                      short_name='segmentInterp')
        self._crv_skin = variables.kwargs('curve_skin', None, kwargs)
        self._jnt_suffix = variables.kwargs('joint_suffix', 'SplineIk', kwargs, short_name='jntSfx')
        self._ctrl_shape = variables.kwargs('control_shape', 'cube', kwargs, short_name='shape')
        self._crv_name = variables.kwargs('curve_name', None, kwargs)

        self.iks = []
        self.curve = []
        self.ramp_twist = None

    def create(self):
        super(SplineIk, self).create()
        if isinstance(self._ctrl_shape, basestring):
            self._ctrl_shape = [self._ctrl_shape] * len(self._bp_ctrl)

        # create ik curve
        crv_info = curves.get_curve_shape_info(self._bp_crv)
        if self._crv_name:
            crv_ik = self._crv_name
        else:
            crv_ik = naming.Namer(type=naming.Type.curve, side=self._side, description=self._des+self._jnt_suffix,
                                  index=1).name
        crv_ik, crv_ik_shape = curves.create_curve(crv_ik, crv_info['control_vertices'], crv_info['knots'],
                                                   degree=crv_info['degree'], form=crv_info['form'],
                                                   parent=self._nodes_world_grp)

        # create controls and joints to driven curve
        ctrl_objs = []
        ctrl_jnts = []
        for bp_ctrl, ctrl_shape in zip(self._bp_ctrl, self._ctrl_shape):
            namer = naming.Namer(bp_ctrl)
            ctrl = controls.create(namer.description + self._jnt_suffix, side=namer.side, index=namer.index,
                                   offsets=self._ctrl_offsets, parent=self._controls_grp, pos=bp_ctrl,
                                   lock_hide=attributes.Attr.rotate+attributes.Attr.scale+attributes.Attr.rotateOrder,
                                   shape=ctrl_shape, size=self._ctrl_size, color=self._ctrl_color, sub=self._sub)
            # create transform to move with control
            ctrl_trans = naming.update_name(ctrl.name, type=naming.Type.transform)
            ctrl_trans = transforms.create(ctrl_trans, lock_hide=attributes.Attr.all, vis=False, pos=ctrl.name,
                                           parent=self._nodes_hide_grp)
            # create joint and parent to the transform
            ctrl_jnt = joints.create_on_node(ctrl.name, naming.Type.control, naming.Type.joint, suffix='Ctrl',
                                             parent=ctrl_trans)

            # connect control with transform
            constraints.matrix_connect(ctrl.world_matrix_attr, ctrl_trans, skip=attributes.Attr.scale)

            self.ctrls.append(ctrl.name)
            ctrl_objs.append(ctrl)
            ctrl_jnts.append(ctrl_jnt)

        # unlock start and end controls rotation
        ctrl_objs[0].unlock_attrs(attributes.Attr.rotate+attributes.Attr.rotateOrder, keyable=True, channel_box=True)
        ctrl_objs[-1].unlock_attrs(attributes.Attr.rotate + attributes.Attr.rotateOrder, keyable=True, channel_box=True)

        # skin the curve
        crv_bind = False
        if self._crv_skin:
            # load the curve skin data, return True/False and set to crv_bind
            pass

        if not crv_bind:
            # give it a default skin
            crv_skin_cluster = naming.update_name(crv_ik, type=naming.Type.skinCluster)
            cmds.skinCluster(ctrl_jnts, crv_ik, toSelectedBones=True, dropoffRate=6, bindMethod=0,
                             name=crv_skin_cluster)
        # get curve spans
        spans = cmds.getAttr(crv_ik_shape+'.spans')
        # rebuild curve
        cmds.rebuildCurve(crv_ik, replaceOriginal=True, rebuildType=0, endKnots=1, keepRange=0, keepControlPoints=0,
                          keepEndPoints=1, keepTangents=0, spans=spans, degree=3)

        # create joints if no joints are given
        if not self._bp_jnts:
            # build joints chain
            self.jnts = joints.create_joints_along_curve(crv_ik, self._jnt_num, aim_vector=[1, 0, 0],
                                                         up_vector=[0, 1, 0], rotation_up_vector=self._rot_up_vector,
                                                         uniform_type='length', aim_type='next', flip_check=True,
                                                         hierarchy=True, parent=self._joints_grp)

        # create spline ik
        ik_handle = naming.update_name(crv_ik, type=naming.Type.ikHandle)
        cmds.ikHandle(startJoint=self.jnts[0], endEffector=self.jnts[-1], solver='ikSplineSolver', createCurve=False,
                      simplifyCurve=False, curve=crv_ik, parentCurve=False, name=ik_handle)

        hierarchy.parent_node(ik_handle, self._nodes_world_grp)

        # zero out joints offsets
        cmds.makeIdentity(self.jnts[0], apply=True, translate=True, rotate=True, scale=True, jointOrient=False)

        # create twist joints
        jnts_num = len(self.jnts)
        jnts_twist = []
        for jnt in self.jnts:
            jnt_twist = joints.create_on_node(jnt, None, None, suffix='Twist', parent=jnt)
            jnts_twist.append(jnt_twist)

        # auto set twist range
        pos, param_start = curves.get_closest_point_on_curve(crv_ik, ctrl_objs[0].name)
        pos, param_end = curves.get_closest_point_on_curve(crv_ik, ctrl_objs[-1].name)
        if not self._auto_twist_range:
            param_start = self._twist_start
            param_end = self._twist_end

        # get third vector to check flip
        pos_a = cmds.xform(self.jnts[0], query=True, translation=True, worldSpace=True)
        pos_b = cmds.xform(self.jnts[1], query=True, translation=True, worldSpace=True)
        tangent_zero = mathUtils.get_vector_from_points(pos_b, pos_a)
        z_vec = mathUtils.cross_product(tangent_zero, self._rot_up_vector)

        mash_distribute_nodes = []
        mash_breakout_nodes = []
        for ctrl, param in zip([ctrl_objs[0], ctrl_objs[-1]], [param_start, param_end]):
            # add twist attrs for start and end controls
            attributes.separator(ctrl.name, 'twist')
            ctrl.add_attrs('twist', attribute_type='float', keyable=False, channel_box=False)
            ctrl.add_attrs('twistOffset', attribute_type='float', keyable=True, channel_box=True)
            ctrl.add_attrs('twistStart', attribute_type='float', keyable=True, range=[0, 1], default_value=param)

            twist_extract_attr = self.extract_twist(ctrl.name, ctrl.world_matrix_attr, crv_ik, self._rot_up_vector,
                                                    flip_check_vector=z_vec)

            # connect to twist
            nodeUtils.equation('{}+{}.twistOffset'.format(twist_extract_attr, ctrl.name), side=ctrl.side,
                               description=ctrl.description+'TwistSum', index=ctrl.index, attrs=ctrl.name+'.twist')

            # create mash node
            mash_distribute, mash_breakout = nodeUtils.mash_distribute(ctrl.name+'.twist', jnts_num, 'rotateX',
                                                                       side=ctrl.side, index=ctrl.index,
                                                                       description=ctrl.description+'Twist',
                                                                       ramp_position=[0, 1], ramp_values=[0, 1],
                                                                       ramp_interpolation=1)

            # add to list
            mash_distribute_nodes.append(mash_distribute)
            mash_breakout_nodes.append(mash_breakout)

        # connect start mash node
        attributes.connect_attrs([ctrl_objs[0].name+'.twistStart', ctrl_objs[-1].name+'.twistStart',
                                  ctrl_objs[0].name+'.twistStart', ctrl_objs[-1].name+'.twistStart'],
                                 ['{}.rotationRamp[0].rotationRamp_Position'.format(mash_distribute_nodes[0]),
                                  '{}.rotationRamp[1].rotationRamp_Position'.format(mash_distribute_nodes[0]),
                                  '{}.rotationRamp[0].rotationRamp_Position'.format(mash_distribute_nodes[1]),
                                  '{}.rotationRamp[1].rotationRamp_Position'.format(mash_distribute_nodes[1])],
                                 force=True)
        attributes.set_attrs(['{}.rotationRamp[0].rotationRamp_FloatValue'.format(mash_distribute_nodes[0]),
                              '{}.rotationRamp[1].rotationRamp_FloatValue'.format(mash_distribute_nodes[0]),
                              '{}.rotationRamp[0].rotationRamp_FloatValue'.format(mash_distribute_nodes[1]),
                              '{}.rotationRamp[1].rotationRamp_FloatValue'.format(mash_distribute_nodes[1])],
                             [1, 0, 0, 1], force=True)

        # add attr for twist interp
        twist_interpolations = ['linear', 'smooth', 'spline']
        if self._twist_interp.lower() in twist_interpolations:
            twist_interp = twist_interpolations.index(self._twist_interp.lower()) + 1
        else:
            twist_interp = 1

        enum_name = ''
        for i in range(len(twist_interpolations)):
            # because ramp type starts with None, linear is 1
            enum_name += '{}={}:'.format(twist_interpolations[i].title(), i + 1)

        ctrl_objs[-1].add_attrs('twistInterp', attribute_type='enum', keyable=True, default_value=twist_interp,
                                enum_name=enum_name[:-1])
        attributes.connect_attrs([ctrl_objs[-1].name+'.twistInterp', ctrl_objs[-1].name+'.twistInterp'],
                                 ['{}.rotationRamp[0].rotationRamp_Interp'.format(mash_distribute_nodes[0]),
                                  '{}.rotationRamp[0].rotationRamp_Interp'.format(mash_distribute_nodes[1])],
                                 force=True)

        # in-between twist control
        ctrl_num = len(ctrl_objs)
        if ctrl_num > 2 and self._segment_twist:
            attributes.separator(ctrl_objs[0].name, 'segmentTwist')
            attributes.separator(ctrl_objs[-1].name, 'segmentTwist')
            ctrl_objs[0].add_attrs('segmentTwistOffset', attribute_type='float', keyable=True, channel_box=True)
            ctrl_objs[-1].add_attrs('segmentTwistOffset', attribute_type='float', keyable=True, channel_box=True)

            # create segment twist interp
            if self._segment_twist_interp.lower() in twist_interpolations:
                twist_interp = twist_interpolations.index(self._segment_twist_interp.lower()) + 1
            else:
                twist_interp = 1

            ctrl_objs[-1].add_attrs('segmentTwistInterp', attribute_type='enum', keyable=True,
                                    default_value=twist_interp, enum_name=enum_name[:-1])

            # create first segment mash
            mash_distribute, mash_breakout = nodeUtils.mash_distribute(ctrl_objs[0].name+'.segmentTwistOffset',
                                                                       jnts_num, 'rotateX',
                                                                       side=ctrl_objs[0].side, index=ctrl_objs[0].index,
                                                                       description=ctrl_objs[0].description+'SegTwist',
                                                                       ramp_position=[0, 1], ramp_values=[1, 0],
                                                                       ramp_interpolation=1)
            # connect with ctrl
            attributes.connect_attrs([ctrl_objs[-1].name+'.segmentTwistInterp', ctrl_objs[0].name+'.twistStart'],
                                     ['{}.rotationRamp[0].rotationRamp_Interp'.format(mash_distribute),
                                      '{}.rotationRamp[0].rotationRamp_Position'.format(mash_distribute)],
                                     force=True)

            mash_distribute_nodes.append(mash_distribute)
            mash_breakout_nodes.append(mash_breakout)

            # get parameter distance
            param_dis = param_end - param_start
            # in-between fall off is from previous point to param to next point
            param_pre = ctrl_objs[0].name+'.twistStart'
            mash_dis_pre = mash_distribute

            for i, ctrl in enumerate(ctrl_objs[1:ctrl_num-1]):
                # loop in each in-between control
                # add attrs
                attributes.separator(ctrl.name, 'segmentTwist')
                ctrl.add_attrs('segmentTwistOffset', attribute_type='float', keyable=True, channel_box=True)
                ctrl.add_attrs('twist', attribute_type='float', keyable=False, channel_box=False)

                # get parameter on curve
                pos, param = curves.get_closest_point_on_curve(crv_ik, ctrl.name)

                # extract twist
                twist_extract_attr = self.extract_twist(ctrl.name, ctrl.local_matrix_attr, crv_ik, self._rot_up_vector,
                                                        flip_check_vector=z_vec)

                # connect to twist
                nodeUtils.equation('{}+{}.segmentTwistOffset'.format(twist_extract_attr, ctrl.name), side=ctrl.side,
                                   description=ctrl.description+'SegTwistSum', index=ctrl.index,
                                   attrs=ctrl.name+'.twist')

                # get parameter weight base on parameter distance
                weight = (param - param_start)/param_dis
                # get parameter connect with start and end
                param_attr = nodeUtils.equation('{}*{}.twistStart+{}*{}.twistStart'.format(weight, ctrl_objs[-1].name,
                                                                                           1-weight, ctrl_objs[0].name),
                                                side=ctrl.side, description=ctrl.description+'ParamOffset',
                                                index=ctrl.index)

                # create mash node
                mash_distribute, mash_breakout = nodeUtils.mash_distribute(ctrl.name+'.twist',
                                                                           jnts_num, 'rotateX',
                                                                           side=ctrl.side, index=ctrl.index,
                                                                           description=ctrl.description+'SegTwist',
                                                                           ramp_position=[0, 0.5, 1],
                                                                           ramp_values=[0, 1, 0],
                                                                           ramp_interpolation=1)

                # connect attrs
                attributes.connect_attrs([param_pre, param_attr, ctrl_objs[-1].name+'.segmentTwistInterp',
                                          ctrl_objs[-1].name+'.segmentTwistInterp'],
                                         ['{}.rotationRamp[0].rotationRamp_Position'.format(mash_distribute),
                                          '{}.rotationRamp[1].rotationRamp_Position'.format(mash_distribute),
                                          '{}.rotationRamp[0].rotationRamp_Interp'.format(mash_distribute),
                                          '{}.rotationRamp[1].rotationRamp_Interp'.format(mash_distribute)],
                                         force=True)
                if mash_dis_pre:
                    if i > 0:
                        ramp_index = 2
                    else:
                        ramp_index = 1
                    cmds.connectAttr(param_attr, '{}.rotationRamp[{}].rotationRamp_Position'.format(mash_dis_pre,
                                                                                                    ramp_index))

                # add to list
                mash_breakout_nodes.append(mash_breakout)
                mash_dis_pre = mash_distribute
                param_pre = param_attr

            # add end ctrl param to last mash
            cmds.connectAttr(ctrl_objs[-1].name+'.twistStart',
                             '{}.rotationRamp[2].rotationRamp_Position'.format(mash_dis_pre))

            # add last mash
            mash_distribute, mash_breakout = nodeUtils.mash_distribute(ctrl_objs[-1].name+'.segmentTwistOffset',
                                                                       jnts_num, 'rotateX', side=ctrl_objs[-1].side,
                                                                       index=ctrl_objs[-1].index,
                                                                       description=ctrl_objs[-1].description+'SegTwist',
                                                                       ramp_position=[0, 1], ramp_values=[0, 1],
                                                                       ramp_interpolation=1)
            # connect with ctrl
            attributes.connect_attrs([ctrl_objs[-1].name+'.segmentTwistInterp', param_pre,
                                      ctrl_objs[-1].name+'.twistStart'],
                                     ['{}.rotationRamp[0].rotationRamp_Interp'.format(mash_distribute),
                                      '{}.rotationRamp[0].rotationRamp_Position'.format(mash_distribute),
                                      '{}.rotationRamp[1].rotationRamp_Position'.format(mash_distribute)],
                                     force=True)

            mash_distribute_nodes.append(mash_distribute)
            mash_breakout_nodes.append(mash_breakout)

        # connect mash node to twist joints
        for i, jnt in enumerate(jnts_twist):
            # get jnt namer
            namer = naming.Namer(jnt)
            # create plusMinusAverage node
            pmav = nodeUtils.node(type=naming.Type.plusMinusAverage, side=namer.side,
                                  description=namer.description+'Sum', index=namer.index)
            # loop in each breakout node to connect
            # mash breakout need to connect the parent attr to be evaluated properly
            for j, mash_breakout in enumerate(mash_breakout_nodes):
                cmds.connectAttr('{}.outputs[{}].rotate'.format(mash_breakout, i),
                                 '{}.input3D[{}]'.format(pmav, j))
            # connect to jnt
            cmds.connectAttr(pmav+'.output3Dx', jnt+'.rx')

        # pass info
        self.iks = [ik_handle]
        self.curve = [crv_ik]
        self.jnts = jnts_twist

    @staticmethod
    def extract_twist(node, matrix_attr, curve, up_vector, flip_check_vector=None):
        """
        extract twist value along the curve,
        take the closest tangent as main axis, joint chain's up vector, and build the coordinate system
        Args:
            node(str): node to be extracted
            matrix_attr(str): matrix attribute, normally is sth like node.worldMatrix[0]
            curve(str)
            up_vector(list)
        Keyword Args:
             flip_check_vector(list): vector to check flipping

        Returns:
            twist_attr(str): twist attribute
        """
        # get namer
        namer = naming.Namer(node)

        # get tangent
        pos, param = curves.get_closest_point_on_curve(curve, node)
        tangent = curves.get_tangent_at_param(curve, param)

        # build coordinate system
        vec_x_offset, vec_y_offset, vec_z_offset = mathUtils.build_coordinate_system(tangent, up_vector,
                                                                                     flip_check_vec=flip_check_vector)

        # get offset matrix
        pos = cmds.xform(node, query=True, translation=True, worldSpace=True)
        matrix_offset = mathUtils.four_by_four_matrix(vec_x_offset, vec_y_offset, vec_z_offset, pos)
        matrix_node = cmds.getAttr(matrix_attr)
        matrix_offset_local = mathUtils.get_local_matrix(matrix_offset, matrix_node)
        matrix_offset_inverse = mathUtils.inverse_matrix(matrix_offset)

        # twist extraction
        mult_matrix_attr = nodeUtils.mult_matrix([matrix_offset_local, matrix_attr,
                                                  matrix_offset_inverse], side=namer.side,
                                                 description=namer.description+'Twist', index=namer.index)
        twist_extract_attr = nodeUtils.twist_extraction(mult_matrix_attr)

        return twist_extract_attr


