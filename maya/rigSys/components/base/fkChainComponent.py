# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import lib.common.naming.naming as naming
import lib.common.transforms as transforms
import lib.common.attributes as attributes
import lib.rigging.controls.controls as controls
import lib.rigging.constraints as constraints
# ---- import end ----

# -- import component
import rigSys.core.jointComponent as jointComponent
import rigSys.behaviors.fkChainBehavior as fkChainBehavior
# -- import end ----

class FkChainComponent(jointComponent.JointComponent):
	"""
	FkChainComponent

	create base fk chain rig component

	"""
	def __init__(self, *args,**kwargs):
		super(FkChainComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.components.base.fkChainComponent'

	def _registerDefaultKwargs(self):
		super(FkChainComponent, self)._registerDefaultKwargs()
		kwargs = {'lockHide': {'value': ['sx', 'sy', 'sz'],
						 	   'type': list}}
		self._kwargs.update(kwargs)

	def _createComponent(self):
		super(FkChainComponent, self)._createComponent()

		kwargs = {'side': self._side,
				  'part': self._part,
				  'index': self._index,
				  'blueprintJoints': self._blueprintJoints,
				  'stacks': self._stacks,
				  'lockHide': self._lockHide,

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