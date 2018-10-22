# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import builder
# ---- import end ----

class DeformationRig(builder.Builder):
	"""docstring for DeformationRig"""
	def __init__(self):
		super(DeformationRig, self).__init__()
		self._rigType = 'deformationRig'

		self._hierarchyInfo.update({'bindGroup':{'name': naming.Naming(type = 'bindGroup',
																	 side = 'middle',
																	 part = self._rigType).name,
											   'parent': 'master'},
									'bindJoints': {'name': naming.Naming(type = 'bindJoints',
																		 side = 'middle',
																		 part = self._rigType).name,
													  'parent': 'bindGroup'},
									'bindObjectsLocal': {'name': naming.Naming(type = 'bindObjectsLocal',
																			   side = 'middle',
																			   part = self._rigType).name,
														'parent': 'bindGroup'},
									'bindObjectsWorld': {'name': naming.Naming(type = 'bindObjectsWorld',
																			   side = 'middle',
																			   part = self._rigType).name,
														 'parent': 'bindGroup'}})

	def registertion(self):
		super(DeformationRig, self).registertion()

		# prebuild

		self.registerTask({'name': 'Import Model',
						   'task': self._importModel,
						   'section': 'preBuild',
						   'after': 0})

		self.registerTask({'name': 'Import Skeleton',
						   'task': self._importSkeleton,
						   'section': 'preBuild',
						   'after': 1})

		# build

		# postBuild

		self.registerTask({'name': 'Load Hierarchy',
						   'task': self._loadHierarchy,
						   'section': 'postBuild',
						   'after': 0})

		self.registerTask({'name': 'Load Deformers',
						   'task': self._loadDeformers,
						   'section': 'postBuild',
						   'after': 1})

	def _baseHierarchy(self):
		super(DeformationRig, self)._baseHierarchy()

		attributes.addAttrs(self._master, ['bindNodesVis'], attributeType = 'long', minValue = 0, maxValue = 1, 
							defaultValue = 0, keyable = False, channelBox = True)
		attributes.connectAttrs('bindNodesVis', 'v', driver = self._master, driven = self._bindGroup)
		
		cmds.addAttr('{}.controlsComponentVis'.format(self._master), e = True, dv = 0)
		cmds.setAttr('{}.controlsComponentVis'.format(self._master), 0)

		constraints.matrixConnect(self._controlsGrp, 'worldPosMatrix', self._bindObjectsWorld, force = True)
		constraints.matrixConnect(self._controlsGrp, 'localizationMatrix', [self._bindJoints, self._bindObjectsLocal], force = True)



