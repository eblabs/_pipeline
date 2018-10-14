# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import lib.rigging.controls.controls as controls
# ---- import end ----

# -- import component
import rigSys.core.ikSolverComponent as ikSolverComponent
import rigSys.behaviors.ikSplineSolverBehavior as ikSplineSolverBehavior
# -- import end ----

class IkSplineSolverComponent(ikSolverComponent.IkSolverComponent):
	"""
	IkSplineSolverComponent

	create base ik spline solver rig component

	"""
	def __init__(self, *args,**kwargs):
		super(IkSplineSolverComponent, self).__init__(*args,**kwargs)
		
	def _registerDefaultKwargs(self):
		super(IkSplineSolverComponent, self)._registerDefaultKwargs()
		kwargs = {'blueprintCurve': {'value': '', 'type': basestring},
				  'blueprintControls': {'value': [], 'type': list},
				  'topFk': {'value': False, 'type': bool},
				  'bottomFk': {'value': False, 'type': bool}}
		self._kwargs.update(kwargs)

	def _setVariables(self):
		super(IkSplineSolverComponent, self)._setVariables()
		self._suffix = 'IkSpline'
		self._rigComponentType = 'rigSys.components.base.ikSplineSolverComponent'

	def _createComponent(self):
		super(IkSplineSolverComponent, self)._createComponent()

		kwargs = {'side': self._side,
				  'part': self._part,
				  'index': self._index,
				  'blueprintJoints': self._blueprintJoints,
				  'stacks': self._stacks,
				  'blueprintCurve': self._blueprintCurve,
				  'blueprintControls': self._blueprintControls,
				  'topFk': self._topFk,
				  'bottomFk': self._bottomFk,
				  'jointSuffix': self._suffix,
				  'controlSize': self._controlSize,

				  'controlsGrp': self._controlsGrp,
				  'jointsGrp': self._jointsGrp,
				  'nodesLocalGrp': self._nodesLocalGrp,
				  'nodesHideGrp': self._nodesHideGrp,
				  'nodesShowGrp': self._nodesShowGrp}

		IkSplineSolverBehavior = ikSplineSolverBehavior.IkSplineSolverBehavior(**kwargs)
		IkSplineSolverBehavior.create()

		# pass info
		self._joints += IkSplineSolverBehavior._joints
		self._controls += IkSplineSolverBehavior._controls
		self._ikHandles = IkSplineSolverBehavior._ikHandles
		self._ikControls = IkSplineSolverBehavior._ikControls
		self._ikTweakControls = IkSplineSolverBehavior._ikTweakControls
		self._fkRotControls = IkSplineSolverBehavior._fkRotControls
		self._curve = IkSplineSolverBehavior._curve
		self._nodesHide = IkSplineSolverBehavior._nodesHide
		self._jointsLocal = IkSplineSolverBehavior._jointsLocal

	def _writeRigComponentInfo(self):
		super(IkSplineSolverComponent, self)._writeRigComponentInfo()

		# ik controls
		self._addListAsStringAttr('ikTweakControls', self._ikTweakControls)

		# fk controls
		self._addListAsStringAttr('fkRotControls', self._fkRotControls)

		# curve
		self._addStringAttr('ikCurve', self._curve)

	def _getRigComponentInfo(self):
		super(IkSplineSolverComponent, self)._getRigComponentInfo()

		# get ik controls
		self._ikTweakControls = self._getStringAttrAsList('ikTweakControls')

		# get fk rot controls
		self._fkRotControls = self._getStringAttrAsList('fkRotControls')

		# get curve
		self._curve = self._getStringAttr('ikCurve')