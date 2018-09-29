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
import common.apiUtils as apiUtils
import rigging.joints as joints
import rigging.controls.controls as controls
# ---- import end ----

# -- import component
import core.componentsPackage as componentsPackage
# ---- import end ----

class MultiComponentsPackage(componentsPackage.ComponentsPackage):
	"""multiComponentsPackage template"""
	def __init__(self, *args,**kwargs):
		super(MultiComponentsPackage, self).__init__()
		self._rigComponentType = 'rigSys.components.package.multiComponentsPackage'

		self._removeAttributes(['blueprintJoints', 'jointsDescriptor'])

		kwargsDefault = {'components': {'value': {}, 'type': dict}}

		## components example
			#{Key name: 
			#  { 'componentType': module path,
			#	 'kwargs': kwargs,}
			#}
		self._registerAttributes(kwargsDefault)

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
						  'index': self._index})

			componentImport = __import__(componentType)
			Limb = getattr(componentImport, componentFunc)(**kwargs)
			Limb.create()

			controls.addCtrlShape(Limb.controls.list, asCtrl = packageCtrl)

			for attr in ['jointsVis', 'rigNodesVis', 'controlsVis']:
				cmds.connectAttr('{}.{}'.format(self._rigComponent, attr),
								 '{}.{}'.format(Limb._rigComponent, attr),)

			subComponentNodes.append(Limb._rigComponent)

		self._controls += [packageCtrl]
		self._subComponentNodes = subComponentNodes