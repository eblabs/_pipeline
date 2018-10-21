# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import lib.common.files.files as files
import lib.common.naming.naming as naming
import lib.common.transforms as transforms
import lib.common.attributes as attributes
import lib.common.apiUtils as apiUtils
import lib.common.nodeUtils as nodeUtils
import lib.common.hierarchy as hierarchy
import lib.rigging.joints as joints
import lib.rigging.constraints as constraints
import lib.rigging.controls.controls as controls
# ---- import end ----

# -- import component
from rigSys.components.core import path_spaceDict
# ---- import end ----

class RigComponent(object):
	"""rigComponent template"""

	def __init__(self, *args,**kwargs):

		# default attrs
		self._kwargs = {}
		self._kwargsRemove = []
		self._controls = []
		self._suffix = ''

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

	def connect(self, inputObj, **kwargs):
		matrixPlug = inputObj.localMatrixPlug
		inputMatrixList = cmds.getAttr(matrixPlug)
		componentMatrixList = cmds.getAttr('{}.worldMatrix[0]'.format(self._rigComponent))

		MMatrixComponent = apiUtils.convertListToMMatrix(componentMatrixList)
		MMatrixInput = apiUtils.convertListToMMatrix(inputMatrixList)

		offsetMatrixList = apiUtils.convertMMatrixToList(MMatrixComponent * MMatrixInput.inverse())

		attributes.connectAttrs(matrixPlug, self._inputMatrixPlug, force = True)
		attributes.setAttrs(self._offsetMatrixPlug, offsetMatrixList, type = 'matrix', force = True)

	def addSpace(self, ctrl, spaceDict):
		# space dict template
		# {'chest': {'matrixPlug': matrixPlug,
		#			 'spaces': ['pos', 'scale']},
		#  'pelvis':}
		spaceKeys = files.readJsonFile(path_spaceDict)
		Control = controls.Control(ctrl)

		indexList = []
		indexCustom = 100
		keyIndexDict = {}

		spaceChannelInfo = {'pos': {'channel': [True, True, False],
									'attr': False,
									'enumName': '',
									'defaultA': 0,
									'defaultB': 0,
									'spaces': {}},
							'point': {'channel': [True, False, False],
									'attr': False,
									'enumName': '',
									'defaultA': 0,
									'defaultB': 0,
									'spaces': {}},
							'orient': {'channel': [False, True, False],
									'attr': False,
									'enumName': '',
									'defaultA': 0,
									'defaultB': 0,
									'spaces': {}},
							'scale': {'channel': [False, False, True],
									'attr': False,
									'enumName': '',
									'defaultA': 0,
									'defaultB': 0,
									'spaces': {}}}

		# query ctrl's space attr
		addPosAttrCheck = False

		indexCustomList = []
		for key in spaceChannelInfo:
			check = cmds.attributeQuery('space{}A'.format(key.title()), node = ctrl, ex = True)
			if check:
				defaultA = cmds.addAttr('{}.space{}A'.format(ctrl, key.title()), q = True, dv = True)
				defaultB = cmds.addAttr('{}.space{}B'.format(ctrl, key.title()), q = True, dv = True)				
				enumName = cmds.addAttr('{}.space{}A'.format(ctrl, key.title()), q = True, en = True)
				enumList = enumName.split(':')

				itemIndex = -1

				for item in enumList:
					if '=' in item:
						attr = item.split('=')[0]
						index = int(item.split('=')[-1])
					else:
						attr = item
						index = itemIndex + 1
					itemIndex = index
					keyIndexDict.update({attr: index})
					indexCustomList.append(index)
				spaceChannelInfo[key]['attr'] = True
				spaceChannelInfo[key]['enumName'] = enumName + ':'
				spaceChannelInfo[key]['defaultA'] = defaultA
				spaceChannelInfo[key]['defaultB'] = defaultB

		if indexCustomList:
			maxIndex = max(indexCustomList)
			if maxIndex >= indexCustom:
				indexCustom = maxIndex + 1

		if not spaceChannelInfo['point']['attr'] and not spaceChannelInfo['orient']['attr']:
			addPosAttrCheck = True

		# re organize dictionary
		for space, spaceInfo in spaceDict.iteritems():
			spaceList = spaceInfo['spaces']
			spaceAddKeys = []
			if 'pos' in spaceList and addPosAttrCheck:
				spaceAddKeys.append('pos')
			else:
				if 'point' in spaceList:
					spaceAddKeys.append('point')
				if 'orient' in spaceList:
					spaceAddKeys.append('orient')
			if 'scale' in spaceList:
				spaceAddKeys.append('scale')

			if 'defaultA' in spaceInfo:
				for key in spaceInfo['defaultA']:
					spaceChannelInfo[key]['defaultA'] = space
			if 'defaultB' in spaceInfo:
				for key in spaceInfo['defaultB']:
					spaceChannelInfo[key]['defaultB'] = space

			for key in spaceAddKeys:
				spaceChannelInfo[key]['spaces'].update({space: spaceInfo['matrixPlug']})

		# do each space blend
		for spaceType in ['pos', 'point', 'orient', 'scale']:
			spaceInfo = spaceChannelInfo[spaceType]['spaces']
			if spaceInfo:
				# has key for this space type blend
				enumName = spaceChannelInfo[spaceType]['enumName']
				# get choice node, skip automatically if exist
				choiceA = nodeUtils.create(type = 'choice', side = Control.side, 
							part = '{}Space{}A'.format(Control.part, spaceType.title()), index = Control.index)
				choiceB = nodeUtils.create(type = 'choice', side = Control.side, 
							part = '{}Space{}B'.format(Control.part, spaceType.title()), index = Control.index)

				for key in spaceInfo:
					if key not in enumName:
						# make sure the space not exist
						# get index
						if key in keyIndexDict:
							index = keyIndexDict[key]
						elif key in spaceKeys:
							index = spaceKeys[key]
							keyIndexDict.update({key: index})
						else:
							index = indexCustom
							keyIndexDict.update({key: index})
							indexCustom += 1
						enumName += '{}={}:'.format(key, index)
						
						matrixPlug = spaceInfo[key]
						nodePlug = matrixPlug.split('.')[0]
						attrPlug = matrixPlug.replace(nodePlug + '.', '')
						
						# get multMatrix node, skip creation if exist
						multMatrix = naming.Naming(type = 'multMatrix', side = Control.side,
									part = '{}Space{}'.format(Control.part, index), index = Control.index).name
						if not cmds.objExists(multMatrix):
							multMatrix = nodeUtils.create(name = multMatrix)
							matrixLocal = transforms.getLocalMatrix(Control.space, nodePlug, parentMatrix = attrPlug)
							cmds.setAttr('{}.matrixIn[0]'.format(multMatrix), matrixLocal, type = 'matrix')
							cmds.connectAttr(matrixPlug, '{}.matrixIn[1]'.format(multMatrix))
						# connect multMatrix with choice
						cmds.connectAttr('{}.matrixSum'.format(multMatrix), '{}.input[{}]'.format(choiceA, index))
						cmds.connectAttr('{}.matrixSum'.format(multMatrix), '{}.input[{}]'.format(choiceB, index))

				# get default value
				defaultA = spaceChannelInfo[spaceType]['defaultA']
				defaultB = spaceChannelInfo[spaceType]['defaultB']

				if isinstance(defaultA, basestring):
					defaultA = keyIndexDict[defaultA]
				if isinstance(defaultB, basestring):
					defaultB = keyIndexDict[defaultB]

				if defaultA == 0:
					# no given default val, pick one randomly
					defaultA = keyIndexDict[spaceInfo.keys()[0]]
				if defaultB == 0:
					defaultB = keyIndexDict[spaceInfo.keys()[0]]

				# add attr or edit attr
				if not spaceChannelInfo[spaceType]['attr']:
					attributes.addDivider(ctrl, 'space')
					attributes.addAttrs(ctrl, ['space{}A'.format(spaceType.title()), 'space{}B'.format(spaceType.title())],
										attributeType = 'enum', keyable = True, channelBox = True, enumName = enumName[:-1])
					cmds.addAttr('{}.space{}A'.format(ctrl, spaceType.title()), e = True, dv = defaultA)
					cmds.addAttr('{}.space{}B'.format(ctrl, spaceType.title()), e = True, dv = defaultB)
					attributes.setAttrs(['{}.space{}A'.format(ctrl, spaceType.title()), '{}.space{}B'.format(ctrl, spaceType.title())],
										[defaultA, defaultB])
					cmds.addAttr(ctrl, ln = 'space{}Blend'.format(spaceType.title()), at = 'float', min = 0, max = 10, keyable = True)
					multBlend = nodeUtils.create(type = 'multDoubleLinear',
											 side = Control.side, 
											 part = '{}Space{}Blend'.format(Control.part, spaceType.title()),
											 index = Control.index)
					cmds.connectAttr('{}.space{}Blend'.format(ctrl, spaceType.title()), '{}.input1'.format(multBlend))
					cmds.setAttr('{}.input2'.format(multBlend), 0.1)
					rvsBlend = nodeUtils.create(type = 'reverse',
											 side = Control.side, 
											 part = '{}Space{}Blend'.format(Control.part, spaceType.title()),
											 index = Control.index)
					cmds.connectAttr('{}.output'.format(multBlend), '{}.inputX'.format(rvsBlend))
					cmds.connectAttr('{}.space{}A'.format(ctrl, spaceType.title()), '{}.selector'.format(choiceA))
					cmds.connectAttr('{}.space{}B'.format(ctrl, spaceType.title()), '{}.selector'.format(choiceB))
					constraints.constraintBlend(['{}.output'.format(choiceA), '{}.output'.format(choiceB)], Control.space, 
						weightList = ['{}.outputX'.format(rvsBlend), '{}.output'.format(multBlend)], 
						translate = spaceChannelInfo[spaceType]['channel'][0], rotate = spaceChannelInfo[spaceType]['channel'][1], 
						scale = spaceChannelInfo[spaceType]['channel'][2], parentInverseMatrix = '{}.worldInverseMatrix[0]'.format(Control.passer))
				else:
					cmds.addAttr('{}.space{}A'.format(ctrl, spaceType.title()), e = True, en = enumName[:-1])
					cmds.addAttr('{}.space{}B'.format(ctrl, spaceType.title()), e = True, en = enumName[:-1])
					cmds.addAttr('{}.space{}A'.format(ctrl, spaceType.title()), e = True, dv = defaultA)
					cmds.addAttr('{}.space{}B'.format(ctrl, spaceType.title()), e = True, dv = defaultB)
					attributes.setAttrs(['{}.space{}A'.format(ctrl, spaceType.title()), '{}.space{}B'.format(ctrl, spaceType.title())],
										[defaultA, defaultB])

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
				  'controlSize': {'value': 1,
				  				  'type': float}
							}

		# add resolution tag
		res = naming.getKeys('resolution', returnType = 'longName')
		kwargs.update({'resolution': {'value': res, 'type': list}})

		self._kwargs.update(kwargs)

	def _setVariables(self):
		self._rigComponentType = 'rigSys.components.core.rigComponent'

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
		hierarchy.parent(self._rigComponent, self._parent)
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
		attributes.addAttrs(self._rigComponent, ['inputMatrix', 'offsetMatrix', 'outputMatrix', 
												 'outputInverseMatrix', 'localizationMatrix',
												 'localizationMatrixRvs'], 
							attributeType = 'matrix', lock = True)
		
		attributes.addAttrs(self._rigComponent, ['controlsVis', 'rigNodesVis', 'subComponents', 'localization'],
							attributeType = 'long', minValue = 0, maxValue = 1, 
							defaultValue = [1,0,0,1], keyable = False, channelBox = True)

		localizationPlug = attributes.addRvsAttr(self._rigComponent, 'localization')

		# connect attrs
		attributes.connectAttrs(['controlsVis', 'rigNodesVis', 'rigNodesVis', 'subComponents'], 
								['{}.v'.format(self._controlsGrp), 
								 '{}.v'.format(self._nodesLocalGrp), 
								 '{}.v'.format(self._nodesHideGrp), 
								 '{}.v'.format(self._subComponents)], 
								 driver = self._rigComponent, force=True)
		cmds.connectAttr(localizationPlug, '{}.inheritsTransform'.format(self._rigLocal))

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

		# localization matrix
		matrixLocalization = nodeUtils.create(type = 'wtAddMatrix', side = self._side, part = self._part + 'LocalizationMatrix', index = self._index)
		attributes.connectAttrs(['{}.localization'.format(self._rigComponent), '{}.worldInverseMatrix[0]'.format(self._rigComponent), localizationPlug],
								['wtMatrix[0].weightIn', 'wtMatrix[1].matrixIn', 'wtMatrix[1].weightIn'], driven = matrixLocalization)
		matrixList = cmds.getAttr('{}.outputMatrix'.format(self._rigComponent))
		cmds.setAttr('{}.wtMatrix[0].matrixIn'.format(matrixLocalization), matrixList, type = 'matrix', lock = True)
		attributes.connectAttrs('{}.matrixSum'.format(matrixLocalization), '{}.localizationMatrix'.format(self._rigComponent))

		matrixLocalizationRvs = nodeUtils.create(type = 'wtAddMatrix', side = self._side, part = self._part + 'localizationMatrixRvs', index = self._index)
		attributes.connectAttrs(['{}.localization'.format(self._rigComponent), '{}.worldMatrix[0]'.format(self._rigComponent), localizationPlug],
								['wtMatrix[0].weightIn', 'wtMatrix[0].matrixIn', 'wtMatrix[1].weightIn'], driven = matrixLocalizationRvs)
		cmds.setAttr('{}.wtMatrix[1].matrixIn'.format(matrixLocalizationRvs), matrixList, type = 'matrix', lock = True)
		attributes.connectAttrs('{}.matrixSum'.format(matrixLocalizationRvs), '{}.localizationMatrixRvs'.format(self._rigComponent))

		# get attrs
		self._inputMatrixPlug = '{}.inputMatrix'.format(self._rigComponent)
		self._offsetMatrixPlug = '{}.offsetMatrix'.format(self._rigComponent)
		self._localizationMatrixPlug = '{}.localizationMatrix'.format(self._rigComponent)
		self._localizationMatrixRvsPlug = '{}.localizationMatrixRvs'.format(self._rigComponent)

	def _writeRigComponentInfo(self):
		# rig component type
		self._writeRigComponentType()

		# parent holder matrix
		cmds.addAttr(self._rigComponent, ln = 'parentHolderMatrix', at = 'matrix')
		cmds.setAttr('{}.parentHolderMatrix'.format(self._rigComponent), lock = True)

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
		self._localizationMatrixPlug = '{}.localizationMatrix'.format(self._rigComponentType)
		self._localizationMatrixRvsPlug = '{}.localizationMatrixRvs'.format(self._rigComponentType)

		self._addObjAttr('parentHolder', {'matrixPlug': '{}.parentHolderMatrix'.format(self._rigComponent)})

		self._getControlsInfo()

	def _getControlsInfo(self):
		controlList = self._getStringAttrAsList('controls')
		if controlList:
			controlObjList = []
			controlDict = {'list': controlList,
						  'count': len(controlList)}
			self._addObjAttr('controls', controlDict)

			for i, control in enumerate(controlList):
				controlInfoDict = {'name': control}
				if cmds.objectType(control) == 'transform':
					ControlObj = controls.Control(control)
					controlInfoDict.update({'object': ControlObj})
				self._addObjAttr('controls.control{:03d}'.format(i), controlInfoDict)

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

