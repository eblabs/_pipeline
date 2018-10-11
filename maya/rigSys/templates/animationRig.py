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

class AnimationRig(builder.Builder):
	"""docstring for AnimationRig"""
	def __init__(self, arg):
		super(AnimationRig, self).__init__()
		self.arg = arg

	def registertion(self):
		super(AnimationRig, self).registertion()

		# prebuild
		self.registerTask({'name': 'Create New Scene',
						   'task': self._createNewScene,
						   'section': 'preBuild'})

		self.registerTask({'name': 'Import Blueprint',
						   'task': self._importBlueprint,
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

		self.registerTask({'name': 'Set Default Attributes',
						   'task': self._setDefaultAttributes,
						   'section': 'build'})

		# postBuild

		self.registerTask({'name': 'Load ControlShapes',
						   'task': self._loadControlShapes,
						   'section': 'postBuild'})

		self.registerTask({'name': 'Hide History',
						   'task': self._hideHistory,
						   'section': 'postBuild'})


