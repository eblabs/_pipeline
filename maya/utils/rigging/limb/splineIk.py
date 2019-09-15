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
        @ splineIk
            blueprint_curve(str): blueprint curve for spline ik setup
            blueprint_controls(list): blueprint controls
            joints_number(int): generate joints evenly along the curve if no blueprint is given
            up_vector(list): generated joints' up vector, default is [0,1,0]
            auto_twist_range(bool): auto set twist start and end base on controls position
            twist_start(float): twist start position on the curve, value from 0 to 1
            twist_end(float): twist end position on the curve, value from 0 to 1
            twist_interpolation(str): twist ramp interpolation, linear/exponential up/exponential down/smooth/bump/spike
            curve_skin(dict): curve's skin cluster data
    """
    def __init__(self, **kwargs):
        super(SplineIk, self).__init__(**kwargs)
        self._bp_crv = variables.kwargs('blueprint_curve', '', kwargs, short_name=naming.Type.blueprintCurve)
        self._bp_ctrl = variables.kwargs('blueprint_controls', [], kwargs, short_name='bpCtrls')
        self._jnt_num = variables.kwargs('joints_number', 5, kwargs, short_name='jntNum')
        self._up_vector = variables.kwargs('up_vector', [0, 1, 0], kwargs, short_name='upVec')
        self._auto_twist_range = variables.kwargs('auto_twist_range', True, kwargs, short_name='autoRange')
        self._twist_start = variables.kwargs('twist_start', 0, kwargs)
        self._twist_end = variables.kwargs('twist_end', 1, kwargs)
        self._twist_interp = variables.kwargs('twist_interpolation', 'linear', kwargs, short_name='interp')
        self._crv_skin = variables.kwargs('curve_skin', None, kwargs)
        self._jnt_suffix = variables.kwargs('joint_suffix', 'SplineIk', kwargs, short_name='jntSfx')
        self._ctrl_shape = variables.kwargs('control_shape', 'cube', kwargs, short_name='shape')

        self.iks = []
        self.curve = []

    def create(self):
        super(SplineIk, self).create()
        if isinstance(self._ctrl_shape, basestring):
            self._ctrl_shape = [self._ctrl_shape] * len(self._bp_ctrl)

        # create ik curve
        crv_info = curves.get_curve_info(self._bp_crv)
        crv_ik = naming.Namer(type=naming.Type.curve, side=self._side, description=self._des+self._jnt_suffix,
                              index=self._index).name
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
            cmds.skinCluster(ctrl_jnts, crv_ik, toSelectedBones=True, dropoffRate=4, bindMethod=0,
                             name=crv_skin_cluster)
        # get curve spans
        spans = cmds.getAttr(crv_ik_shape+'.spans')
        # rebuild curve
        cmds.rebuildCurve(crv_ik, replaceOriginal=True, rebuildType=0, endKnots=1, keepRange=0, keepControlPoints=0,
                          keepEndPoints=1, keepTangents=0, span=spans, degree=3)

        # create joints if no joints are given
        if not self._bp_jnts:
            # build joints chain
            pass

        # create spline ik
        ik_handle = naming.update_name(crv_ik, type=naming.Type.ikHandle)
        cmds.ikHandle(startJoint=self.jnts[0], endEffector=self.jnts[-1], solver='ikSplineSolver', createCurve=False,
                      simplifyCurve=False, curve=crv_ik, parentCurve=False, name=ik_handle)
        cmds.parent(ik_handle, self._nodes_world_grp)

        # zero out joints offsets
        cmds.makeIdentity(self.jnts[0], apply=True, translate=True, rotate=True, scale=True, jointOrient=False)

        # set up twist
        # root twist mode
        cmds.setAttr(ik_handle+'.rootTwistMode', 1)
        # advance twist
        cmds.setAttr(ik_handle+'.dTwistControlEnable', 1)
        cmds.setAttr(ik_handle+'.dWorldUpType', 3)  # object rotation up
        # create transform as up vector reference
        trans_up = naming.update_name(crv_ik, type=naming.Type.transform,
                                      description='{}{}UpVec'.format(self._des, self._jnt_suffix))
        trans_up = transforms.create(trans_up, lock_hide=attributes.Attr.all, vis=False, pos=self.jnts[0],
                                     parent=self._nodes_hide_grp)
        # connect up vector to ik handle
        cmds.connectAttr(trans_up+'.worldMatrix[0]', ik_handle+'.dWorldUpMatrix')
        # twist set to ramp
        cmds.setAttr(ik_handle+'.dTwistValueType', 2)
        cmds.setAttr(ik_handle+'.dTwistRampMult', 1)

        # connect ramp
        ramp_twist = naming.update_name(crv_ik, type=naming.Type.ramp,
                                        description='{}{}Twist'.format(self._des, self._jnt_suffix))
        ramp_twist = nodeUtils.node(name=ramp_twist)
        cmds.connectAttr(ramp_twist+'.outColor', ik_handle+'.dTwistRamp')

        # get the second joint's parameter on curve
        pos, param_min = curves.get_closest_point_on_curve(crv_ik, self.jnts[1])
        # auto set twist range
        if self._auto_twist_range:
            pos, param_start = curves.get_closest_point_on_curve(crv_ik, ctrl_objs[0].name)
            pos, param_end = curves.get_closest_point_on_curve(crv_ik, ctrl_objs[-1].name)
        else:
            param_start = self._twist_start
            param_end = self._twist_end
        # remap from [param_min, 1] to [0, 1]
        param_start = mathUtils.remap_value(param_start, [param_min, 1], [0, 1])
        param_end = mathUtils.remap_value(param_end, [param_min, 1], [0, 1])

        # add attrs for start and end controls
        attributes.separator(ctrl_objs[-1], 'twist')
        ctrl_objs[-1].add_attrs('twist', attribute_type='float', keyable=False, channel_box=False)
        ctrl_objs[-1].add_attrs('twistStart', attribute_type='float', keyable=True, range=[0, 1],
                                default_value=param_end)

        twist_interpolations = ['linear', 'exponential up', 'exponential down', 'smooth', 'bump', 'spike']
        if self._twist_interp.lower() in twist_interpolations:
            twist_interp = twist_interpolations.index(self._twist_interp.lower()) + 1
        else:
            twist_interp = 1

        enum_name = ''
        for i in range(len(twist_interpolations)):
            # because ramp type starts with None, linear is 1
            enum_name += '{}={}:'.format(twist_interpolations[i].title, i+1)

        ctrl_objs[-1].add_attrs('twistInterp', attribute_type='enum', keyable=True, default_value=twist_interp,
                                enum=enum_name[:-1])
        cmds.connectAttr(ctrl_objs[-1].name+'.twistInterp', ramp_twist+'.interpolation')

        attributes.separator(ctrl_objs[0], 'twist')
        ctrl_objs[0].add_attrs('twist', attribute_type='float', keyable=False, channel_box=False)
        ctrl_objs[0].add_attrs('twistStart', attribute_type='float', keyable=True, range=[0, 1],
                               default_value=param_start)

        # extract twist
        for ctrl, jnt in zip([ctrl_objs[0], ctrl_objs[-1]], [self.jnts[0], self.jnts[-1]]):
            # get jnt world matrix
            jnt_matrix = cmds.getAttr(jnt+'.worldMatrix[0]')
            # get ctrl matrix
            ctrl_matrix = ctrl.world_matrix
            # get jnt local matrix under joint
            ctrl_matrix_inverse = mathUtils.inverse_matrix(ctrl_matrix)
            jnt_matrix_local = mathUtils.mult_matrix([jnt_matrix, ctrl_matrix_inverse])

            # get jnt world matrix inverse
            jnt_matrix_inverse = mathUtils.inverse_matrix(jnt_matrix)

            # mult matrix node
            mult_matrix_attr = nodeUtils.mult_matrix([jnt_matrix_local, ctrl.world_matrix_attr, jnt_matrix_inverse],
                                                     side=ctrl.side, description=ctrl.description+'.Twist',
                                                     index=ctrl.index)
            nodeUtils.twist_extraction(mult_matrix_attr, attrs=ctrl.name+'.twist')

        for i, ctrl in enumerate([ctrl_objs[0], ctrl_objs[-1]]):
            # create remap value node to remap twist start
            nodeUtils.remap(ctrl.name+'.twistStart', [0, 1], [param_min, 1], side=ctrl.side,
                            description=ctrl.description+'TwistRoot', index=ctrl.index,
                            attrs='{}.colorEntryList[{}].position'.format(ramp_twist, i))
            # connect twist value
            attributes.connect_attrs(ctrl.name+'.twist', ['{}.colorEntryList[{}].colorR'.format(ramp_twist, i),
                                                          '{}.colorEntryList[{}].colorG'.format(ramp_twist, i),
                                                          '{}.colorEntryList[{}].colorB'.format(ramp_twist, i)])
        # pass info
        self.iks = [ik_handle]
        self.curve = [crv_ik]
