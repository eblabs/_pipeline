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

class Builder(object):
	"""docstring for Builder"""
	def __init__(self):
		super(Builder, self).__init__()
		
		self._pathBpJnt = []
		self._pathBpGeo = []
		self._pathComponents = []
		self._componentsData = {}

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
		pass

	def run(self):
		for buildDict in [self._preBuild, self._build, self._postBuild]:
			order = buildDict['order']
			for task in order:
				TaskFunc = buildDict['info'][task]
				TaskFunc()

	def _createNewScene(self):
		cmds.file(f = True, new = True)

	def _importBlueprint(self):
		bpGrp = '_blueprint_'
		if not cmds.objExist(bpGrp):
			cmds.group(empty = True, name = bpGrp)
		for path in self._pathBpJnt:
			joints.loadJointsInfo(path, vis=True)
		for path in self._pathBpGeo:
			geometries.loadGeoInfo(path, vis=True)

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

	def _createComponents(self):
		for component, componentInfo in self._componentsData.iteritems():
			componentType = componentInfo['componentType']
			kwargs = componentInfo['kwargs']
			kwargs.update({'parent': self._componentsGrp})
			kwargs.update({'controlSize': 10})
			Limb = componentUtils.createComponent(componentType, kwargs)
			attributes.connectAttrs(['jointsVis', 'controlsVis', 'rigNodesVis', 'localization'],
									['jointsVis', 'controlsVis', 'rigNodesVis', 'localization'],
									driver = self._animationRig,
									driven = Limb._rigComponent)
			self._addAttributeFromDict({component: Limb})

	def _connectComponents(self):
		for component, componentInfo in self._componentsData.iteritems():
			ComponentObj = getattr(self, component)
			matrixPlug = componentInfo['matrixPlug']
			if matrixPlug:
				matrixPlug = matrixPlug.split('.')
				ComponentPlug = getattr(self, matrixPlug[0])
				matrixPlug = componentUtils.getComponentAttr(ComponentPlug, matrixPlug[1:])
				ComponentObj.connect(matrixPlug)
			if 'deformationNodesParent' in componentInfo:
				parentNode = componentInfo['deformationNodesParent']
				if not isinstance(parentNode, list):
					parentNode = [parentNode]
				parentNodeList = []
				for node in parentNode:
					if node:
						node = node.split('.')
						NodeObj = getattr(self, node[0])
						node = componentUtils.getComponentAttr(NodeObj, node[1:])
					parentNodeList.append(node)
				ComponentObj.connectDeformationNodes(parentNodeList)

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
