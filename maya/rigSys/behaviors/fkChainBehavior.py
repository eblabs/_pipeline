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
import lib.rigging.joints as joints
import lib.rigging.controls.controls as controls
import lib.rigging.constraints as constraints
# ---- import end ----

# -- import component
import baseBehavior
# ---- import end ----

class FkChainBehavior(baseBehavior.BaseBehavior):
	"""FkChainBehavior template"""
	def __init__(self, **kwargs):
		super(FkChainBehavior, self).__init__(**kwargs)
		self._lockHide = kwargs.get('lockHide', ['sx', 'sy', 'sz'])
		self._jointSuffix = kwargs.get('jointSuffix', 'Fk')
		self._controlShape = kwargs.get('controlShape', 'circle')

	def create(self):
		super(FkChainBehavior, self).create()

		# create control
		self.controls = []
		ctrlParent = self._controlsGrp
		for jnt in self._joints:
			NamingCtrl = naming.Naming(jnt)
			Control = controls.create(NamingCtrl.part, side = NamingCtrl.side, index = NamingCtrl.index, 
				stacks = self._stacks, parent = ctrlParent, posParent = jnt, lockHide = self._lockHide,
				shape = self._controlShape)

			## connect ctrl to joint
			constraints.matrixConnect(Control.name, Control.matrixLocalAttr, jnt, skipTranslate = ['x', 'y', 'z'], 
						  force = True, quatToEuler = False)
			constraints.matrixConnect(Control.name, Control.matrixWorldAttr, jnt, skipRotate = ['x', 'y', 'z'], 
						  skipScale = ['x', 'y', 'z'], force = True)

			self._controls.append(Control.name)
			ctrlParent = Control.output