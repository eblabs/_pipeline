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
import lib.common.transforms as transforms
import lib.common.attributes as attributes
import lib.common.apiUtils as apiUtils
import lib.common.packages as packages
import lib.rigging.joints as joints
import lib.rigging.controls.controls as controls
# ---- import end ----

# -- import component
import rigSys.core.componentsPackage as componentsPackage
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
			componentFunc = componentType.split('.')[-1]
			componentFunc = componentFunc[0].upper() + componentFunc[1:]
			kwargs = self._components[key]['kwargs']
			kwargs.update({'parent': self._subComponents,
						  'part': key[0].upper() + key[1:],
						  'side': self._side,
						  'index': self._index,
						  'bind': self._bind,
						  'bindParent': self._bindParent,
						  'xtran': self._xtran,
						  'xtranParent': self._xtranParent})

			componentImport = packages.importModule(componentType)
			Limb = getattr(componentImport, componentFunc)(**kwargs)
			Limb.create()

			controls.addCtrlShape(Limb.controls.list, asCtrl = packageCtrl)

			for attr in ['jointsVis', 'rigNodesVis', 'controlsVis']:
				cmds.connectAttr('{}.{}'.format(self._rigComponent, attr),
								 '{}.{}'.format(Limb._rigComponent, attr),)

			subComponentNodes.append(Limb._rigComponent)

		self._controls += [packageCtrl]
		self._subComponentNodes = subComponentNodes