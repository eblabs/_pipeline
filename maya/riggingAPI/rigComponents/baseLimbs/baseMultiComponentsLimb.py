###########################################################
# base multi components limb
# this limb should contain serveral limbs as one components
###########################################################
## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import riggingAPI.joints as joints
import riggingAPI.controls as controls
import common.importer as importer

import riggingAPI.rigComponents.baseLimbs.baseJointsLimb as baseJointsLimb
import riggingAPI.rigComponents.rigUtils.componentInfo as componentInfo
## kwarg class
class kwargsGenerator(baseJointsLimb.kwargsGenerator):
	"""docstring for kwargsGenerator"""
	def __init__(self):
		super(kwargsGenerator, self).__init__()
		self.dKwargs = {'lParts': None,
						'sModulePath': None,
						'sModuleName': None,
						'dKwargs': {}}
		self.addKwargs()

class baseMultiComponentsLimb(baseJointsLimb.baseJointsLimb):
	"""docstring for baseMultiComponentsLimb"""
	def __init__(self, *args, **kwargs):
		super(baseMultiComponentsLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lParts = kwargs.get('lParts', None)
			self._sModulePath = kwargs.get('sModulePath', None)
			self._sModuleName = kwargs.get('sModuleName', None)
			self._dKwargs = kwargs.get('dKwargs', {})

	def createComponent(self):
		super(baseMultiComponentsLimb, self).createComponent()
		
		sComponentMasterNodes = ''
		self._lBindRootJnts = []
		sNameString = ''
		for i, lBpJnts_each in enumerate(self._lBpJnts):
			dKwargs = self._dKwargs
			if self._lParts:
				sName = self._lParts[i]
			else:
				sName = '%s%02d'%(self._sName, i + 1)
			sNameString += '%s,' %sName
			dKwargs.update({'bInfo': True, 'lBpJnts': lBpJnts_each, 'sParent': self._sComponentRigNodesWorld, 'sName': sName, 'sSide': self._sSide, 'iIndex': self._iIndex, 'bBind': self._bBind})
			oModule = importer.importModule(self._sModulePath)
			oLimb = getattr(oModule, self._sModuleName)(**dKwargs)
			oLimb.createComponent()

			if self._bBind:
				self._lBindRootJnts += oLimb.lBindRootJoints
			sComponentMasterNodes += '%s,' %oLimb._sComponentMaster

			## reparent nodes
			sGrp = [self._sComponentControls, self._sComponentJoints, self._sComponentRigNodesLocal, self._sComponentRigNodesWorld, self._sComponentSubComponents]
			for j, sGrp_limb in enumerate([oLimb._sComponentControls, oLimb._sComponentJoints, oLimb._sComponentRigNodesLocal, oLimb._sComponentRigNodesWorld, oLimb._sComponentSubComponents]):
				lNodes = cmds.listRelatives(sGrp_limb, c = True)
				if lNodes:
					cmds.parent(lNodes, sGrp[j])

			## delete unused nodes
			lNodes_delete = cmds.listRelatives(oLimb._sComponentMaster, c = True)
			cmds.delete(lNodes_delete)

			## connect matrix
			cmds.connectAttr('%s.inputMatrix' %self._sComponentMaster, '%s.inputMatrix' %oLimb._sComponentMaster)
			cmds.connectAttr('%s.lWorldMatrix' %self._sComponentMaster, '%s.lWorldMatrix' %oLimb._sComponentMaster)
			## overwrite component info
			for sAttr in ['sComponentSpace', 'sComponentPasser']:
				cmds.setAttr('%s.%s' %(oLimb._sComponentMaster, sAttr), lock = False, type = 'string')
				cmds.setAttr('%s.%s' %(oLimb._sComponentMaster, sAttr), '', lock = True, type = 'string')

		## write component info
		self._writeGeneralComponentInfo('baseMultiComponentsLimb', [], None, None, self._lBindRootJnts)
		cmds.addAttr(self._sComponentMaster, ln = 'sModulePath', dt = 'string')
		cmds.setAttr('%s.sModulePath' %self._sComponentMaster, self._sModulePath, type = 'string', lock = True)
		cmds.addAttr(self._sComponentMaster, ln = 'sModuleName', dt = 'string')
		cmds.setAttr('%s.sModuleName' %self._sComponentMaster, self._sModuleName, type = 'string', lock = True)
		cmds.addAttr(self._sComponentMaster, ln = 'sComponentNodes', dt = 'string')
		cmds.setAttr('%s.sComponentNodes' %self._sComponentMaster, sComponentMasterNodes[:-1], type = 'string', lock = True)
		cmds.addAttr(self._sComponentMaster, ln = 'sComponentParts', dt = 'string')
		cmds.setAttr('%s.sComponentParts' %self._sComponentMaster, sNameString[:-1], type = 'string', lock = True)

		self._getComponentInfo(self._sComponentMaster)

	def _getComponentInfo(self, sComponent):
		super(baseMultiComponentsLimb, self)._getComponentInfo(sComponent)

		sModulePath = self._getComponentAttr(sComponent, 'sModulePath')
		sModuleName = self._getComponentAttr(sComponent, 'sModuleName')
		sComponentNodes = self._getComponentAttr(sComponent, 'sComponentNodes')
		lComponentNodes = sComponentNodes.split(',')
		sComponentParts = self._getComponentAttr(sComponent, 'sComponentParts')
		lComponentParts = sComponentParts.split(',')

		dAttrs = {'limbs': lComponentParts}
		for i, sComponentNode in enumerate(lComponentNodes):
			oModule = importer.importModule(sModulePath)
			oLimb = getattr(oModule, sModuleName)(sComponentNode)
			dAttrs.update({lComponentParts[i]: oLimb})

		self._addObjAttr('componentLimbs', dAttrs)



		
