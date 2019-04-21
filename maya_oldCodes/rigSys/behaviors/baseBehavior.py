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

		self._controlSize = kwargs.get('controlSize', 1)

		self._local = False

		self._joints = []
		self._jointsLocal = []
		self._controls = []
		self._nodesLocal = []
		self._nodesHide = []
		self._nodesShow = []

	def create(self):
		# create joints
		if self._createJoints:
			bpJntType = naming.getName('blueprintJoint', 'type', returnType = 'shortName')
			jntType = naming.getName('joint', 'type', returnType = 'shortName') 

			self._joints = joints.createOnHierarchy(self._blueprintJoints,	
						bpJntType, jntType, suffix = self._jointSuffix, 
						parent = self._jointsGrp, rotateOrder = False)
		else:
			self._joints = self._blueprintJoints

		if self._local:
			self._jointsLocal = joints.createOnHierarchy(self._joints,	
								'', '', suffix = 'Local', 
								parent = self._nodesHideGrp, rotateOrder = False)
			for jnts in zip(self._joints, self._jointsLocal):
				for attr in ['translate', 'rotate', 'scale']:
					for axis in 'XYZ':
						cmds.connectAttr('{}.{}{}'.format(jnts[1], attr, axis),
										 '{}.{}{}'.format(jnts[0], attr, axis))

