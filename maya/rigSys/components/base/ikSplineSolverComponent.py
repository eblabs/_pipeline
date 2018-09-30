# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import common.naming.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import rigging.controls.controls as controls
import rigging.constraints as constraints
# ---- import end ----

# -- import component
import core.ikSolverComponent as ikSolverComponent
import behaviors.ikSplineSolverBehavior as ikSplineSolverBehavior
# -- import end ----

class IkSplineSolverComponent(ikSolverComponent.IkSolverComponent):
	"""
	IkSplineSolverComponent

	create base ik spline solver rig component

	"""
	def __init__(self, *args,**kwargs):
		super(IkSplineSolverComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.components.base.ikSplineSolverComponent'

	def _registerDefaultKwargs(self):
		super(IkSplineSolverComponent, self)._registerDefaultKwargs()
		kwargs = {'blueprintCurve': {'value': '', 'type': basestring},
				  'blueprintControls': {'value': [], 'type': list}}
		self._kwargs.update(kwargs)

	def _createComponent(self):
		super(IkSplineSolverComponent, self)._createComponent()

		kwargs = {'side': self._side,
				  'part': self._part,
				  'index': self._index,
				  'blueprintJoints': self._blueprintJoints,
				  'stacks': self._stacks,
				  'blueprintCurve': self._blueprintCurve,
				  'blueprintControls': self._blueprintControls,

				  'controlsGrp': self._controlsGrp,
				  'jointsGrp': self._jointsGrp,
				  'nodesLocalGrp': self._nodesLocalGrp,
				  'nodesHideGrp': self._nodesHideGrp,
				  'nodesShowGrp': self._nodesShowGrp}

		IkSplineSolverBehavior = ikSplineSolverBehavior.IkSplineSolverBehavior(**kwargs)

		# pass info
		self._joints += IkSplineSolverBehavior._joints
		self._controls += IkSplineSolverBehavior._controls
		self._ikHandles = [IkSplineSolverBehavior._ikHandle]
		self._ikControls = IkSplineSolverBehavior._ikControls
		self._ikTweakControls = IkSplineSolverBehavior._ikTweakControls
		self._curve = IkSplineSolverBehavior._curve

	def _writeRigComponentInfo(self):
		super(IkSplineSolverComponent, self)._writeRigComponentInfo()

		# ik controls
		self._addListAsStringAttr('ikTweakControls', self._ikTweakControls)

		# curve
		self._addStringAttr('ikCurve', self._curve)

	def _getRigComponentInfo(self):
		super(IkSplineSolverComponent, self)._getRigComponentInfo()

		# get ik controls
		self._ikTweakControls = self._getStringAttrAsList('ikTweakControls')

		# get curve
		self._curve = self._getStringAttr('ikCurve')