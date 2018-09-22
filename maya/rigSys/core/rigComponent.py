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
	_kwargs = {}
	_controls = []
	def __init__(self, *args,**kwargs):
		super(RigComponent, self).__init__()
		self._rigComponentType = 'rigSys.core.rigComponent'

		kwargsDefault = {'side': {'value': 'middle', 
								  'type' : 'basestring'},
						 'part': {'value': '',
						 		  'type': 'basestring'},
						 'index': {'value': None,
						 		   'type': 'int'},
						 'parent': {'value': '',
						 			'type': 'basestring'},
						 'stacks': {'value': 3,
						 			'type': 'int'},
						 'controlsDescriptor': {'value': [],
						 						'type': 'list'},
							}

		self._registerInput(kwargs)
		self._registerAttributes(kwargsDefault)

		if args:
			self._rigComponent = args[0]
			self._getRigComponentInfo()

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

	def create(self):
		self._createComponent()
		self._writeRigComponentInfo()

	def connect(self, inputPlug):
		inputMatrixList = cmds.getAttr(inputPlug)
		componentMatrixList = cmds.getAttr('{}.worldMatrix[0]'.format(self._rigComponent))

		MMatrixComponent = apiUtils.convertListToMMatrix(componentMatrixList)
		MMatrixInput = apiUtils.convertListToMMatrix(inputMatrixList)

		offsetMatrixList = apiUtils.convertMMatrixToList(MMatrixComponent * MMatrixInput.inverse())

		attributes.connectAttrs(inputPlug, self._inputMatrixPlug, force = True)
		attributes.setAttrs(self._offsetMatrixPlug, offsetMatrixList, type = 'matrix', force = True)

	def _createComponent(self):
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

		# input matrix, offset matrix, component type, controls, joints, rigNodes
		attributes.addAttrs(self._rigComponent, ['inputMatrix', 'offsetMatrix', 'outputMatrix', 'outputInverseMatrix'], 
							attributeType = 'matrix', lock = True)
		
		attributes.addAttrs(self._rigComponent, ['controlsVis', 'jointsVis', 'rigNodesVis'],
							attributeType = 'long', minValue = 0, maxValue = 1, 
							defaultValue = [1,0,0], keyable = False, channelBox = True)

		attributes.addAttrs(self._rigComponent, ['controls', 'joints', 'controlsDescriptor', 'jointsDescriptor'],
							attributeType = 'string')

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

	def _writeRigComponentInfo(self):
		# rig component type
		self._writeRigComponentType()

		# controls
		self._writeControlsInfo()

	def _registerInput(self, kwargs):
		for key, val in kwargs.iteritems():
            self._kwargs.update({key: {'value': val}})
            self._addObjAttr('_' + key, val)

	def _registerAttributes(self, kwargs):
		for key, valDic in kwargs.iteritems():
			self._kwargs[key]['type'] = valDic['type']
            if key not in self._kwargs:
                self._kwargs[key]['value'] = valDic['value']
                self._addObjAttr('_' + key, valDic['value'])

    def _removeAttributes(self, kwargs):
    	for key in kwargs:
    		self._kwargs.pop(key, None)
            	
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

	def _getControlsInfo(self):
		controlsName = cmds.getAttr('{}.controls'.format(self._rigComponent))
		if controlsName:
			controlList = controlsName.split(',')
			controlObjList = []
			controlDic = {'list': controlList,
						  'count': len(controlList)}

			self._controlsDescriptor = self.getListFromStringAttr('{}.controlsDescriptor'.format(self._rigComponent))

			for i, control in enumerate(controlList):
				ControlObj = controls.Control(control)
				controlObjList.append(ControlObj)
				if self._controlsDescriptor:
					controlDic.append(self._controlsDescriptor[i]: ControlObj)
			self._addAttributeFromList('controls', controlObjList)
			self._addObjAttr('controls', controlDic)

	def _writeRigComponentType(self):
		if not cmds.attributeQuery('rigComponentType', node = self._rigComponent, ex = True):
			cmds.addAttr(self._rigComponent, ln = 'componentType', dt = 'string')
		attributes.setAttrs('componentType', self._rigComponentType, 
							node = self._rigComponent, type = 'string', force = True)

	def _writeControlsInfo(self):
		# controls
		self._addListAsStringAttr('controls', self._controls)
		self._getControlsInfo()

		# discriptor
		self._addListAsStringAttr(self._rigComponent, 'controlsDescriptor', self._controlsDescriptor)

			
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

	def _addListAsStringAttr(self, attr, listAttr):
		listName = self.composeListToString(listAttr)
		if not cmds.attributeQuery(attr, node = self._rigComponent, ex = True):
			attributes.addAttrs(self._rigComponent, attr, attributeType = 'string', lock = True)
		attributes.setAttrs(attr, listName, node = self._rigComponent, type = 'string', force = True)

class Objectview(object):
    def __init__(self, kwargs):
        self.__dict__ = kwargs

