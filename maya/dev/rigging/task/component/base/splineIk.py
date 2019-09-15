# IMPORT PACKAGES

# import utils
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
        self.up_vector = None
        self.auto_twist_range = None
        self.twist_start = None
        self.twist_end = None
        self.twist_interp = None
        self.crv_skin_path = None

        super(SplineIk, self).__init__(*args, **kwargs)

        self._task = 'dev.rigging.task.component.base.splineIk'
        self._jnt_suffix = 'SplineIk'
        self._iks = []
        self._curve = []

    def register_kwargs(self):
        super(SplineIk, self).register_kwargs()
        self.register_attribute('blueprint curve', '', attr_name='bp_crv', attr_type='str', select=True,
                                hint="blueprint curve for spline ik setup")
        self.register_attribute('blueprint controls', [], attr_name='bp_ctrls', attr_type='list', select=True,
                                hint="blueprint controls, order is from start to end")
        self.register_attribute('joints number', [], attr_name='jnts_num', attr_type='int', min=3, skippable=False,
                                hint="generate joints evenly along the curve if no blueprint is given")
        self.register_attribute('up vector', [0, 1, 0], attr_name='up_vector', attr_type='list', template=None,
                                hint="generate joints base on the given up vector")
        self.register_attribute('auto twist range', True, attr_name='auto_twist_range', attr_type='bool',
                                hint="auto set twist start and end base on controls position")
        self.register_attribute('twist start', 0, attr_name='twist_start', attr_type='float', min=0, max=1,
                                hint="twist start position on the curve, value from 0 to 1")
        self.register_attribute('twist end', 1, attr_name='twist_end', attr_type='float', min=0, max=1,
                                hint="twist end position on the curve, value from 0 to 1")
        self.register_attribute('twist interpolation', 'linear', attr_name='twist_interp', attr_type='enum',
                                enum=['linear', 'exponential up', 'exponential down', 'smooth', 'bump', 'spike'],
                                hint="twist ramp interpolation")
        self.register_attribute('curve weights', [{'project': '', 'asset': '', 'rig_type': ''}],
                                attr_name='crv_skin_path', attr_type='list', select=False, template=None,
                                hint="curve's skin cluster data to override the auto generate one")

    def create_component(self):
        super(SplineIk, self).create_component()

        # get skin data from crv_skin_path
        crv_skin_data = None
        if self.crv_skin_path:
            # get path
            self.crv_skin_path = buildUtils.get_data_path(self._name, self.rig_type, self.asset, self.project,
                                                          warning=False, check_exist=True)
            # get curve skin data
            pass

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

                  'blueprint_curve': self.bp_crv,
                  'blueprint_controls': self.bp_ctrls,
                  'joints_number': self.jnts_num,
                  'up_vector': self.up_vector,
                  'auto_twist_range': self.auto_twist_range,
                  'twist_start': self.twist_start,
                  'twist_end': self.twist_end,
                  'twist_interpolation': self.twist_interp,
                  'curve_skin': crv_skin_data}

        ik_limb = splineIkLimb.SplineIk(**kwargs)
        ik_limb.create()

        # pass info
        self._jnts = ik_limb.jnts
        self._ctrls = ik_limb.ctrls
        self._iks = ik_limb.iks
        self._nodes_hide = ik_limb.nodes_hide
        self._curve = ik_limb.curve
