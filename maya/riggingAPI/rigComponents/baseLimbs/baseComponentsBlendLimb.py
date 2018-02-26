#####################################################
# base components blend limb
# this limb should blend several rigs into one rig
#####################################################
## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import riggingAPI.joints as joints
import riggingAPI.controls as controls

import riggingAPI.rigComponents.baseComponent as baseComponent

class baseComponentsBlendLimb(baseComponent.baseComponent):
	"""docstring for baseComponentsBlendLimb"""
	def __init__(self, *args, **kwargs):
		super(baseComponentsBlendLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpJnts = kwargs.get('lBpJnts', None)
			self._bBind = kwargs.get('bBind', False)
			self._dComponents = kwargs.get('dComponents', {})

			## dComponents example
			#{Key name: 
			#  { 'sModulePath': module path,
			#	 'sModuleName': module name
			#	 'dKwargs': kwargs,}
			#}

	def createComponent(self):
		super(baseComponentsBlendLimb, self).createComponent()

		lComponentsObj = []

		for sKey in self._dComponents.keys():
			sModulePath = self._dComponents[sKey]['sModulePath']
			sModuleName = self._dComponents[sKey]['sModuleName']
			dKwargs = self._dComponents[sKey]['dKwargs']
			dKwargs.update({'bInfo': False, 'lBpJnts': self._lBpJnts, 'sParent': self._sComponentSubComponents, 'sName': '%s%s%s' %(self._sName, sKey[0].upper(), sKey[1:]), 'sSide': self._sSide, 'iIndex': self._iIndex})

			oModule = __import__(sModulePath)
			oLimb = getattr(oMdule, sModuleName)(**dKwargs)
			oLimb.createComponent()

			## connect attrs
			attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sDriver = self._sComponentPasser, sDriven = oLimb._sComponentPasser, bForce = True)
			attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sDriver = self._sComponentSpace, sDriven = oLimb._sComponentSpace, bForce = True)
			for sAttr in ['inputMatrix', 'inputMatrixOffset', 'deformGeo']:
				cmds.connectAttr('%s.%s' %(self._sComponentMaster, sAttr), '%s.%s' %(oLimb._sComponentMaster, sAttr))