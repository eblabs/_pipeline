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
import common.hierarchy as hierarchy
import common.nodes as nodes
import rigging.controls.controls as controls
import rigging.constraints as constraints
import rigging.joints as joints
# ---- import end ----

# -- import component
import components.base.ikSCsolverComponent as ikSCsolverComponent
# -- import end ----

class SingleChainNoFlipFkComponent(ikSCsolverComponent.IkSCsolverComponent):
	"""
	SingleChainNoFlipFkComponent

	create non flip single fk joint chain, mainly used for clacivle or piston joint

	"""
	
	def __init__(self, *args,**kwargs):
		super(SingleChainNoFlipFkComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.components.advance.singleChainNoFlipFkComponent'

	def _createComponent(self):
		super(SingleChainNoFlipFkComponent, self)._createComponent()

		NamingCtrl = naming.Naming(self._joints[0])
		ControlFk = controls.create(NamingCtrl.part + 'Fk', side = NamingCtrl.side, 
				index = NamingCtrl.index, stacks = self._stacks, parent = self._controlsGrp,
				posParent = self._joints[0], lockHide = ['sx', 'sy', 'sz'])

		# connect root and base control
		ControlRoot = controls.Control(self._controls[0])
		ControlTarget = controls.Control(self._controls[-1])
		constraints.matrixConnect(ControlFk.name, ControlFk.matrixWorldAttr, ControlRoot.zero, skipScale = ['x', 'y', 'z'])
		constraints.matrixConnect(ControlFk.name, ControlFk.matrixWorldAttr, ControlTarget.zero, 
									offset = ControlFk.output, skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'])

		cmds.addAttr(ControlFk.name, ln = 'twist', at = 'float', dv = 0, keyable = True)
		cmds.connectAttr('{}.twist'.format(ControlFk.name), '{}.rx'.format(ControlTarget.name))
		ControlTarget.lockHideAttrs(['rx', 'ro'])

		# extra control vis
		attributes.addAttrs(ControlFk.name, 'extraControlsVis', attributeType='long', minValue=0, maxValue=1, 
							defaultValue=0, keyable=False, channelBox=True)
		attributes.connectAttrs('extraControlsVis', ['{}.v'.format(ControlRoot.name), '{}.v'.format(ControlTarget.name)], 
								driver = ControlFk.name, force=True)

		self._controls.insert(0, ControlFk.name)




