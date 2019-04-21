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
import lib.common.nodeUtils as nodeUtils
import lib.common.hierarchy as hierarchy
import lib.rigging.joints as joints
# ---- import end ----

# -- import component
import rigComponent
# ---- import end ----

class JointComponent(rigComponent.RigComponent):
	"""jointComponent template"""
	def __init__(self, *args,**kwargs):
		super(JointComponent, self).__init__(*args,**kwargs)

		# default attrs
		self._joints = []
		self._skeleton = []
		self._skeletonRoot = []

	def connect(self, inputObj, **kwargs):
		super(JointComponent, self).connect(inputObj, **kwargs)
		skeletonParent = kwargs.get('skeletonParent', '')
		self._connectSkeleton(inputObj, skeletonParent = skeletonParent)

	def _connectSkeleton(self, inputObj):
		if self._asSkeleton and inputObj and hasattr(inputObj, 'skeleton'):
			hierarchy.parent(self._skeletonRoot, inputObj.skeleton)
		elif self._asSkeleton and skeletonParent:
			hierarchy.parent(self._skeletonRoot, skeletonParent)

	def _registerDefaultKwargs(self):
		super(JointComponent, self)._registerDefaultKwargs()
		kwargs = {'blueprintJoints': {'value': [],
						 			  'type': list},
				  'asSkeleton': {'value': False,
				  				       'type': bool},
							}
		self._kwargs.update(kwargs)

	def _setVariables(self):
		super(JointComponent, self)._setVariables()
		self._rigComponentType = 'rigSys.components.core.jointComponent'
		
	def create(self):
		self._createComponent()
		self._buildDeformationNodes()
		self._writeRigComponentInfo()

	def _buildSkeleton(self):
		if self._asSkeleton:
			jntType = naming.getName('joint', 'type', returnType = 'shortName')
			skltType = naming.getName('skeleton', 'type', returnType = 'shortName')
			self._skeleton = joints.createOnHierarchy(self._joints,
							[jntType, self._suffix], [skltType, ''], 
							parent = self._skeletonGrp, scaleCompensate = True)			

			# tag bind joints with drive joint
			for jnts in zip(self._skeleton, self._joints):
				for channel in ['translate', 'rotate'. 'scale']:
					for axis in 'XYZ':
						cmds.connectAttr('{}.{}{}'.format(jnts[1], channel, axis),
										 '{}.{}{}'.format(jnts[0], channel, axis))
				attributes.addAttrs(jnts[0], 'joint', attributeType = 'string', 
													defaultValue = jnts[1], lock = True)

			self._skeletonRoot = cmds.listRelatives(self._skeletonGrp, c = True)

	def _createComponent(self):
		super(JointComponent, self)._createComponent()

		# create groups
		NamingGrp = naming.Naming(type = 'jointsGrp', 
								  side = self._side,
								  part = self._part,
								  index = self._index)

		attrDict = {}
		for grp in ['jointsGrp', 'skeletonGrp']:
			NamingGrp.type = grp
			transformNode = transforms.createTransformNode(NamingGrp.name, 
														   lockHide = ['tx', 'ty', 'tz',
																	  'rx', 'ry', 'rz',
																	  'sx', 'sy', 'sz',
																	  'v'])
			attrDict.update({'_{}'.format(grp): transformNode})

		self._addAttributeFromDict(attrDict)

		cmds.parent(self._jointsGrp, self._skeletonGrp, self._rigLocal)

		attributes.addAttrs(self._rigComponent, ['jointsVis'],
							attributeType = 'long', minValue = 0, maxValue = 1, 
							defaultValue = [0], keyable = False, channelBox = True)

		attributes.addAttrs(self._rigComponent, ['joints'],
							attributeType = 'string')

		# connect attrs
		attributes.connectAttrs(['jointsVis'], 
								[ '{}.v'.format(self._jointsGrp)], 
								 driver = self._rigComponent, force=True)

	def _writeRigComponentInfo(self):
		super(JointComponent, self)._writeRigComponentInfo()

		self._writeJointsInfo()
		self._getJointsInfo()

	def _getJointsInfo(self):
		jointList = self._getStringAttrAsList('joints')
		skeletonList = self._getStringAttrAsList('skeleton')
		self._skeletonRoot = self._getStringAttrAsList('skeletonRoot')

		if skeletonList:
			self._asSkeleton = True
		else:
			self._asSkeleton = False

		if jointList:
			jntsDict = {'list': jointList,
						 'count': len(jointList)}
			self._addObjAttr('joints', jntsDict)

			for i, jnt in enumerate(jointList):
				jntsInfoDict = {'name': jnt,
								'localMatrixPlug': '{}.joint{:03d}MatrixLocal'.format(self._rigComponent, i),
								'worldMatrixPlug': '{}.joint{:03d}MatrixWorld'.format(self._rigComponent, i)}
				if self._asSkeleton:
					jntsInfoDict.update({'skeleton': skeletonList[i]})
				self._addObjAttr('joints.joint{:03d}'.format(i), jntsInfoDict)

	def _writeJointsInfo(self):
		self._addListAsStringAttr('joints', self._joints)
		self._addListAsStringAttr('skeleton', self._skeleton)
		self._addListAsStringAttr('skeletonRoot', self._skeletonRoot)

		for i, jnt in enumerate(self._joints):
			NamingJnt = naming.Naming(jnt)
			
			multMatrixLocal = nodeUtils.create(type = 'multMatrix', side = NamingJnt.side, 
								part = '{}MatrixLocalOutput'.format(NamingJnt.part), index = NamingJnt.index)
			multMatrixWorld = nodeUtils.create(type = 'multMatrix', side = NamingJnt.side, 
								part = '{}MatrixWorldOutput'.format(NamingJnt.part), index = NamingJnt.index)

			attributes.addAttrs(self._rigComponent, ['joint{:03d}MatrixLocal'.format(i),
													 'joint{:03d}MatrixWorld'.format(i)], 
								attributeType = 'matrix', lock = True)

			attributes.connectAttrs(['{}.worldMatrix[0]'.format(jnt), self._localizationMatrixPlug,
									 '{}.worldMatrix[0]'.format(jnt), self._localizationMatrixRvsPlug],
									['{}.matrixIn[0]'.format(multMatrixLocal), '{}.matrixIn[1]'.format(multMatrixLocal),
									 '{}.matrixIn[0]'.format(multMatrixWorld), '{}.matrixIn[1]'.format(multMatrixWorld)])
			attributes.connectAttrs(['{}.matrixSum'.format(multMatrixLocal), '{}.matrixSum'.format(multMatrixWorld)],
									['{}.joint{:03d}MatrixLocal'.format(self._rigComponent, i),
									 '{}.joint{:03d}MatrixWorld'.format(self._rigComponent, i)])

	def _getRigComponentInfo(self):
		super(JointComponent, self)._getRigComponentInfo()
		
		NamingGrp = naming.Naming(self._rigComponent)
		NamingGrp.type = 'jointsGrp'
		self._addAttributeFromDict({'_jointsGrp': NamingGrp.name})

		self._getJointsInfo()