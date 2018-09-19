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

class RigComponent(object):
	"""rigComponent template"""
	def __init__(self, *args,**kwargs):
		super(RigComponent, self).__init__()
		self._rigComponentType = 'rigSys.core.rigComponent'
		if args:
			self._rigComponent = args[0]
			self._getRigComponentInfo()
		else:
			self._side = kwargs.get('side', 'middle')
			self._part = kwargs.get('part', None)
			self._index = kwargs.get('index', None)
			self._parent = kwargs.get('parent', None)

			self._bpJnts = kwargs.get('blueprintJoints', None) # blueprint joints
			self._bpCtrls = kwargs.get('blueprintControls', None)
			self._stacks = kwargs.get('stacks', 3) # control's stacks
			self._lockHide = kwargs.get('lockHide', ['sx', 'sy', 'sz', 'v']) # lock hide control's attrs
			self._ctrlDescriptor = kwargs.get('controlsDescriptor', [])
			self._jntDescriptor = kwargs.get('jointsDescriptor', [])

			self._joints = []
			self._controls = []

	def __str__(self):
		return self._rigComponentType

	@ property
	def rigComponent(self):
		return self._rigComponent

	@ property
	def rigComponentType(self):
		return self._rigComponentType
	
	@ property
	def inputMatrixPlug(self):
		return self._inputMatrixPlug

	@ property
	def offsetMatrixPlug(self):
		return self._offsetMatrixPlug

	@ staticmethod
	def composeListToString(valList):
		valString = ''
		for val in valList:
			valString += '{},'.format(val)
		if valString:
			valString = valString[:-1]
		return valString

	@ staticmethod
	def getListFromStringAttr(attr):
		attrString = cmds.getAttr(attr)
		attrList = attrString.split(',')
		return attrList

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
		
	def create(self):
		'''
		create rig component hierarchy

		rigComponent
		  -- controlsGrp
		  -- rigLocal	
			-- jointsGrp
			-- nodesLocal
		  -- rigWorld
		    -- nodesHide
		    -- nodesShow
		    -- subComponents
		'''

		# get name
		NamingGrp = naming.Naming(type = 'rigComponent', 
								  side = self._side,
								  part = self._part,
								  index = self._index)

		# get key name
		self._side = NamingGrp.side
		self._part = NamingGrp.part
		self._index = NamingGrp.index

		# create groups
		dicAttr = {}
		for grp in ['rigComponent', 'controlsGrp', 'rigLocal', 'jointsGrp', 'nodesLocal',
					'rigWorld', 'nodesHide', 'nodesShow', 'subComponents']:
			NamingGrp.type = grp
			transformNode = transforms.createTransformNode(NamingGrp.name, 
														   lockHide = ['tx', 'ty', 'tz',
																	  'rx', 'ry', 'rz',
																	  'sx', 'sy', 'sz',
																	  'v'])
			dicAttr.update({'_{}'.format(grp): transformNode})

		self._addAttributeFromDict(dicAttr)

		# parent components
		cmds.parent(self._rigComponent, self._parent)
		cmds.parent(self._controlsGrp, self._rigLocal, self._rigWorld, self._rigComponent)
		cmds.parent(self._jointsGrp, self._nodesLocal, self._rigLocal)
		cmds.parent(self._nodesHide, self._nodesShow, self._subComponents, self._rigWorld)

		# inheritsTransform
		attributes.setAttrs(['{}.inheritsTransform'.format(self._rigLocal),
							 '{}.inheritsTransform'.format(self._rigWorld)],
							 0, force = True)

		# hide nodesHide
		attributes.setAttrs('{}.v'.format(self._nodesHide), 0, force = True)

		# add attrs
		self._writeRigComponentType()

		# input matrix, offset matrix, component type, controls, joints, rigNodes
		attributes.addAttrs(self._rigComponent, ['inputMatrix', 'offsetMatrix', 'outputMatrix', 'outputInverseMatrix'], 
							attributeType = 'matrix', lock = True)
		
		attributes.addAttrs(self._rigComponent, ['controlsVis', 'jointsVis', 'rigNodesVis'],
							attributeType = 'long', minValue = 0, maxValue = 1, 
							defaultValue = [1,0,0], keyable = False, channelBox = True)

		attributes.addAttrs(self._rigComponent, ['controls', 'joints', 'controlsDescriptor', 'jointsDescriptor'],
							attributeType = 'string')

		for items in [[self._ctrlDescriptor, 'controlsDescriptor'], [self._jntDescriptor, 'jointsDescriptor']]:
			descriptorString = self.composeListToString(itmes[0])
			attributes.setAttrs('{}.{}'.format(self._rigComponent, items[1]), descriptorString, force = True)
		
		# connect attrs
		attributes.connectAttrs(['controlsVis', 'jointsVis', 'rigNodesVis', 'rigNodesVis'], 
								['{}.v'.format(self._controlsGrp), '{}.v'.format(self._jointsGrp),
								 '{}.v'.format(self._nodesLocal), '{}.v'.format(self._nodesHide)], 
								 driver = self._rigComponent, force=True)

		# connect matrix
		NamingGrp.type = 'multMatrix'
		multMatrixInput = cmds.createNode('multMatrix', name = NamingGrp.name)

		NamingGrp.type = 'inverseMatrix'
		inverseMatrixInput = cmds.createNode('inverseMatrix', name = NamingGrp.name)

		attributes.connectAttrs(['offsetMatrix', 'inputMatrix'], ['matrixIn[0]', 'matrixIn[1]'],
								driver = self._rigComponent, driven = multMatrixInput, force = True)

		attributes.connectAttrs('matrixSum', 'outputMatrix', 
								driver = multMatrixInput, driven = self._rigComponent, force = True)

		attributes.connectAttrs(['{}.matrixSum'.format(multMatrixInput), '{}.outputMatrix'.format(inverseMatrixInput)],
								['{}.inputMatrix'.format(inverseMatrixInput), '{}.outputInverseMatrix'.format(self._rigComponent)],
								force = True)

		constraints.matrixConnect('{}.outputMatrix'.format(self._rigComponent), [self._controlsGrp, self._rigLocal], force = True)

		attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'],
								['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'],
								driver = self._controlsGrp, driven = self._rigLocal, force = True)

		# get attrs
		self._inputMatrixPlug = '{}.inputMatrix'.format(self._rigComponent)
		self._offsetMatrixPlug = '{}.offsetMatrix'.format(self._rigComponent)

	def connect(self, inputPlug):
		inputMatrixList = cmds.getAttr(inputPlug)
		componentMatrixList = cmds.getAttr('{}.worldMatrix[0]'.format(self._rigComponent))

		MMatrixComponent = apiUtils.convertListToMMatrix(componentMatrixList)
		MMatrixInput = apiUtils.convertListToMMatrix(inputMatrixList)

		offsetMatrixList = apiUtils.convertMMatrixToList(MMatrixComponent * MMatrixInput.inverse())

		attributes.connectAttrs(inputPlug, self._inputMatrixPlug, force = True)
		attributes.setAttrs(self._offsetMatrixPlug, offsetMatrixList, type = 'matrix', force = True)

	def _getRigComponentInfo(self):
		# get groups
		NamingGrp = naming.Naming(self._rigComponent)

		self._side = NamingGrp.side
		self._part = NamingGrp.part
		self._index = NamingGrp.index

		dicAttr = {}
		for grp in ['controls', 'rigLocal', 'joints', 'nodesLocal',
					'rigWorld', 'nodesHide', 'nodesShow', 'subComponents']:
			NamingGrp.type = grp
			dicAttr.update('_{}'.format(grp), NamingGrp.name)

		self._addAttributeFromDict(dicAttr)

		self._rigComponentType = cmds.getAttr('{}.rigComponentType'.format(self._rigComponent))

		self._inputMatrixPlug = '{}.inputMatrix'.format(self._rigComponent)
		self._offsetMatrixPlug = '{}.offsetMatrix'.format(self._rigComponent)

		self._getControlsInfo()
		self._getJointsInfo()

	def _getControlsInfo(self):
		controlsName = cmds.getAttr('{}.controls'.format(self._rigComponent))
		if controlsName:
			controlList = controlsName.split(',')
			controlObjList = []
			controlDic = {'list': controlList,
						  'count': len(controlList)}

			self._ctrlDescriptor = self.getListFromStringAttr('{}.controlsDescriptor'.format(self._rigComponent))

			for i, control in enumerate(controlList):
				ControlObj = controls.Control(control)
				controlObjList.append(ControlObj)
				if self._ctrlDescriptor:
					controlDic.append(self._ctrlDescriptor[i]: ControlObj)
			self._addAttributeFromList('controls', controlObjList)
			self._addObjAttr('controls', controlDic)

	def _getJointsInfo(self):
		jointsName = cmds.getAttr('{}.joints'.format(self._rigComponent))
		if jointsName:
			jointList = jointsName.split(',')

			jointsDic = {'list': jointList,
						 'count': len(jointList)}

			self._jntDescriptor = self.getListFromStringAttr('{}.jointsDescriptor'.format(self._rigComponent))

			for i, joint in enumerate(jointList):
				jointsDicUpdate = {'joint{:03d}'.format(i) : {'name': jnt,
															  'matrixPlug': '{}.joint{:03d}Matrix'.format(self._rigComponent, i)}}
				jointsDic.update(jointsDicUpdate)

				if self._jntDescriptor:
					jointsDicUpdate = {self._jntDescriptor[i] : {'name': jnt,
															  'matrixPlug': '{}.joint{:03d}Matrix'.format(self._rigComponent, i)}}
					jointsDic.update(jointsDicUpdate)

			self._addObjAttr('joints', jointsDic)

	def _writeRigComponentType(self):
		if not cmds.attributeQuery('rigComponentType', node = self._rigComponent, ex = True):
			cmds.addAttr(self._rigComponent, ln = 'componentType', dt = 'string')
		attributes.setAttrs('componentType', self._rigComponentType, 
							node = self._rigComponent, type = 'string', force = True)

	def _writeJointsInfo(self):
		if self._joints:
			jointsName = self.composeListToString(self._joints)
			attributes.addAttrs(self._rigComponent, 'joints', attributeType = 'string', lock = True)
			attributes.setAttrs('joints', jointsName, node = self._rigComponent, type = 'string', force = True)

			for i, jnt in enumerate(self._joints):
				NamingJnt = naming.Naming(jnt)
				NamingJnt.type = 'multMatrix'
				multMatrixJnt = cmds.createNode('multMatrix', name = NamingJnt.name)
				attributes.connectAttrs(['{}.worldMatrix[0]'.format(jnt), '{}.outputInverseMatrix'.format(self._rigComponent)],
										['matrixIn[0]', 'matrix[1]'], driven = multMatrixJnt)
				
				cmds.addAttr(self._rigComponent, ln = 'joint{:03d}Matrix'.format(i), at = 'matrix')

				cmds.connectAttr('{}.matrixSum'.format(multMatrixJnt), '{}.joint{:03d}Matrix'.format(self._rigComponent, i))

		self._getJointsInfo()

	def _writeControlsInfo(self):
		if self._controls:
			controlsName = self.composeListToString(self._controls)
			attributes.addAttrs(self._rigComponent, 'controls', attributeType = 'string', lock = True)
			attributes.setAttrs('controls', controlsName, node = self._rigComponent, type = 'string', force = True)

			self._getControlsInfo()
			
	def _addAttributeFromList(self, attr, valList):
		if valList:
			attrDic = self._generateAttrDict(attr, valList)
			self._addAttributeFromDict(attrDic)

	def _addAttributeFromDict(self, dic):
		for key, value in dic.items():
			setattr(self, key, value)

	def _generateAttrDict(self, attr, valList):
		attrDic = {}
		for i, val in enumerate(valList):
			attrDic.update({'%s%03d' %(attr, i): val})
		return attrDic

	def _addObjAttr(self, attr, attrDic):
		attrSplit = attr.split('.')
		attrParent = self
		if len(attrSplit) > 1:
			for a in attrSplit[:-1]:
				attrParent = getattr(attrParent, a)
		setattr(attrParent, attrSplit[-1], objectview(attrDic))

class Objectview(object):
    def __init__(self, kwargs):
        self.__dict__ = kwargs

