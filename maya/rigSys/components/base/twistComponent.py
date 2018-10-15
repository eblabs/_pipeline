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
import rigSys.components.core.jointComponent as jointComponent
import rigSys.behaviors.twistBehavior as twistBehavior
# -- import end ----

class TwistComponent(jointComponent.JointComponent):
	"""
	twistComponent

	create base twist rig component

	"""
	def __init__(self, *args,**kwargs):
		super(TwistComponent, self).__init__(*args,**kwargs)
		
	def _registerDefaultKwargs(self):
		super(TwistComponent, self)._registerDefaultKwargs()
		kwargs = {'jointsNumber': {'value': 5,
						 	   	   'type': int}}
		self._kwargs.update(kwargs)

	def _setVariables(self):
		super(TwistComponent, self)._setVariables()
		self._rigComponentType = 'rigSys.components.base.twistComponent'
		self._suffix = 'Twist'

	def _createComponent(self):
		super(TwistComponent, self)._createComponent()

		kwargs = {'side': self._side,
				  'part': self._part,
				  'index': self._index,
				  'blueprintJoints': self._blueprintJoints,
				  'stacks': self._stacks,
				  'jointSuffix': self._suffix,
				  'jointsNumber': self._jointsNumber,
				  'controlSize': self._controlSize,

				  'controlsGrp': self._controlsGrp,
				  'jointsGrp': self._jointsGrp,
				  'nodesLocalGrp': self._nodesLocalGrp,
				  'nodesHideGrp': self._nodesHideGrp,
				  'nodesShowGrp': self._nodesShowGrp}

		TwistBehavior = twistBehavior.TwistBehavior(**kwargs)
		TwistBehavior.create()

		# pass info
		self._joints += TwistBehavior._joints
		self._controls += TwistBehavior._controls