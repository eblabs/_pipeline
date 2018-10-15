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
import rigSys.components.core.ikSolverComponent as ikSolverComponent
import rigSys.behaviors.ikSCsolverBehavior as ikSCsolverBehavior
# -- import end ----

class IkSCsolverComponent(ikSolverComponent.IkSolverComponent):
	"""
	IkSCsolverComponent

	create base ik sc solver rig component

	"""
	def __init__(self, *args,**kwargs):
		super(IkSCsolverComponent, self).__init__(*args,**kwargs)
		
	def _registerDefaultKwargs(self):
		super(IkSCsolverComponent, self)._registerDefaultKwargs()
		kwargs = {'ikSolver': {'value': 'ikSCsolver',
						 	   'type': basestring}}
		self._kwargs.update(kwargs)

	def _setVariables(self):
		super(IkSCsolverComponent, self)._setVariables()
		self._rigComponentType = 'rigSys.components.base.ikSCsolverComponent'
		if self._ikSolver == 'ikSCsolver':
			self._suffix = 'IkSC'
		elif self._ikSolver == 'aimConstraint':
			self._suffix = 'AimSC'

	def _createComponent(self):
		super(IkSCsolverComponent, self)._createComponent()

		kwargs = {'side': self._side,
				  'part': self._part,
				  'index': self._index,
				  'blueprintJoints': self._blueprintJoints,
				  'stacks': self._stacks,
				  'ikSolver': self._ikSolver,
				  'jointSuffix': self._suffix,
				  'controlSize': self._controlSize,

				  'controlsGrp': self._controlsGrp,
				  'jointsGrp': self._jointsGrp,
				  'nodesLocalGrp': self._nodesLocalGrp,
				  'nodesHideGrp': self._nodesHideGrp,
				  'nodesShowGrp': self._nodesShowGrp}

		IkSCsolverBehavior = ikSCsolverBehavior.IkSCsolverBehavior(**kwargs)
		IkSCsolverBehavior.create()

		# pass info
		self._joints += IkSCsolverBehavior._joints
		self._controls += IkSCsolverBehavior._controls
		self._ikHandles = IkSCsolverBehavior._ikHandles
		self._ikControls = IkSCsolverBehavior._controls
		self._nodesLocal = IkSCsolverBehavior._nodesLocal
		self._nodesHide = IkSCsolverBehavior._nodesHide
		self._jointsLocal = IkSCsolverBehavior._jointsLocal