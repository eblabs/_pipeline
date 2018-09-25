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
import rigging.control.controls as controls
import rigging.constraints as constraints
# ---- import end ----

# -- import component
import rigSys.core.jointComponent as jointComponent
import rigSys.behavior.fkChainBehavior as fkChainBehavior
# -- import end ----

class FkChainComponent(jointComponent.JointComponent):
	"""
	FkChainComponent

	create base fk chain rig component

	"""
	def __init__(self, *args,**kwargs):
		super(FkChainComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.components.base.fkChainComponent'

		kwargsDefault = {'lockHide': {'value': ['sx', 'sy', 'sz'],
						 			  'type': list},
							}

		self._registerAttributes(kwargsDefault)

	def _createComponent(self):
		super(FkChainComponent, self)._createComponent()

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

		FkChainBehavior = fkChainBehavior.FkChainBehavior(**kwargs)
		FkChainBehavior.create()

		# pass info
		self._joints += FkChainBehavior._joints
		self._controls += FkChainBehavior._controls