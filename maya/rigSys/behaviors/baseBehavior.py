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
import lib.common.naming.namingDict as namingDict
import lib.common.transforms as transforms
import lib.common.attributes as attributes
import lib.common.apiUtils as apiUtils
import lib.rigging.joints as joints

class BaseBehavior(object):
	"""BaseBehavior template"""
	def __init__(self, **kwargs):
		super(BaseBehavior, self).__init__()
		
		# kwargs
		self._side = kwargs.get('side', '')
		self._part = kwargs.get('part', '')
		self._index = kwargs.get('index', '')
		self._blueprintJoints = kwargs.get('blueprintJoints', [])
		self._stacks = kwargs.get('stacks', 3)
		self._jointSuffix = kwargs.get('jointSuffix', '')
		self._createJoints = kwargs.get('createJoints', True)

		self._controlsGrp = kwargs.get('controlsGrp', '')
		self._jointsGrp = kwargs.get('jointsGrp', '')
		self._nodesLocalGrp = kwargs.get('nodesLocalGrp', '')
		self._nodesHideGrp = kwargs.get('nodesHideGrp', '')
		self._nodesShowGrp = kwargs.get('nodesShowGrp', '')

		self._controls = []
		self._nodesLocal = []
		self._nodesHide = []
		self._nodesShow = []

	def create(self):
		# create joints
		if self._createJoints:
			self._joints = joints.createChainOnNodes(self._blueprintJoints, 
						namingDict.dNameConvension['type']['blueprintJoint'], 
						namingDict.dNameConvension['type']['joint'], 
						suffix = self._jointSuffix, 
						parent = self._jointsGrp, rotateOrder = False)
		else:
			self._joints = self._blueprintJoints

