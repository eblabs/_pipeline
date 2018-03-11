#################################################
# arm fk module
# this module should do the base biped arm fk rig
#################################################
## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import riggingAPI.joints as joints
import riggingAPI.controls as controls
import riggingAPI.constraints as constraints

import riggingAPI.rigComponents.baseLimbs.baseFkChainLimb as baseFkChainLimb
import riggingAPI.rigComponents.rigUtils.componentInfo as componentInfo

class armFkModule(baseFkChainLimb.baseFkChainLimb):
	"""docstring for armFkModule"""
	def __init__(self, *args, **kwargs):
		super(armFkModule, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		
	def createComponent(self):
		super(armFkModule, self).createComponent()

		## remove end bind joint
		if self._bBind:
			sBindEnd = self._lBindJoints[-1]
			lBindJnts = self._lBindJoints[:-1]
			cmds.delete(sBindEnd)

			sBindString = componentInfo.composeListToString(lBindJnts)
			cmds.setAttr('%s.sBindJoints' %self._sComponentMaster, lock = False, type = 'string')
			cmds.setAttr('%s.sBindJoints' %self._sComponentMaster, sBindString, type = 'string', lock = True)


		## write component info
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, lock = False, type = 'string')
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, 'armFkModule', type = 'string', lock = True)

		self._getComponentInfo(self._sComponentMaster)
		
