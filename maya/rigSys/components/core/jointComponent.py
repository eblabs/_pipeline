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
		self._binds = []
		self._xtrans = []

	def connectDeformationNodes(self, parentNodes):
		if not isinstance(parentNodes, list):
			parentNodes = [parentNodes]
		if 'bindJoint' in self._deformationNodes:
			hierarchy.parent(self.binds.bind000.name, parentNodes[0])
		if 'xtran' in self._deformationNodes:
			hierarchy.parent(self.xtrans.bind000.name, parentNodes[-1])

	def _registerDefaultKwargs(self):
		super(JointComponent, self)._registerDefaultKwargs()
		kwargs = {'blueprintJoints': {'value': [],
						 			  'type': list},
				  'deformationNodes': {'value': [],
				  				       'type': list},
							}
		self._kwargs.update(kwargs)

	def _setVariables(self):
		super(JointComponent, self)._setVariables()
		self._rigComponentType = 'rigSys.components.core.jointComponent'
		
	def create(self):
		self._createComponent()
		self._buildDeformationNodes()
		self._writeRigComponentInfo()

	def _buildDeformationNodes(self):
		if self._deformationNodes:
			for i, node in enumerate(self._deformationNodes):
				nodeType = naming.getName(node, 'type', returnType='longName')
				self._deformationNodes[i] = nodeType
			if 'bindJoint' in self._deformationNodes:
				self._buildBindJoints()
			if 'xtran' in self._deformationNodes:
				self._buildXtrans()

	def _createComponent(self):
		super(JointComponent, self)._createComponent()

		# create groups
		NamingGrp = naming.Naming(type = 'jointsGrp', 
								  side = self._side,
								  part = self._part,
								  index = self._index)

		transformNode = transforms.createTransformNode(NamingGrp.name, 
													   lockHide = ['tx', 'ty', 'tz',
																  'rx', 'ry', 'rz',
																  'sx', 'sy', 'sz',
																  'v'])

		self._addAttributeFromDict({'_jointsGrp': transformNode})

		cmds.parent(self._jointsGrp, self._rigLocal)

		attributes.addAttrs(self._rigComponent, ['jointsVis'],
							attributeType = 'long', minValue = 0, maxValue = 1, 
							defaultValue = [0], keyable = False, channelBox = True)

		attributes.addAttrs(self._rigComponent, ['joints'],
							attributeType = 'string')

		# connect attrs
		attributes.connectAttrs(['jointsVis'], 
								[ '{}.v'.format(self._jointsGrp)], 
								 driver = self._rigComponent, force=True)

	def _buildBindJoints(self):
		if self._joints:
			jntType = naming.getName('joint', 'type', returnType = 'shortName')
			bindType = naming.getName('bindJoint', 'type', returnType = 'shortName')
			self._binds = joints.createOnHierarchy(self._joints,
							[jntType, self._suffix], [bindType, ''], scaleCompensate = True)			

			# tag bind joints with drive joint
			for jnts in zip(self._binds, self._joints):
				attributes.addAttrs(jnts[0], 'joint', attributeType = 'string', 
													defaultValue = jnts[1], lock = True)

			# set bind joints tag
			joints.tagJoints(self._binds)

	def _buildXtrans(self):
		if self._joints:
			jntType = naming.getName('joint', 'type', returnType = 'shortName')
			xtranType = naming.getName('xtran', 'type', returnType = 'shortName')
			
			self._xtrans = transforms.createOnHierarchy(self._blueprintJoints, 
							[jntType, self._suffix], [xtranType, ''], rotateOrder=False, 
							lockHide=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

			# tag xtrans
			for xtr in zip(self._xtrans, self._joints):
				attributes.addAttrs(xtr[0], 'joint', attributeType = 'string', 
													defaultValue = xtr[1], lock = True)

	def _writeRigComponentInfo(self):
		super(JointComponent, self)._writeRigComponentInfo()

		self._addListAsStringAttr('deformationNodes', self._deformationNodes)
		self._writeJointsInfo()
		self._getJointsInfo()

	def _getJointsInfo(self):
		jointList = self._getStringAttrAsList('joints')
		bindList = self._getStringAttrAsList('binds')
		xtransList = self._getStringAttrAsList('xtrans')

		for i, nodeList in enumerate([jointList, bindList, xtransList]):
			attr = ['joints', 'binds', 'xtrans'][i]
			if nodeList:
				nodesDict = {'list': nodeList,
							 'count': len(nodeList)}
				self._addObjAttr(attr, nodesDict)

				for j, node in enumerate(nodeList):
					nodesInfoDict = {'name': node}
					if attr == 'joints':
						nodesInfoDict.update({'localMatrixPlug': '{}.joint{:03d}MatrixLocal'.format(self._rigComponent, j),
											  'worldMatrixPlug': '{}.joint{:03d}MatrixWorld'.format(self._rigComponent, j)})
					self._addObjAttr('{}.{}{:03d}'.format(attr, attr[:-1], j), nodesInfoDict)

	def _writeJointsInfo(self):
		self._addListAsStringAttr('joints', self._joints)
		self._addListAsStringAttr('binds', self._binds)
		self._addListAsStringAttr('xtrans', self._xtrans)

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

		self._deformationNodes = self._getStringAttrAsList('deformationNodes')
		self._getJointsInfo()