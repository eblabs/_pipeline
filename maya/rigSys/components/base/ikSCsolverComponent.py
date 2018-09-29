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
import behaviors.ikSCsolverBehavior as ikSCsolverBehavior
# -- import end ----

class IkSCsolverComponent(ikSolverComponent.IkSolverComponent):
	"""
	IkSCsolverComponent

	create base ik sc solver rig component

	"""
	def __init__(self, *args,**kwargs):
		super(IkSCsolverComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.components.base.ikSCsolverComponent'

	def _createComponent(self):
		super(IkSCsolverComponent, self)._createComponent()

		kwargs = {'side': self._side,
				  'part': self._part,
				  'index': self._index,
				  'blueprintJoints': self._blueprintJoints,
				  'stacks': self._stacks,

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
		self._ikHandles = [IkSCsolverBehavior._ikHandle]
		self._ikControls = IkSCsolverBehavior._controls
		self._nodesLocal = IkSCsolverBehavior._nodesLocal