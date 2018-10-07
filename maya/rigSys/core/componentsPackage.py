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
# ---- import end ----

# -- import component
import jointComponent
# ---- import end ----

class ComponentsPackage(jointComponent.JointComponent):
	"""componentsPackage template"""
	def __init__(self, *args,**kwargs):
		super(ComponentsPackage, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.core.componentsPackage'
		self._subComponentNodes = []

	def _setVariables(self):
		super(ComponentsPackage, self)._setVariables()
		self._rigComponentType = 'rigSys.core.componentsPackage'
		self._subComponentNodes = []

	def _writeRigComponentInfo(self):
		super(ComponentsPackage, self)._writeRigComponentInfo()

		# sub components node
		self._writeSubComponentNodesInfo()

	def _getRigComponentInfo(self):
		super(ComponentsPackage, self)._getRigComponentInfo()

		# sub components node
		self._getSubComponentNodesInfo()

	def _writeSubComponentNodesInfo(self):
		self._addListAsStringAttr('subComponentNodes', self._subComponentNodes)
		self._getSubComponentNodesInfo()

	def _getSubComponentNodesInfo(self):
		self._subComponentNodes = self._getStringAttrAsList('subComponentNodes')
		subComponentDic = {'list': self._subComponentNodes}
		if self._subComponentNodes:
			for node in self._subComponentNodes:
				componentType = cmds.getAttr('{}.rigComponentType'.format(node))
				componentFunc = componentType.split('.')[-1]
				componentFunc = componentFunc[0].upper() + componentFunc[1:]
				componentImport = packages.importModule(componentType)
				Limb = getattr(componentImport, componentFunc)(node)
				subComponentDic.update({node: Limb})
		self._addObjAttr('subComponentNodes', subComponentDic)