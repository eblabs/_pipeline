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
import behaviors.ikRPsolverBehavior as ikRPsolverBehavior
# -- import end ----

class IkRPsolverComponent(ikSolverComponent.IkSolverComponent):
	"""
	IkRPsolverComponent

	create base ik rp solver rig component

	"""
	def __init__(self, *args,**kwargs):
		super(IkRPsolverComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.components.base.ikRPsolverComponent'

	def _registerDefaultKwargs(self):
		super(IkRPsolverComponent, self)._registerDefaultKwargs()
		kwargs = {'blueprintControls': {'value': [],
						 				'type': list},
				  'ikSolver': {'value': 'ikRPsolver',
						 	   'type': basestring}}
		self._kwargs.update(kwargs)

	def _createComponent(self):
		super(IkRPsolverComponent, self)._createComponent()

		kwargs = {'side': self._side,
				  'part': self._part,
				  'index': self._index,
				  'blueprintJoints': self._blueprintJoints,
				  'stacks': self._stacks,
				  'blueprintControls': self._blueprintControls,
				  'ikSolver': self._ikSolver,

				  'controlsGrp': self._controlsGrp,
				  'jointsGrp': self._jointsGrp,
				  'nodesLocalGrp': self._nodesLocalGrp,
				  'nodesHideGrp': self._nodesHideGrp,
				  'nodesShowGrp': self._nodesShowGrp}

		IkRPsolverBehavior = ikRPsolverBehavior.IkRPsolverBehavior(**kwargs)
		IkRPsolverBehavior.create()

		# pass info
		self._joints += IkRPsolverBehavior._joints
		self._controls += IkRPsolverBehavior._controls
		self._ikHandles = IkRPsolverBehavior._ikHandles
		self._ikControls = IkRPsolverBehavior._controls
		self._nodesLocal = IkRPsolverBehavior._nodesLocal

	def _writeRigComponentInfo(self):
		super(IkRPsolverComponent, self)._writeRigComponentInfo()

		# ikHandle type
		self._addStringAttr('ikSolver', self._ikSolver)

	def _getRigComponentInfo(self):
		super(IkRPsolverComponent, self)._getRigComponentInfo()

		# get reverse controls
		self._ikSolver = self._getStringAttr('ikSolver')




