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
	def __init__(self, arg):
		super(DeformationRig, self).__init__()
		self.arg = arg

	def registertion(self):
		super(DeformationRig, self).registertion()

		# prebuild

		self.registerTask({'name': 'Create New Scene',
						   'task': self._createNewScene,
						   'section': 'preBuild'})

		self.registerTask({'name': 'Import Model',
						   'task': self._importModel,
						   'section': 'preBuild'})

		self.registerTask({'name': 'Import Skeleton',
						   'task': self._importSkeleton,
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

		self.registerTask({'name': 'Set Default Attributes',
						   'task': self._setDefaultAttributes,
						   'section': 'build'})

		# postBuild

		self.registerTask({'name': 'Load Hierarchy',
						   'task': self._loadHierarchy,
						   'section': 'postBuild'})

		self.registerTask({'name': 'Load Deformers',
						   'task': self._loadDeformers,
						   'section': 'postBuild'})

		self.registerTask({'name': 'Hide History',
						   'task': self._hideHistory,
						   'section': 'postBuild'})


