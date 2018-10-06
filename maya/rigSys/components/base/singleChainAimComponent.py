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
import rigging.controls.controls as controls
import rigging.constraints as constraints
# ---- import end ----

# -- import component
import core.jointComponent as jointComponent
import behaviors.singleChainAimBehavior as singleChainAimBehavior
# -- import end ----

class SingleChainAimComponent(jointComponent.JointComponent):
	"""
	SingleChainAimComponent

	create single chain aim rig component

	"""
	def __init__(self, *args,**kwargs):
		super(SingleChainAimComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.components.base.singleChainAimComponent'

	def _registerDefaultKwargs(self):
		super(SingleChainAimComponent, self)._registerDefaultKwargs()
		kwargs = {'upVectorDistance': {'value': 1,
						 	   		   'type': int}}
		self._kwargs.update(kwargs)

	def _createComponent(self):
		super(SingleChainAimComponent, self)._createComponent()

		kwargs = {'side': self._side,
				  'part': self._part,
				  'index': self._index,
				  'blueprintJoints': self._blueprintJoints,
				  'stacks': self._stacks,
				  'upVectorDistance': self._upVectorDistance,

				  'controlsGrp': self._controlsGrp,
				  'jointsGrp': self._jointsGrp,
				  'nodesLocalGrp': self._nodesLocalGrp,
				  'nodesHideGrp': self._nodesHideGrp,
				  'nodesShowGrp': self._nodesShowGrp}

		SingleChainAimBehavior = singleChainAimBehavior.SingleChainAimBehavior(**kwargs)
		SingleChainAimBehavior.create()

		# pass info
		self._joints += SingleChainAimBehavior._joints
		self._controls += SingleChainAimBehavior._controls