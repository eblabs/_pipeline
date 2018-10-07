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
import lib.common.nodes as nodes
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

	def _registerDefaultKwargs(self):
		super(JointComponent, self)._registerDefaultKwargs()
		kwargs = {'blueprintJoints': {'value': [],
						 			  'type': list},
				  'jointsDescriptor': {'value': [],
						 			   'type': list},
				  'bind': {'value': False,
				  		   'type': bool},
				  'bindParent': {'value': '',
				  				 'type': basestring},
				  'xtran': {'value': False,
				  			'type': bool},
				  'xtranParent': {'value': '',
				  				  'type': basestring}
							}
		self._kwargs.update(kwargs)

	def _setVariables(self):
		super(JointComponent, self)._setVariables()
		self._rigComponentType = 'rigSys.core.jointComponent'
		self._joints = []
		self._binds = []
		self._xtrans = []

	def create(self):
		self._createComponent()
		self._buildBindJoints()
		self._buildXtrans()
		self._writeRigComponentInfo()

	def connect(self):
		super(JointComponent, self).connect()
		self._connectBindJoints()

	def _connectBindJoints(self):
		if self._binds:
			hierarchy.parent(self._binds[0], self._bindParent)

	def _connectXtrans(self):
		if self._xtrans:
			hierarchy.parent(self._xtrans[0], self._xtranParent)

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

		attributes.addAttrs(self._rigComponent, ['joints', 'jointsDescriptor'],
							attributeType = 'string')

		# connect attrs
		attributes.connectAttrs(['jointsVis'], 
								[ '{}.v'.format(self._jointsGrp)], 
								 driver = self._rigComponent, force=True)

	def _buildBindJoints(self):
		if self._bind and self._joints:
			self._binds = joints.createOnHierarchy(self._joints,
							[namingDict.dNameConvension['type']['joint'], self._suffix],
							[namingDict.dNameConvension['type']['bindJoint'], ''],
							scaleCompensate = True)			

			# tag bind joints with drive joint
			for jnts in zip(self._binds, self._joints):
				attributes.addAttrsaddAttrs(jnts[0], 'joint', attributeType = 'string', 
													defaultValue = jnts[1], lock = True)

			# set bind joints tag
			joints.tagJoints(self._binds)

	def _buildXtrans(self):
		if self._xtran and self._joints:
			self._xtrans = transforms.createOnHierarchy(self._blueprintJoints, 
							[namingDict.dNameConvension['type']['joint'], self._suffix],
							[namingDict.dNameConvension['type']['bindJoint'], ''],
							rotateOrder=False, 
							lockHide=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

			# tag xtrans
			for xtr in zip(self._xtrans, self._joints):
				attributes.addAttrsaddAttrs(xtr[0], 'joint', attributeType = 'string', 
													defaultValue = xtr[1], lock = True)

	def _writeRigComponentInfo(self):
		super(JointComponent, self)._writeRigComponentInfo()

		self._writeJointsInfo()
		self._writeXtransInfo()

	def _getJointsInfo(self):
		jointList = self._getStringAttrAsList('joints')
		if jointList:

			jointsDic = {'list': jointList,
						 'count': len(jointList)}

			self._addObjAttr('joints', jointsDic)

			self._jointsDescriptor = self._getStringAttrAsList('jointsDescriptor')

			for i, joint in enumerate(jointList):
				jointsInfoDic = {'name': joint,
								 'matrixPlug': '{}.joint{:03d}Matrix'.format(self._rigComponent, i)}

				self._addObjAttr('joints.joint{:03d}'.format(i), jointsInfoDic)

				if self._jointsDescriptor:
					self._addObjAttr('joints.{}'.format(self._jointsDescriptor[i]), jointsInfoDic)

		bindList = self._getStringAttrAsList('binds')
		if bindList:
			self._addAttributeFromDict({'binds': bindList})

	def _getXtransInfo(self):
		xtransList = self._getStringAttrAsList('xtrans')
		if xtransList:
			self._addAttributeFromDict({'xtrans': xtransList})

	def _writeJointsInfo(self):
		self._addListAsStringAttr('joints', self._joints)
		self._addListAsStringAttr('binds', self._binds)

		for i, jnt in enumerate(self._joints):
			NamingJnt = naming.Naming(jnt)
			NamingJnt.type = 'multMatrix'
			NamingJnt.part = '{}Output'.format(NamingJnt.part)
			multMatrixJnt = nodes.create(name = NamingJnt.name)
			attributes.connectAttrs(['{}.worldMatrix[0]'.format(jnt), '{}.outputInverseMatrix'.format(self._rigComponent)],
									['matrixIn[0]', 'matrixIn[1]'], driven = multMatrixJnt)
			
			cmds.addAttr(self._rigComponent, ln = 'joint{:03d}Matrix'.format(i), at = 'matrix')

			cmds.connectAttr('{}.matrixSum'.format(multMatrixJnt), '{}.joint{:03d}Matrix'.format(self._rigComponent, i))

		# discriptor
		self._addListAsStringAttr('jointsDescriptor', self._jointsDescriptor)

		self._getJointsInfo()

	def _writeXtransInfo(self):
		self._addListAsStringAttr('xtrans', self._xtrans)
		self._getXtransInfo()

	def _getRigComponentInfo(self):
		super(JointComponent, self)._getRigComponentInfo()
		
		NamingGrp = naming.Naming(self._rigComponent)
		NamingGrp.type = 'jointsGrp'
		self._addAttributeFromDict({'_jointsGrp': NamingGrp.name})

		self._getJointsInfo()
		self._getXtransInfo()