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
import lib.common.attributes as attributes
import lib.common.packages as packages
import lib.common.hierarchy as hierarchy
import lib.rigging.joints as joints
import lib.rigging.controls.controls as controls
# ---- import end ----

# -- import component
import rigSys.components.core.componentsPackage as componentsPackage
import rigSys.components.utils.componentUtils as componentUtils
# ---- import end ----

class MultiComponentsPackage(componentsPackage.ComponentsPackage):
	"""multiComponentsPackage template"""
	def __init__(self, *args,**kwargs):
		super(MultiComponentsPackage, self).__init__(*args,**kwargs)
		
	def _registerDefaultKwargs(self):
		super(MultiComponentsPackage, self)._registerDefaultKwargs()
		kwargs = {'components': {'value': {}, 'type': dict}}
		## components example
			#{Key name: 
			#  { 'componentType': module path,
			#	 'kwargs': kwargs,}
			#}
		self._kwargs.update(kwargs)
		self._kwargsRemove += ['blueprintJoints', 'jointsDescriptor']

	def _setVariables(self):
		super(MultiComponentsPackage, self)._setVariables()
		self._rigComponentType = 'rigSys.components.package.multiComponentsPackage'

	def _createComponent(self):
		super(MultiComponentsPackage, self)._createComponent()

		# set sub components visible
		cmds.setAttr('{}.subComponents'.format(self._rigComponent), 1)

		packageCtrl = naming.Naming(type = 'control', side = self._side, 
									part = self._part, index = self._index).name

		subComponentNodes = []
		for key in self._components.keys():
			componentType = self._components[key]['componentType']
			kwargs = self._components[key]['kwargs']
			kwargs.update({'parent': self._subComponents,
						  'part': key[0].upper() + key[1:],
						  'side': self._side,
						  'index': self._index,
						  'controlSize': self._controlSize,
						  'deformationNodes': self._deformationNodes})

			Limb = componentUtils.createComponent(componentType, kwargs)

			controls.addCtrlShape(Limb.controls.list, asCtrl = packageCtrl)

			attributes.connectAttrs(['jointsVis', 'rigNodesVis', 'controlsVis', 'localization', 
									 'inputMatrix', 'offsetMatrix'],
									['jointsVis', 'rigNodesVis', 'controlsVis', 'localization', 
									 'inputMatrix', 'offsetMatrix'],
									driver = self._rigComponent,
									driven = Limb._rigComponent)

			subComponentNodes.append(Limb._rigComponent)

		self._controls += [packageCtrl]
		self._subComponentNodes = subComponentNodes

	def connectDeformationNodes(self, parentNodes):
		if not isinstance(parentNodes, list):
			parentNodes = [parentNodes]
		if 'bindJoint' in self._deformationNodes or 'xtran' in self._deformationNodes:
			for Limb in self.subComponentNodes.Components:
				if 'bindJoint' in self._deformationNodes:
					hierarchy.parent(Limb.binds.bind000.name, parentNodes[0])
				if 'xtran' in self._deformationNodes:
					hierarchy.parent(Limb.xtrans.xtran000.name, parentNodes[-1])
			