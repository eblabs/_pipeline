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
# ---- import end ----

# -- import component
import jointComponent
# ---- import end ----

class ComponentsPackage(jointComponent.JointComponent):
	"""componentsPackage template"""
	_subComponentNodes = []
	def __init__(self, *args,**kwargs):
		super(ComponentsPackage, self).__init__()
		self._rigComponentType = 'rigSys.core.componentsPackage'

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
			for node in subComponentNodes:
				componentType = cmds.getAttr('{}.rigComponentType'.format(node))
				componentFunc = componentType.split('.')[-1]
				componentFunc = componentFunc[0].upper() + componentFunc[1:]
				componentImport = __import__(componentType)
				Limb = getattr(componentImport, componentFunc)(node)
				subComponentDic.update({node: Limb})
		self._addObjAttr('subComponentNodes', subComponentDic)