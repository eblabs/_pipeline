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
import common.nodes as nodes
import rigging.joints as joints
# ---- import end ----

# -- import component
import rigComponent
# ---- import end ----

class JointComponent(rigComponent.RigComponent):
	"""jointComponent template"""
	_joints = []
	def __init__(self, *args,**kwargs):
		super(JointComponent, self).__init__()
		self._rigComponentType = 'rigSys.core.jointComponent'

		kwargsDefault = {'blueprintJoints': {'value': [],
						 					 'type': list},
						 'jointsDescriptor': {'value': [],
						 					  'type': list},
							}

		self._registerAttributes(kwargsDefault)

	@ staticmethod
	def createJntsFromBpJnts(bpJnts, type='jnt', search='', replace='', suffix='', parent=None):
		jntList = []
		# create jnts
		for j in bpJnts:
			NamingJnt = naming.Naming(j)
			NamingJnt.type = type
			NamingJnt.part = NamingJnt.part.replace(search, replace) + suffix
			joints.createOnNode(j, j, NamingJnt.name)
			jntList.append(NamingJnt.name)

		# parent jnts
		for i, j in enumerate(bpJnts):
			jntParent = cmds.listRelatives(j, p = True)
			if jntParent:
				NamingJnt = naming.Nameing(jntParent)
				NamingJnt.type = type
				NamingJnt.part = NamingJnt.part.replace(search, replace) + suffix
				if NamingJnt.name in jntList:
					jntParent = NamingJnt.name
				else:
					jntParent = parent
			else:
				jntParent = parent
			if jntParent and cmds.objExists(jntParent):
				cmds.parent(jntList[i], jntParent)

		return jntList

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

	def _writeRigComponentInfo(self):
		super(JointComponent, self)._writeRigComponentInfo()

		self._writeJointsInfo()

	def _getJointsInfo(self):
		jointList = self._getStringAttrAsList('joints')
		if jointList:

			jointsDic = {'list': jointList,
						 'count': len(jointList)}

			self._jointsDescriptor = self._getStringAttrAsList('jointsDescriptor')

			for i, joint in enumerate(jointList):
				jointsDicUpdate = {'joint{:03d}'.format(i) : {'name': jnt,
															  'matrixPlug': '{}.joint{:03d}Matrix'.format(self._rigComponent, i)}}
				jointsDic.update(jointsDicUpdate)

				if self._jointsDescriptor:
					jointsDicUpdate = {self._jointsDescriptor[i] : {'name': jnt,
															  'matrixPlug': '{}.joint{:03d}Matrix'.format(self._rigComponent, i)}}
					jointsDic.update(jointsDicUpdate)

			self._addObjAttr('joints', jointsDic)

	def _writeJointsInfo(self):
		self._addListAsStringAttr('joints', self._joints)

		for i, jnt in enumerate(self._joints):
			NamingJnt = naming.Naming(jnt)
			NamingJnt.type = 'multMatrix'
			multMatrixJnt = nodes.create(name = NamingJnt.name)
			attributes.connectAttrs(['{}.worldMatrix[0]'.format(jnt), '{}.outputInverseMatrix'.format(self._rigComponent)],
									['matrixIn[0]', 'matrix[1]'], driven = multMatrixJnt)
			
			cmds.addAttr(self._rigComponent, ln = 'joint{:03d}Matrix'.format(i), at = 'matrix')

			cmds.connectAttr('{}.matrixSum'.format(multMatrixJnt), '{}.joint{:03d}Matrix'.format(self._rigComponent, i))

		self._getJointsInfo()

		# discriptor
		self._addListAsStringAttr(self._rigComponent, 'jointsDescriptor', self._jointsDescriptor)

	def _getRigComponentInfo(self):
		super(JointComponent, self)._getRigComponentInfo()
		
		NamingGrp = naming.Naming(self._rigComponent)
		NamingGrp.type = 'jointsGrp'
		self._addAttributeFromDict({'_jointsGrp': NamingGrp.name})

		self._getJointsInfo()