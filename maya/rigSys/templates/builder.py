# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import lib.common.transforms as transforms
import lib.common.attributes as attributes
import lib.common.hierarchy as hierarchy
import lib.modeling.geometries as geometries
import lib.rigging.joints as joints
# ---- import end ----

# -- import component
import rigSys.components.utils.componentUtils as componentUtils
# ---- import end ----

# -- import assets lib
import assets.lib.rigs as rigs

# -- import file format
import common.files.files as files
fileFormat = files.readJsonFile(files.path_fileFormat)

class Builder(object):
	"""docstring for Builder"""
	def __init__(self, *args, **kwargs):
		super(Builder, self).__init__()
		
		rigData = kwargs.get('rigData', {})

		# build info
		self._rigType = 'animationRig'

		self._hierarchyInfo = {
							   'master': {'name': naming.Naming(type = 'master', 
																side = 'middle', 
																part = self._rigType).name},
							   'controlsGrp': {'name': naming.Naming(type = 'controlsGroup', 
						 									  		 side = 'middle', 
						 									  		 part = self._rigType).name,
						 					   'parent': 'master'},
						 	   'skeletonGrp': {'name': naming.Naming(type = 'skeletonGroup', 
						 									  		 side = 'middle', 
						 									  		 part = self._rigType).name,
						 					   'parent': 'master'},
							   'componentsGrp': {'name': naming.Naming(type = 'componentsGrp', 
																	   side = 'middle', 
																	   part = self._rigType).name,
												 'parent': 'master'},
							   'rigNodesGrp': {'name': naming.Naming(type = 'rigNodesGrp', 
																	 side = 'middle', 
																	 part = self._rigType).name,
											   'parent': 'master',
											   'vis': False},
							   'rigLocal': {'name': naming.Naming(type = 'rigLocal', 
																  side = 'middle', 
																  part = self._rigType).name,
											'parent': 'rigNodesGrp'},
							   'rigWorld': {'name': naming.Naming(type = 'rigWorld', 
																  side = 'middle', 
																  part = self._rigType).name,
											'parent': 'rigNodesGrp'}}

		self._rigData = self._getRigDataPath(rigData)
		self._componentsData = self._composeRigData(self._rigData['components'])
		#self._controlsData = self._composeRigData(self._rigData['controlShape'])

		# preBuild, build, postBuild
		self._preBuild = {'order': [],
						  'info': {}}
		self._build = {'order': [],
					   'info': {}}
		self._postBuild = {'order': [],
						   'info': {}}

	def registerTask(self, taskInfo):
		'''
		taskInfo template

		'name'
		'task'
		'after'
		'section'
		'''
		# get section
		section = taskInfo['section']
		if section == 'preBuild':
			taskDict = self._preBuild
		elif section == 'build':
			taskDict = self._build
		else:
			taskDict = self._postBuild

		# get index
		index = None
		if 'after' in taskInfo:
			after = taskInfo['after']
			if isinstance(after, int):
				index = after + 1
				if index > len(taskDict['order']):
					index = None
			elif isinstance(after, basestring):
				if after in taskDict['order']:
					index = taskDict['order'].index(after) + 1

		# add to section
		if index == None:
			taskDict['order'].append(taskInfo['name'])
			taskDict['info'].update({taskInfo['name']: taskInfo['task']})
		else:
			taskDict['order'].insert(index, taskInfo['name'])
			taskDict['info'].update({taskInfo['name']: taskInfo['task']})

	def registertion(self):
		# prebuild
		self.registerTask({'name': 'Create New Scene',
						   'task': self._createNewScene,
						   'section': 'preBuild'})

		self.registerTask({'name': 'Import Misc',
						   'task': self._importMisc,
						   'section': 'preBuild'})

		self.registerTask({'name': 'Base Hierarchy',
						   'task': self._baseHierarchy,
						   'section': 'preBuild'})

		# build

		self.registerTask({'name': 'Create Components',
						   'task': self._createComponents,
						   'section': 'build'})

		self.registerTask({'name': 'Connect Components',
						   'task': self._connectComponents,
						   'section': 'build'})

		self.registerTask({'name': 'Space Switch',
						   'task': self._spaceSwitch,
						   'section': 'build'})

		# self.registerTask({'name': 'Set Default Attributes',
		# 				   'task': self._setDefaultAttributes,
		# 				   'section': 'build'})

		# postBuild

		# self.registerTask({'name': 'Load ControlShapes',
		# 				   'task': self._loadControlShapes,
		# 				   'section': 'postBuild'})

		# self.registerTask({'name': 'Hide History',
		# 				   'task': self._hideHistory,
		# 				   'section': 'postBuild'})

	def run(self):
		for buildDict in [self._preBuild, self._build, self._postBuild]:
			order = buildDict['order']
			for task in order:
				logger.info('Task: {} build start'.format(task))
				TaskFunc = buildDict['info'][task]
				TaskFunc()
				logger.info('Task: {} build end'.format(task))

	def _createNewScene(self):
		cmds.file(f = True, new = True)

	def _importMisc(self):
		pathMiscs = self._rigData['miscs']
		for pathM in pathMiscs:
			try:
				cmds.file(pathM, i = True)
				logger.info('Import misc file: {} successfully'.format(pathM))
			except:
				logger.info('Can not import misc file: {}, skipped'.format(pathM))

	def _buildGroupHierarchy(self, hierarchyInfo):
		attrDict = {}
		for key in hierarchyInfo:
			transformNode = transforms.createTransformNode(hierarchyInfo[key]['name'], 
														   lockHide = ['tx', 'ty', 'tz',
																	  'rx', 'ry', 'rz',
																	  'sx', 'sy', 'sz',
																	  'v'])
			attrDict.update({'_{}'.format(key): transformNode})

		self._addAttributeFromDict(attrDict)

		# parent hierarchy
		for key in hierarchyInfo:
			if 'parent' in hierarchyInfo[key]:
				parentKey = hierarchyInfo[key]['parent']
				hierarchy.parent(hierarchyInfo[key]['name'], hierarchyInfo[parentKey]['name'])
			if 'vis' in hierarchyInfo[key]:
				vis = hierarchyInfo[key]['vis']
				attributes.setAttrs('{}.v'.format(hierarchyInfo[key]['name']), vis, force = True)

	def _baseHierarchy(self):
		self._buildGroupHierarchy(self._hierarchyInfo)

		# vis attrs
		attributes.addAttrs(self._master, ['jointsVis', 'controlsVis', 'rigNodesVis', 'skeletonVis', 'localization'], attributeType = 'long', minValue = 0, maxValue = 1, 
							defaultValue = [0, 1, 0, 0, 1], keyable = False, channelBox = True)
		attributes.addAttrs(self._master, ['controlsRigVis', 'controlsComponentVis'], attributeType = 'long', minValue = 0, maxValue = 1, 
							defaultValue = [1, 1], keyable = False, channelBox = False)
		attrPlugs = []
		for attr in ['controlsRigVis', 'controlsComponentVis']:
			multNode = nodeUtils.create(type = 'multDoubleLinear', side = 'middle', part = attr)
			attributes.connectAttrs(['{}.controlsVis'.format(self._master), '{}.{}'.format(multNode, attr)],
									['input1', 'input2'], driven = multNode)
			attrPlugs.append('{}.output'.format(multNode))
		self._controlsRigVisPlug = attrPlugs[0]
		self._controlsComponentVisPlug = attrPlugs[1]
		attributes.connectAttrs('rigNodesVis', 'v', driver = self._master, driven = self._rigNodesGrp)
		attributes.connectAttrs(self._controlsRigVisPlug, 'v', driven = self._controlsGrp)

		cmds.addAttr(self._controlsGrp, ln = 'worldPosMatrix', at = 'matrix')
		cmds.addAttr(self._controlsGrp, ln = 'localizationMatrix', at = 'matrix')
		self.worldPosMatrixPlug = '{}.worldPosMatrix'.format(self._controlsGrp)

		# localization matrix
		localizationPlug = attributes.addRvsAttr(self._master, 'localization')
		matrixLocalization = nodeUtils.create(type = 'wtAddMatrix', side = 'middle', part = '{}LocalizationMatrix'.format(self._rigType))
		attributes.connectAttrs(['{}.localization'.format(self._master), '{}.worldPosMatrix'.format(self._controlsGrp), localizationPlug],
								['wtMatrix[0].weightIn', 'wtMatrix[1].matrixIn', 'wtMatrix[1].weightIn'], driven = matrixLocalization)
		matrixList = cmds.getAttr('{}.outputMatrix'.format(self._master))
		cmds.setAttr('{}.wtMatrix[0].matrixIn'.format(matrixLocalization), matrixList, type = 'matrix', lock = True)
		attributes.connectAttrs('{}.matrixSum'.format(matrixLocalization), '{}.localizationMatrix'.format(self._controlsGrp))

		constraints.matrixConnect(self._controlsGrp, 'worldPosMatrix', self._componentsGrp, force = True)
		constraints.matrixConnect(self._controlsGrp, 'localizationMatrix', [self._rigLocal, self._skeletonGrp], force = True)

	def _createComponents(self):
		for component, componentInfo in self._componentsData.iteritems():
			componentType = componentInfo['componentType']
			kwargs = componentInfo['kwargs']
			kwargs.update({'parent': self._componentsGrp})
			kwargs.update({'controlSize': 10})
			Limb = componentUtils.createComponent(componentType, kwargs)
			attributes.connectAttrs(['jointsVis', 'rigNodesVis', 'localization'],
									['jointsVis', 'rigNodesVis', 'localization'],
									driver = self._animationRig,
									driven = Limb._rigComponent)
			cmds.connectAttr(self._controlsComponentVisPlug, '{}.controlsVis'.format(Limb._rigComponent))
			self._addAttributeFromDict({component: Limb})

	def _connectComponents(self):
		for component, componentInfo in self._componentsData.iteritems():
			ComponentObj = getattr(self, component)
			ConnectObj = componentInfo['connect']
			if ConnectObj:
				ConnectObj = ConnectObj.split('.')
				ComponentPlug = getattr(self, ConnectObj[0])
				ConnectObj = componentUtils.getComponentAttr(ComponentPlug, ConnectObj[1:])
				ComponentObj.connect(ConnectObj, skeletonParent = self._skeletonGrp)

	def _spaceSwitch(self):
		for component, componentInfo in self._componentsData.iteritems():
			if 'space' in componentInfo:
				ComponentObj = getattr(self, component)
				for key, spaceInfo in componentInfo['space'].iteritems():
					key = key.split('.')
					ctrl = componentUtils.getComponentAttr(self, key)
					# replace matrixPlug
					for space in spaceInfo:
						matrixPlug = spaceInfo[space]['matrixPlug']
						matrixPlug = matrixPlug.split('.')
						matrixPlug = componentUtils.getComponentAttr(self, matrixPlug)
						spaceInfo[space]['matrixPlug'] = matrixPlug
					# add space
					ComponentObj.addSpace(ctrl, spaceInfo)

	def _addAttributeFromDict(self, attrDict):
		for key, value in attrDict.items():
			setattr(self, key, value)

	def _getRigDataPath(self, rigData):
		# in the ui, each data component should return as follow
		# key: etc blueprints
		# dataKey: in case have multi data import from multi places
		#          will be rigData001.... in order
		# project: (None will look for current project)
		# asset: (None will look for current)
		# rigSet: (None will look for current)
		# files: (list of file, empty will go over each files)
		# fileType: (list of file type, empty will go over each files)
		# mode: (publish/wip/version)
		# version: (None will look for the latest)

		dataPathDict = {}

		for key, data in rigData.iteritems():
			keyEachList = data.keys()
			keyEachList.sort()
			pathDataList = []
			for keyEach in keyEachList:
				#getDataPath(data, rigSet, asset, project, files=[], fileType=[], mode='publish', version=0):	
				dataEach = data[keyEach]
				getDataPathDict = {'files': dataEach['files'],
								   'fileType': dataEach['fileType'],
								   'mode': dataEach['mode'],
								   'version': dataEach['version']}
				pathDataEach = rigs.getDataPath(key, dataEach['rigSet'], dataEach['asset'], dataEach['project'], **getDataPathDict)
				pathDataList += pathDataEach
			dataPathDict.update({key: pathDataList})

		self._rigData = dataPathDict

	def _composeRigData(self, pathRigData):
		dataDict = {}
		fileFormatJson = [fileFormat['control'], fileFormat['joint']]
		fileFormatPickle = [fileFormat['geometry']]
		for p in pathRigData:
			fileName, fileExtension = os.path.splitext(p)
			fileExtension = fileExtension[1:] # remove '.'

			if fileExtension in fileFormatJson:
				dataEach = files.readJsonFile(p)
			elif fileExtension in fileFormatPickle:
				dataEach = files.readPickleFile(p)
			else:
				dataEach = {}

			if dataEach:
				for key, item in dataEach.iteritems():
					if key not in dataDict:
						dataDict.update({key: item})
		return dataDict
