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
                                hint="blueprint curve for spline ik setup")
        self.register_attribute('blueprint controls', [], attr_name='bp_ctrls', attr_type='list', select=True,
                                hint="blueprint controls, order is from start to end")
        self.register_attribute('joints number', [], attr_name='jnts_num', attr_type='int', min=3, skippable=False,
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

    def mirror_kwargs(self):
        super(SplineIk, self).mirror_kwargs()
        self._name_no_flip = naming.mirror_name(self._name, keep_orig=True)  # flip name back to the original
        self.bp_crv = naming.mirror_name(self.bp_crv, keep_orig=True)
        self.bp_ctrls = naming.mirror_name(self.bp_ctrls, keep_orig=True)
        self._crv_name = naming.mirror_name(self._crv_name, keep_orig=True)

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
        save_data_path = buildUtils.get_data_path(self._name, self.rig_type, self.asset, self.project,
                                                  warning=False, check_exist=False)
        # create folder if not exist
        if not os.path.exists(save_data_path):
            os.mkdir(save_data_path)

        # save data
        # save data function

    def _generate_curve_name(self):
        """
        get default curve name from kwargs, we need to use this for build and save data

        """
        self._crv_name = naming.Namer(type=naming.Type.curve, side=self.side,
                                      description=self.description + self._jnt_suffix, index=1).name

