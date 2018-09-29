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
import common.naming.namingDict as namingDict
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import rigging.joints as joints
import rigging.controls.controls as controls
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

	def create(self):
		super(FkChainBehavior, self).create()

		# create control
		self.controls = []
		ctrlParent = self._controlsGrp
		for jnt in self._joints:
			NamingCtrl = naming.Naming(jnt)
			Control = controls.create(NamingCtrl.part, side = NamingCtrl.side, index = NamingCtrl.index, 
				stacks = self._stacks, parent = ctrlParent, posParent = jnt, lockHide = self._lockHide)

			## connect ctrl to joint
			constraints.matrixConnect(Control.name, matrixLocalAttr, jnt, skipTranslate = ['x', 'y', 'z'], 
						  force = True, quatToEuler = False)
			constraints.matrixConnect(Control.name, matrixWorldAttr, jnt, skipRotate = ['x', 'y', 'z'], 
						  skipScale = ['x', 'y', 'z'], force = True)

			self._controls.append(Control.name)
			ctrlParent = Control.ouput