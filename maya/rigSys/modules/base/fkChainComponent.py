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
# -- import end ----

class FkChainComponent(jointComponent.JointComponent):
	"""
	FkChainComponent

	create base fk chain rig component

	"""
	def __init__(self, *args,**kwargs):
		super(FkChainComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.modules.base.fkChainComponent'

		kwargsDefault = {'lockHide': {'value': ['sx', 'sy', 'sz'],
						 			  'type': list},
							}

		self._registerAttributes(kwargsDefault)

	def _createComponent(self):
		super(FkChainComponent, self)._createComponent()

		# create joints
		fkJnts = self.createJntsFromBpJnts(self._blueprintJoints, type = 'jnt', suffix = 'Fk', parent = self._jointsGrp)
		
		# create control
		fkControls = []
		ctrlParent = self._controlsGrp
		for jnt in fkJnts:
			NamingCtrl = naming.Naming(jnt)
			ro = cmds.getAttr('{}.ro'.format(jnt))
			Control = controls.create(NamingCtrl.part, side = NamingCtrl.side, index = NamingCtrl.index, 
				stacks = self._stacks, parent = ctrlParent, posParent = jnt, rotateOrder = ro, 
				lockHide = self._lockHide)

			## connect ctrl to joint
			constraints.matrixConnect(Control.name, matrixLocalAttr, jnt, skipTranslate = ['x', 'y', 'z'], 
						  force = True, quatToEuler = False)
			constraints.matrixConnect(Control.name, matrixWorldAttr, jnt, skipRotate = ['x', 'y', 'z'], 
						  skipScale = ['x', 'y', 'z'], force = True)

			fkControls.append(Control.name)
			ctrlParent = Control.ouput

		# pass info
		self._joints += fkJnts
		self._controls += fkControls