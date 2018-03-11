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

import riggingAPI.rigComponents.baseLimb.baseJointsLimb as baseJointsLimb

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

	@property
	def lComponentLimbs(self):
		return self._lComponentLimbs

	def createComponent(self):
		super(baseMultiComponentsLimb, self).createComponent()
		
		iJointCount = 0
		sComponentMasterNodes = ''

		for i, lBpJnts_each in enumerate(self._lBpJnts):
			dKwargs = self._dKwargs
			if self._lParts:
				sName = self._lParts[i]
			else:
				sName = '%s%02d'%(self._sName, i + 1)
			dKwargs.update({'bInfo': True, 'lBpJnts': lBpJnts_each, 'sParent': self._sComponentRigNodesWorld, 'sName': sName, 'sSide': self._sSide, 'iIndex': self._iIndex, 'bBind': self._bBind})
			oModule = importer.importModule(self._sModulePath)
			oLimb = getattr(oModule, self._sModuleName)(**dKwargs)
			oLimb.createComponent()

			iJointCount += oLimb._iJointCount
			sComponentMasterNodes += '%s,' %oLimb._sComponentMaster

			## reparent nodes
			sGrp = [self._sComponentControls, self._sComponentDrvJoints, self._sComponentBindJoints, self._sComponentRigNodesLocal, self._sComponentRigNodesWorld, self._sComponentSubComponents]
			for j, sGrp_limb in enumerate([oLimb._sComponentControls, oLimb._sComponentDrvJoints, oLimb._sComponentBindJoints, oLimb._sComponentRigNodesLocal, oLimb._sComponentRigNodesWorld, oLimb._sComponentSubComponents]):
				lNodes = cmds.listRelatives(sGrp_limb, c = True)
				if lNodes:
					cmds.parent(lNodes, sGrp[j])

			## delete unused nodes
			lNodes_delete = cmds.listRelatives(oLimb._sComponentMaster, c = True)
			cmds.delete(lNodes_delete)

			## connect matrix
			for sAttr in ['inputMatrix', 'inputMatrixOffset']:
				cmds.connectAttr('%s.%s' %(self._sComponentMaster, sAttr), '%s.%s' %(oLimb._sComponentMaster, sAttr))

			## overwrite component info
			for sAttr in ['sComponentSpace', 'sComponentPasser']:
				cmds.setAttr('%s.%s' %(oLimb._sComponentMaster, sAttr), lock = False, type = 'string')
				cmds.setAttr('%s.%s' %(oLimb._sComponentMaster, sAttr), '', lock = True, type = 'string')

		## write component info
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, type = 'string', lock = False)
		cmds.setAttr('%s.iJointCount' %self._sComponentMaster, lock = False)
		
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, 'baseMultiComponentsLimb', type = 'string', lock = True)
		cmds.setAttr('%s.iJointCount' %self._sComponentMaster, iJointCount, lock = True)
		cmds.addAttr(self._sComponentMaster, ln = 'sModulePath', dt = 'string')
		cmds.setAttr('%s.sModulePath' %self._sComponentMaster, self._sModulePath, type = 'string', lock = True)
		cmds.addAttr(self._sComponentMaster, ln = 'sModuleName', dt = 'string')
		cmds.setAttr('%s.sModuleName' %self._sComponentMaster, self._sModuleName, type = 'string', lock = True)
		cmds.addAttr(self._sComponentMaster, ln = 'sComponentNodes', dt = 'string')
		cmds.setAttr('%s.sComponentNodes' %self._sComponentMaster, sComponentMasterNodes[:-1], type = 'string', lock = True)

		self._getComponentInfo(self._sComponentMaster)

	def _getComponentInfo(self, sComponent):
		super(baseMultiComponentsLimb, self)._getComponentInfo(sComponent)

		sModulePath = cmds.getAttr('%s.sModulePath' %sComponent)
		sModuleName = cmds.getAttr('%s.sModuleName' %sComponent)
		sComponentNodes = cmds.getAttr('%s.sComponentNodes' %sComponent)
		lComponentNodes = sComponentNodes.split(',')
		self._lComponentLimbs = []
		for sComponentNode in lComponentNodes:
			oModule = importer.importModule(sModulePath)
			oLimb = getattr(oModule, sModuleName)(sComponentNode)
			self._lComponentLimbs.append(oLimb)


		
