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
import lib.common.nodeUtils as nodeUtils
import lib.rigging.joints as joints
import lib.rigging.constraints as constraints
import lib.rigging.controls.controls as controls
# ---- import end ----

class RigComponent(object):
	"""rigComponent template"""

	def __init__(self, *args,**kwargs):

		self._registerAttrs(kwargs)

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

	def create(self):
		self._createComponent()
		self._writeRigComponentInfo()

	def connect(self, matrixPlug):
		inputMatrixList = cmds.getAttr(matrixPlug)
		componentMatrixList = cmds.getAttr('{}.worldMatrix[0]'.format(self._rigComponent))

		MMatrixComponent = apiUtils.convertListToMMatrix(componentMatrixList)
		MMatrixInput = apiUtils.convertListToMMatrix(inputMatrixList)

		offsetMatrixList = apiUtils.convertMMatrixToList(MMatrixComponent * MMatrixInput.inverse())

		attributes.connectAttrs(matrixPlug, self._inputMatrixPlug, force = True)
		attributes.setAttrs(self._offsetMatrixPlug, offsetMatrixList, type = 'matrix', force = True)

	def _registerAttrs(self, kwargs):
		self._registerDefaultKwargs()
		self._registerAttributes()
		self._registerInput(kwargs)
		self._removeAttributes()
		self._setVariables()

	def _registerDefaultKwargs(self):
		kwargs = {'side': {'value': 'middle', 
						   'type' : basestring},
				  'part': {'value': '',
						   'type': basestring},
				  'index': {'value': None,
						    'type': int},
				  'parent': {'value': '',
							 'type': basestring},
				  'stacks': {'value': 3,
							 'type': int},
							}

		# add resolution tag
		res = naming.getKeys('resolution', returnType = 'longName')
		kwargs.update('resolution': {'value': res, 'type': list})

		self._kwargs.update(kwargs)

	def _setVariables(self):
		self._rigComponentType = 'rigSys.core.rigComponent'
		self._kwargs = {}
		self._kwargsRemove = []
		self._controls = []
		self._suffix = ''

	def _createComponent(self):
		'''
		create rig component hierarchy

		rigComponent
		  -- controlsGrp
		  -- rigLocal	
			-- jointsGrp
			-- nodesLocalGrp
		  -- rigWorld
			-- nodesHideGrp
			-- nodesShowGrp
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
		attrDict = {}
		for grp in ['rigComponent', 'controlsGrp', 'rigLocal', 'nodesLocalGrp',
					'rigWorld', 'nodesHideGrp', 'nodesShowGrp', 'subComponents']:
			NamingGrp.type = grp
			transformNode = transforms.createTransformNode(NamingGrp.name, 
														   lockHide = ['tx', 'ty', 'tz',
																	  'rx', 'ry', 'rz',
																	  'sx', 'sy', 'sz',
																	  'v'])
			attrDict.update({'_{}'.format(grp): transformNode})

		self._addAttributeFromDict(attrDict)

		# parent components
		cmds.parent(self._rigComponent, self._parent)
		cmds.parent([self._controlsGrp, self._rigLocal, self._rigWorld, self._subComponents], self._rigComponent)
		cmds.parent(self._nodesLocalGrp, self._rigLocal)
		cmds.parent([self._nodesHideGrp, self._nodesShowGrp], self._rigWorld)

		# inheritsTransform
		attributes.setAttrs(['{}.inheritsTransform'.format(self._rigLocal),
							 '{}.inheritsTransform'.format(self._rigWorld)],
							 0, force = True)

		# hide nodesHide
		attributes.setAttrs('{}.v'.format(self._nodesHideGrp), 0, force = True)

		# input matrix, offset matrix, component type, controls, rigNodes
		attributes.addAttrs(self._rigComponent, ['inputMatrix', 'offsetMatrix', 'outputMatrix', 'outputInverseMatrix'], 
							attributeType = 'matrix', lock = True)
		
		attributes.addAttrs(self._rigComponent, ['controlsVis', 'rigNodesVis', 'subComponents'],
							attributeType = 'long', minValue = 0, maxValue = 1, 
							defaultValue = [1,0,0], keyable = False, channelBox = True)

		# connect attrs
		attributes.connectAttrs(['controlsVis', 'rigNodesVis', 'rigNodesVis', 'subComponents'], 
								['{}.v'.format(self._controlsGrp), 
								 '{}.v'.format(self._nodesLocalGrp), 
								 '{}.v'.format(self._nodesHideGrp), 
								 '{}.v'.format(self._subComponents)], 
								 driver = self._rigComponent, force=True)

		# connect matrix
		NamingGrp.type = 'multMatrix'
		multMatrixInput = nodeUtils.create(name = NamingGrp.name)

		NamingGrp.type = 'inverseMatrix'
		inverseMatrixInput = nodeUtils.create(name = NamingGrp.name)

		attributes.connectAttrs(['offsetMatrix', 'inputMatrix'], ['matrixIn[0]', 'matrixIn[1]'],
								driver = self._rigComponent, driven = multMatrixInput, force = True)

		attributes.connectAttrs('matrixSum', 'outputMatrix', 
								driver = multMatrixInput, driven = self._rigComponent, force = True)

		attributes.connectAttrs(['{}.matrixSum'.format(multMatrixInput), '{}.outputMatrix'.format(inverseMatrixInput)],
								['{}.inputMatrix'.format(inverseMatrixInput), '{}.outputInverseMatrix'.format(self._rigComponent)],
								force = True)

		constraints.matrixConnect(self._rigComponent, 'outputMatrix', [self._controlsGrp, self._rigLocal], force = True)

		attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'],
								['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'],
								driver = self._controlsGrp, driven = self._rigLocal, force = True)

		# get attrs
		self._inputMatrixPlug = '{}.inputMatrix'.format(self._rigComponent)
		self._offsetMatrixPlug = '{}.offsetMatrix'.format(self._rigComponent)

	def _writeRigComponentInfo(self):
		# rig component type
		self._writeRigComponentType()

		# parent holder matrix
		cmds.addAttr(self._rigComponent, ln = 'parentHolderMatrix', at = 'matrix', lock = True)

		# add resolution tag
		self._addListAsStringAttr('resolution', self._resolution)

		# controls
		self._writeControlsInfo()

	def _registerInput(self, kwargs):
		for key, val in kwargs.iteritems():
			if key in self._kwargs:
				self.__setattr__('_' + key, val)

	def _registerAttributes(self):
		for key, valDict in self._kwargs.iteritems():
			self._addAttributeFromDict({'_' + key: valDict['value']})

	def _removeAttributes(self):
		for key in self._kwargsRemove:
			self._kwargs.pop(key, None)
				
	def _getRigComponentInfo(self):
		# get groups
		NamingGrp = naming.Naming(self._rigComponent)

		self._side = NamingGrp.side
		self._part = NamingGrp.part
		self._index = NamingGrp.index

		attrDict = {}
		for grp in ['controlsGrp', 'rigLocal', 'nodesLocalGrp',
					'rigWorld', 'nodesHideGrp', 'nodesShowGrp', 'subComponents']:
			NamingGrp.type = grp
			attrDict.update({'_{}'.format(grp): NamingGrp.name})

		self._addAttributeFromDict(attrDict)

		self._rigComponentType = self._getStringAttr('_rigComponentType')

		self._inputMatrixPlug = '{}.inputMatrix'.format(self._rigComponent)
		self._offsetMatrixPlug = '{}.offsetMatrix'.format(self._rigComponent)

		self._addObjAttr('parentHolder', {'matrixPlug': '{}.parentHolderMatrix'.format(self._rigComponent)})

		self._getControlsInfo()

	def _getControlsInfo(self):
		controlList = self._getStringAttrAsList('controls')
		if controlList:
			controlObjList = []
			controlDict = {'list': controlList,
						  'count': len(controlList)}

			for i, control in enumerate(controlList):
				if cmds.objectType(control) == 'transform':
					ControlObj = controls.Control(control)
					controlDict.update({control: ControlObj})
				else:
					controlDict.update({control: control})
			self._addObjAttr('controls', controlDict)

	def _writeRigComponentType(self):
		self._addStringAttr('rigComponentType', self._rigComponentType)

	def _writeControlsInfo(self):
		# controls
		self._addListAsStringAttr('controls', self._controls)
		self._getControlsInfo()
		
	def _addAttributeFromList(self, attr, valList):
		if valList:
			attrDict = self._generateAttrDict(attr, valList)
			self._addAttributeFromDict(attrDict)

	def _addAttributeFromDict(self, attrDict):
		for key, value in attrDict.items():
			setattr(self, key, value)

	def _generateAttrDict(self, attr, valList):
		attrDict = {}
		for i, val in enumerate(valList):
			attrDict.update({'%s%03d' %(attr, i): val})
		return attrDict

	def _addObjAttr(self, attr, attrDict):
		attrSplit = attr.split('.')
		attrParent = self
		if len(attrSplit) > 1:
			for a in attrSplit[:-1]:
				attrParent = getattr(attrParent, a)
		setattr(attrParent, attrSplit[-1], Objectview(attrDict))

	def _addListAsStringAttr(self, attr, valList):
		valString = ''
		for val in valList:
			valString += '{},'.format(val)
		if valString:
			valString = valString[:-1]
		self._addStringAttr(attr, valString)

	def _getStringAttrAsList(self, attr):
		attrList = None
		if cmds.attributeQuery(attr, node = self._rigComponent, ex = True):
			val = cmds.getAttr('{}.{}'.format(self._rigComponent, attr))
			if val:
				attrList = val.split(',')
		return attrList
		
	def _addStringAttr(self, attr, val):
		if not cmds.attributeQuery(attr, node = self._rigComponent, ex = True):
			attributes.addAttrs(self._rigComponent, attr, attributeType = 'string', lock = True)
		attributes.setAttrs(attr, val, node = self._rigComponent, type = 'string', force = True)

	def _getStringAttr(self, attr):
		if cmds.attributeQuery(attr, node = self._rigComponent, ex = True):
			val = cmds.getAttr('{}.{}'.format(self._rigComponent, attr))
		else:
			val = None
		return val

class Objectview(object):
	def __init__(self, kwargs):
		self.__dict__ = kwargs

