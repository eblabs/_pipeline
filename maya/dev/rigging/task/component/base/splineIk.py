# IMPORT PACKAGES

# import os
import os

# import utils
import utils.common.naming as naming
import utils.rigging.limb.splineIk as splineIkLimb
import utils.rigging.buildUtils as buildUtils

# import task
import dev.rigging.task.component.core.component as component


# CLASS
class SplineIk(component.Component):
    """
    single chain ik component

    Keyword Args:
        mirror(bool): [mirror] mirror component, default is False
        side(str): [side] component's side, default is middle
        description(str): [description] component's description
        description suffix(str): [description_suffix] if the component nodes description need additional suffix,
                                                      like Ik, Fk etc, put it here, default is SplineIk
        blueprint joints(list): [bp_jnts] component's blueprint joints
        offsets(int): [ctrl_offsets] component's controls' offset groups number, default is 1
        control_size(float): [ctrl_size] component's controls' size, default is 1.0
        input connection(str):  [input_connect] component's input connection, should be a component's joint's output
                                                matrix, or an existing maya node's matrix attribute
        blueprint curve(str): [bp_crv] blueprint curve for spline ik setup
        blueprint controls(list): [bp_ctrls] blueprint controls, order is from start to end
        joints number(int): [jnts_num] generate joints evenly along the curve if no blueprint is given,
                                       default is 5, minimum is 3
        rotation up vector(list): [rot_up_vector] generated joints' up vector, default is [0,1,0]
        automatic set twist range(bool): [auto_twist_range] auto set twist start and end base on controls position,
                                         default is True
        twist start(float): [twist start] twist start position on the curve, value from 0 to 1, default is 0
        twist end(float): [twist end] twist end position on the curve, value from 0 to 1, default is 1
        twist interpolation(str): [twist_interp] twist ramp interpolation, linear/smooth/spline, default is linear
        segment twist(bool): [segment twist] add twist attribute to control each segment twist, default is True
        segment twist interpolation(str): [segment_twist_interp] segment twist ramp interpolation, linear/smooth/spline,
                                                                 default is linear
        curve weights(list): [crv_skin_path] curve's skin cluster data to override the auto generate one,
                                             template is [{'project': '', 'asset': '', 'rig_type': ''}]

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
        self.bp_crv = None
        self.bp_ctrls = None
        self.jnts_num = None
        self.rot_up_vector = None
        self.auto_twist_range = None
        self.twist_start = None
        self.twist_end = None
        self.twist_interp = None
        self.segment_twist = None
        self.segment_twist_interp = None
        self.crv_skin_path = None

        super(SplineIk, self).__init__(*args, **kwargs)

        self._save = True  # set save to True so can use ui to save the curve's skin data

        self._task = 'dev.rigging.task.component.base.splineIk'
        self._save = True  # it has save data function
        self._jnt_suffix = 'SplineIk'
        self._iks = []
        self._curve = []
        self._ramp_twist = None

        # curve name
        self._crv_name = None

        # we need to save the attr name before mirror behavior, so the flipped side will load the same data
        self._name_no_flip = None

    def register_kwargs(self):
        super(SplineIk, self).register_kwargs()
        self.register_attribute('blueprint curve', '', attr_name='bp_crv', attr_type='str', select=True,
                                hint="blueprint curve for spline ik setup", skippable=False)
        self.register_attribute('blueprint controls', [], attr_name='bp_ctrls', attr_type='list', select=True,
                                hint="blueprint controls, order is from start to end", skippable=False)
        self.register_attribute('joints number', 5, attr_name='jnts_num', attr_type='int', min=3,
                                hint="generate joints evenly along the curve if no blueprint is given")
        self.register_attribute('rotation up vector', [0, 1, 0], attr_name='rot_up_vector', attr_type='list',
                                template=None, hint="generate joints base on the given up vector")
        self.register_attribute('automatic set twist range', True, attr_name='auto_twist_range', attr_type='bool',
                                hint="auto set twist start and end base on controls position")
        self.register_attribute('twist start', 0, attr_name='twist_start', attr_type='float', min=0, max=1,
                                hint="twist start position on the curve, value from 0 to 1")
        self.register_attribute('twist end', 1, attr_name='twist_end', attr_type='float', min=0, max=1,
                                hint="twist end position on the curve, value from 0 to 1")
        self.register_attribute('twist interpolation', 'linear', attr_name='twist_interp', attr_type='enum',
                                enum=['linear', 'smooth', 'spline'], hint="twist ramp interpolation")
        self.register_attribute('segment twist', True, attr_name='segment_twist', attr_type='bool',
                                hint="add twist attribute to control each segment twist")
        self.register_attribute('segment twist interpolation', 'linear', attr_name='segment_twist_interp',
                                attr_type='enum',  enum=['linear', 'smooth', 'spline'],
                                hint="segment twist ramp interpolation")
        self.register_attribute('curve weights', [{'project': '', 'asset': '', 'rig_type': ''}],
                                attr_name='crv_skin_path', attr_type='list', select=False, template=None,
                                hint="curve's skin cluster data to override the auto generate one")

        self.update_attribute('description suffix', default='SplineIk')

    def create_component(self):
        super(SplineIk, self).create_component()
        # get curve name
        self._generate_curve_name()

        # get skin data from crv_skin_path
        crv_skin_data = None
        if self.crv_skin_path:
            # get path
            if self._name_no_flip:
                attr_name = self._name_no_flip
            else:
                attr_name = self._name
            self.crv_skin_path = buildUtils.get_data_path(attr_name, self.rig_type, self.asset, self.project,
                                                          warning=False, check_exist=True)
            # get curve skin data
            pass

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

                  'blueprint_curve': self.bp_crv,
                  'blueprint_controls': self.bp_ctrls,
                  'joints_number': self.jnts_num,
                  'rotation_up_vector': self.rot_up_vector,
                  'auto_twist_range': self.auto_twist_range,
                  'twist_start': self.twist_start,
                  'twist_end': self.twist_end,
                  'twist_interpolation': self.twist_interp,
                  'segment_twist': self.segment_twist,
                  'segment_twist_interpolation': self.segment_twist_interp,
                  'curve_skin': crv_skin_data,
                  'curve_name': self._crv_name}

        ik_limb = splineIkLimb.SplineIk(**kwargs)
        ik_limb.create()

        # pass info
        self._jnts = ik_limb.jnts
        self._ctrls = ik_limb.ctrls
        self._iks = ik_limb.iks
        self._nodes_hide = ik_limb.nodes_hide
        self._curve = ik_limb.curve
        self._ramp_twist = ik_limb.ramp_twist

    def save_data(self):
        """
        save data to current rig's data folder, will automatically create folder if not exist
        """
        super(SplineIk, self).save_data()
        pass

    def _generate_curve_name(self):
        """
        get default curve name from kwargs, we need to use this for build and save data

        """
        self._crv_name = naming.Namer(type=naming.Type.curve, side=self.side,
                                      description=self.description + self._jnt_suffix, index=1).name

